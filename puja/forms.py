from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (CustomUser, VolunteerTeam, Donation, Expense, VolunteerDuty, 
                     Attendance, PujaEvent, Vendor, Quotation, VendorPayment, 
                     InventoryItem, StockTransaction, PrasadPlanner, Announcement, 
                     GalleryAlbum, GalleryMedia)

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'mobile')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'mobile', 'team')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ('donor_name', 'donor_mobile', 'house_number', 'amount', 'payment_method', 'transaction_id', 'is_anonymous', 'receipt_file', 'material_description')
        widgets = {
            'donor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Donor Name / Owner Name'}),
            'donor_mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Donor Mobile'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. House No. 42 / Lane 3 (Optional)'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in Rs. (Optional for material donations)'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction ID (Optional)'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receipt_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'capture': 'environment'}),
            'material_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50kg Rice, 20kg Potato (For In-Kind donations)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].required = False
        self.fields['house_number'].required = False
        self.fields['material_description'].required = False

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('category', 'description', 'amount', 'date_incurred', 'bill_file')
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Expense details'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in Rs.'}),
            'date_incurred': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bill_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'capture': 'environment'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].required = False
        self.fields['description'].required = False
        self.fields['category'].required = False

class VolunteerTeamForm(forms.ModelForm):
    class Meta:
        model = VolunteerTeam
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Team Name (e.g. Catering)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe team responsibilities'}),
        }

class DutyAssignmentForm(forms.ModelForm):
    class Meta:
        model = VolunteerDuty
        fields = ('volunteer', 'duty_name', 'description', 'start_time', 'end_time', 'status')
        widgets = {
            'volunteer': forms.Select(attrs={'class': 'form-control'}),
            'duty_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Duty Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Duty details'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = PujaEvent
        fields = ('title', 'event_type', 'start_time', 'end_time', 'description', 'location')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ('name', 'category', 'total_quantity', 'vendor')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'total_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Initial Quantity'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
        }

class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ('item', 'transaction_type', 'quantity', 'notes')
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes'}),
        }

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ('name', 'contact_person', 'mobile', 'email', 'address')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor/Business Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person Name'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Vendor Address'}),
        }

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ('vendor', 'item_description', 'amount', 'file')
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'item_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Quote description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quoted Amount in Rs.'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class VendorPaymentForm(forms.ModelForm):
    class Meta:
        model = VendorPayment
        fields = ('vendor', 'amount_paid', 'payment_method', 'notes')
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount Paid in Rs.'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Payment reference / details'}),
        }

class PrasadPlannerForm(forms.ModelForm):
    class Meta:
        model = PrasadPlanner
        fields = ('date', 'expected_people', 'food_items', 'volunteers_assigned')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_people': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Expected Headcount'}),
            'food_items': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Khichdi, Kheer, Boondi'}),
            'volunteers_assigned': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('title', 'message', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write announcement here...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class GalleryAlbumForm(forms.ModelForm):
    class Meta:
        model = GalleryAlbum
        fields = ('title', 'description')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Album Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Album Description (Optional)'}),
        }

class GalleryMediaForm(forms.ModelForm):
    class Meta:
        model = GalleryMedia
        fields = ('album', 'file', 'caption')
        widgets = {
            'album': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Caption (Optional)'}),
        }
