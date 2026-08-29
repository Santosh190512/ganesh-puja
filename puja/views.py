from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from .models import (CustomUser, VolunteerTeam, Donation, Expense, VolunteerDuty, 
                     Attendance, PujaEvent, Vendor, Quotation, VendorPayment, 
                     InventoryItem, StockTransaction, PrasadPlanner, Announcement, 
                     GalleryAlbum, GalleryMedia)
from .forms import (CustomUserCreationForm, UserProfileForm, DonationForm, ExpenseForm, 
                    VolunteerTeamForm, DutyAssignmentForm, EventForm, InventoryItemForm, 
                    StockTransactionForm, VendorForm, QuotationForm, VendorPaymentForm, 
                    PrasadPlannerForm, AnnouncementForm, GalleryAlbumForm, GalleryMediaForm)
from .decorators import role_required, admin_only

# --- AUTHENTICATION VIEWS ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'puja/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'puja/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'puja/profile.html', {'form': form})


# --- DASHBOARD ---

@login_required
def dashboard_view(request):
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    net_budget = total_donations - total_expenses

    pending_tasks_count = VolunteerDuty.objects.filter(status='PENDING').count()
    volunteers_count = CustomUser.objects.filter(role='NORMAL_VOLUNTEER').count()
    upcoming_events = PujaEvent.objects.filter(start_time__gte=timezone.now()).order_by('start_time')[:5]
    announcements = Announcement.objects.all().order_by('-created_at')[:5]

    # Category-wise expenses for chart
    expense_by_category = Expense.objects.values('category').annotate(total=Sum('amount'))
    categories = [dict(Expense.CATEGORIES).get(e['category'], e['category']) for e in expense_by_category]
    expense_totals = [float(e['total']) for e in expense_by_category]

    # Recent Donations
    recent_donations = Donation.objects.all().order_by('-date_received')[:5]

    context = {
        'total_donations': total_donations,
        'total_expenses': total_expenses,
        'net_budget': net_budget,
        'pending_tasks_count': pending_tasks_count,
        'volunteers_count': volunteers_count,
        'upcoming_events': upcoming_events,
        'announcements': announcements,
        'categories': categories,
        'expense_totals': expense_totals,
        'recent_donations': recent_donations,
    }
    return render(request, 'puja/dashboard.html', context)


# --- ANNOUNCEMENTS ---

@login_required
def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'puja/announcement_list.html', {'announcements': announcements})

@login_required
@admin_only
def announcement_add(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.posted_by = request.user
            announcement.save()
            messages.success(request, "Announcement posted successfully!")
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'puja/announcement_form.html', {'form': form})


# --- GALLERY ---

@login_required
def gallery_list(request):
    albums = GalleryAlbum.objects.all().prefetch_related('media_files')
    return render(request, 'puja/gallery_list.html', {'albums': albums})

@login_required
@admin_only
def album_add(request):
    if request.method == 'POST':
        form = GalleryAlbumForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Album created successfully!")
            return redirect('gallery_list')
    else:
        form = GalleryAlbumForm()
    return render(request, 'puja/album_form.html', {'form': form})

@login_required
@admin_only
def media_add(request):
    if request.method == 'POST':
        form = GalleryMediaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Photo/Video uploaded successfully!")
            return redirect('gallery_list')
    else:
        form = GalleryMediaForm()
    return render(request, 'puja/media_form.html', {'form': form})


# --- DONATIONS ---

@login_required
def donation_list(request):
    donations = Donation.objects.all().order_by('-date_received')
    total_amount = donations.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'puja/donation_list.html', {
        'donations': donations,
        'total_amount': total_amount
    })

@login_required
@admin_only
def donation_add(request):
    if request.method == 'POST':
        form = DonationForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.received_by = request.user
            
            # Temporary defaults for database integrity before scanning
            if not donation.amount:
                donation.amount = 0.00
                
            donation.save()

            # Execute OCR if image file is uploaded
            if donation.receipt_file:
                try:
                    from .ocr import scan_donation_image
                    scan_results = scan_donation_image(donation.receipt_file.path)
                    
                    # Fill/override with OCR results if left blank or default
                    if donation.amount == 0.00:
                        donation.amount = scan_results['amount']
                    if not donation.donor_name:
                        donation.donor_name = scan_results['donor_name']
                    if not donation.donor_mobile:
                        donation.donor_mobile = scan_results['donor_mobile']
                    if not donation.transaction_id:
                        donation.transaction_id = scan_results['transaction_id']
                    if donation.payment_method == 'CASH':
                        donation.payment_method = scan_results['payment_method']
                        
                    donation.save()
                    messages.success(request, f"Transaction screen scanned! Auto-filled donation: Rs. {donation.amount} from {donation.donor_name}")
                except Exception as ex:
                    messages.warning(request, f"Screenshot uploaded, but automatic scan failed: {ex}. Please enter details manually.")
            else:
                messages.success(request, f"Donation of Rs. {donation.amount} logged successfully!")
                
            return redirect('donation_list')
    else:
        form = DonationForm()
    return render(request, 'puja/donation_form.html', {'form': form})

@login_required
def donation_receipt(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    return render(request, 'puja/receipt.html', {'donation': donation})


# --- EXPENSES ---

@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date_incurred')
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'puja/expense_list.html', {
        'expenses': expenses,
        'total_amount': total_amount
    })

@login_required
@admin_only
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.logged_by = request.user
            
            # Temporary defaults for database integrity before scanning
            if not expense.amount:
                expense.amount = 0.00
            if not expense.description:
                expense.description = "Scanned bill receipt"
            if not expense.category:
                expense.category = 'OTHER'
                
            expense.save()

            # Execute OCR if image file is uploaded
            if expense.bill_file:
                try:
                    from .ocr import scan_receipt_image
                    scan_results = scan_receipt_image(expense.bill_file.path)
                    
                    # Fill values if they were left blank / default
                    if expense.amount == 0.00:
                        expense.amount = scan_results['amount']
                    if expense.category == 'OTHER':
                        expense.category = scan_results['category']
                    if expense.description == "Scanned bill receipt":
                        expense.description = scan_results['description']
                        
                    expense.save()
                    messages.success(request, f"Receipt scanned! Auto-filled expense: Rs. {expense.amount} ({expense.get_category_display()})")
                except Exception as ex:
                    messages.warning(request, f"Bill uploaded, but automatic scan failed: {ex}. Please enter details manually.")
            else:
                messages.success(request, f"Expense of Rs. {expense.amount} logged successfully!")
                
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'puja/expense_form.html', {'form': form})


# --- VOLUNTEERS ---

@login_required
def volunteer_list(request):
    volunteers = CustomUser.objects.filter(role='NORMAL_VOLUNTEER').select_related('team')
    return render(request, 'puja/volunteer_list.html', {'volunteers': volunteers})

@login_required
def team_list(request):
    teams = VolunteerTeam.objects.all()
    return render(request, 'puja/team_list.html', {'teams': teams})

@login_required
@admin_only
def team_add(request):
    if request.method == 'POST':
        form = VolunteerTeamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Volunteer team created successfully!")
            return redirect('team_list')
    else:
        form = VolunteerTeamForm()
    return render(request, 'puja/team_form.html', {'form': form})

@login_required
@admin_only
def duty_assign(request):
    if request.method == 'POST':
        form = DutyAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Duty assigned successfully!")
            return redirect('volunteer_list')
    else:
        form = DutyAssignmentForm()
    return render(request, 'puja/duty_form.html', {'form': form})

@login_required
def my_duties(request):
    duties = VolunteerDuty.objects.filter(volunteer=request.user).order_by('start_time')
    return render(request, 'puja/my_duties.html', {'duties': duties})

@login_required
def duty_update(request, pk):
    duty = get_object_or_404(VolunteerDuty, pk=pk)
    if request.user.role != 'SUPER_ADMIN' and not request.user.is_superuser and duty.volunteer != request.user:
        messages.error(request, "You are not authorized to update this duty.")
        return redirect('my_duties')
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(VolunteerDuty.STATUS_CHOICES):
            duty.status = status
            duty.save()
            messages.success(request, f"Duty status updated to {status}.")
        return redirect('my_duties' if duty.volunteer == request.user else 'volunteer_list')
    return render(request, 'puja/duty_update.html', {'duty': duty})

@login_required
@admin_only
def attendance_sheet(request):
    volunteers = CustomUser.objects.filter(role='NORMAL_VOLUNTEER')
    today = timezone.localdate()
    existing_attendance = Attendance.objects.filter(date=today).values_list('volunteer_id', flat=True)

    if request.method == 'POST':
        present_list = request.POST.getlist('present_volunteers')
        for v in volunteers:
            is_present = str(v.id) in present_list
            Attendance.objects.update_or_create(
                volunteer=v,
                date=today,
                defaults={'is_present': is_present, 'marked_by': request.user}
            )
        messages.success(request, f"Attendance marked for today ({today}).")
        return redirect('attendance_sheet')

    attendance_data = []
    for v in volunteers:
        is_present = v.id in existing_attendance and Attendance.objects.get(volunteer=v, date=today).is_present
        attendance_data.append({
            'volunteer': v,
            'is_present': is_present
        })

    return render(request, 'puja/attendance.html', {
        'attendance_data': attendance_data,
        'today': today
    })


# --- EVENTS & SCHEDULES ---

@login_required
def event_list(request):
    events = PujaEvent.objects.all().order_by('start_time')
    return render(request, 'puja/event_list.html', {'events': events})

@login_required
@admin_only
def event_add(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event scheduled successfully!")
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'puja/event_form.html', {'form': form})


# --- INVENTORY ---

@login_required
def inventory_list(request):
    items = InventoryItem.objects.all()
    return render(request, 'puja/inventory_list.html', {'items': items})

@login_required
@admin_only
def inventory_add(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.available_quantity = item.total_quantity
            item.save()
            messages.success(request, "Inventory item registered.")
            return redirect('inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'puja/inventory_form.html', {'form': form})

@login_required
@admin_only
def inventory_transaction(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.handled_by = request.user
            item = tx.item

            if tx.transaction_type == 'IN':
                item.total_quantity += tx.quantity
                item.available_quantity += tx.quantity
            elif tx.transaction_type == 'OUT':
                if item.available_quantity >= tx.quantity:
                    item.available_quantity -= tx.quantity
                else:
                    messages.error(request, f"Insufficient available stock of {item.name}.")
                    return render(request, 'puja/transaction_form.html', {'form': form})

            item.save()
            tx.save()
            messages.success(request, "Stock transaction updated successfully!")
            return redirect('inventory_list')
    else:
        form = StockTransactionForm()
    return render(request, 'puja/transaction_form.html', {'form': form})


# --- VENDORS ---

@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    quotations = Quotation.objects.all().select_related('vendor')
    payments = VendorPayment.objects.all().select_related('vendor')
    return render(request, 'puja/vendor_list.html', {
        'vendors': vendors,
        'quotations': quotations,
        'payments': payments
    })

@login_required
@admin_only
def vendor_add(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor details added successfully!")
            return redirect('vendor_list')
    else:
        form = VendorForm()
    return render(request, 'puja/vendor_form.html', {'form': form})

@login_required
@admin_only
def vendor_payment_add(request):
    if request.method == 'POST':
        form = VendorPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            # Deduct paid amount from vendor pending balance
            vendor = payment.vendor
            vendor.pending_amount = max(0, vendor.pending_amount - payment.amount_paid)
            vendor.save()
            messages.success(request, f"Payment of Rs. {payment.amount_paid} recorded for {vendor.name}.")
            return redirect('vendor_list')
    else:
        form = VendorPaymentForm()
    return render(request, 'puja/vendor_payment_form.html', {'form': form})

@login_required
@admin_only
def quotation_add(request):
    if request.method == 'POST':
        form = QuotationForm(request.POST, request.FILES)
        if form.is_valid():
            quote = form.save()
            # If quotes are logged, optionally add to vendor's pending balance once approved
            if quote.status == 'APPROVED':
                vendor = quote.vendor
                vendor.pending_amount += quote.amount
                vendor.save()
            messages.success(request, f"Quotation from {quote.vendor.name} uploaded.")
            return redirect('vendor_list')
    else:
        form = QuotationForm()
    return render(request, 'puja/quotation_form.html', {'form': form})


# --- PRASAD / BHANDARA ---

@login_required
def prasad_list(request):
    planners = PrasadPlanner.objects.all().order_by('-date')
    return render(request, 'puja/prasad_list.html', {'planners': planners})

@login_required
@admin_only
def prasad_add(request):
    if request.method == 'POST':
        form = PrasadPlannerForm(request.POST)
        if form.is_valid():
            planner = form.save(commit=False)
            
            # Simple automatic ingredient quantity calculations based on expected headcount
            headcount = planner.expected_people
            rice_qty = headcount * 0.12  # 120 grams per person
            dal_qty = headcount * 0.05   # 50 grams per person
            vegetable_qty = headcount * 0.1  # 100 grams per person
            oil_qty = headcount * 0.015  # 15ml per person
            
            planner.quantity_calculations = (
                f"Rice: {rice_qty:.2f} kg\n"
                f"Dal: {dal_qty:.2f} kg\n"
                f"Vegetables: {vegetable_qty:.2f} kg\n"
                f"Cooking Oil: {oil_qty:.2f} liters\n"
                f"Salt & Spices: Package estimates based on cook discretion"
            )
            planner.save()
            form.save_m2m()  # Save volunteer assignments
            messages.success(request, "Bhandara prasad plan logged with automated ingredient estimates!")
            return redirect('prasad_list')
    else:
        form = PrasadPlannerForm()
    return render(request, 'puja/prasad_form.html', {'form': form})


# --- REPORTS ---

@login_required
@admin_only
def reports_view(request):
    donations = Donation.objects.all().order_by('-date_received')
    expenses = Expense.objects.all().order_by('-date_incurred')
    
    total_donations = donations.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_donations - total_expenses
    
    vendors = Vendor.objects.filter(pending_amount__gt=0)
    total_vendor_dues = vendors.aggregate(total=Sum('pending_amount'))['total'] or 0
    
    inventory_items = InventoryItem.objects.all()
    volunteers = CustomUser.objects.filter(role='NORMAL_VOLUNTEER')
    
    context = {
        'donations': donations,
        'expenses': expenses,
        'total_donations': total_donations,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'vendors': vendors,
        'total_vendor_dues': total_vendor_dues,
        'inventory_items': inventory_items,
        'volunteers': volunteers,
    }
    return render(request, 'puja/reports.html', context)
