from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class VolunteerTeam(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    SUPER_ADMIN = 'SUPER_ADMIN'
    TREASURER = 'TREASURER'
    VOLUNTEER_COORDINATOR = 'VOLUNTEER_COORDINATOR'
    EVENT_MANAGER = 'EVENT_MANAGER'
    INVENTORY_MANAGER = 'INVENTORY_MANAGER'
    NORMAL_VOLUNTEER = 'NORMAL_VOLUNTEER'

    ROLE_CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (TREASURER, 'Treasurer'),
        (VOLUNTEER_COORDINATOR, 'Volunteer Coordinator'),
        (EVENT_MANAGER, 'Event Manager'),
        (INVENTORY_MANAGER, 'Inventory Manager'),
        (NORMAL_VOLUNTEER, 'Normal Volunteer'),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=NORMAL_VOLUNTEER)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    team = models.ForeignKey(VolunteerTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Donation(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('ONLINE', 'Online'),
    ]
    donor_name = models.CharField(max_length=100, blank=True, null=True)
    donor_mobile = models.CharField(max_length=15, blank=True, null=True)
    house_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="House Number / Address")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CASH')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    date_received = models.DateTimeField(default=timezone.now)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    received_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    receipt_file = models.FileField(upload_to='donations/', blank=True, null=True)
    material_description = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. 50kg Rice, 20kg Potato")

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"REC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        name = "Anonymous" if self.is_anonymous else (self.donor_name or "Unknown")
        return f"{name} - Rs. {self.amount} ({self.receipt_number})"

class Expense(models.Model):
    CATEGORIES = [
        ('PANDAL', 'Pandal'),
        ('GANESH_IDOL', 'Ganesh Idol'),
        ('DECORATION', 'Decoration'),
        ('LIGHTING', 'Lighting'),
        ('SOUND_SYSTEM', 'Sound System'),
        ('PRASAD_FOOD', 'Prasad / Food'),
        ('PUJA_SAMAGRI', 'Puja Samagri'),
        ('SECURITY', 'Security'),
        ('CLEANING', 'Cleaning'),
        ('VISARJAN', 'Visarjan / Immersion'),
        ('OTHER', 'Other'),
    ]
    category = models.CharField(max_length=30, choices=CATEGORIES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_incurred = models.DateField(default=timezone.now)
    bill_file = models.FileField(upload_to='bills/', blank=True, null=True)
    logged_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.get_category_display()} - Rs. {self.amount}"

class VolunteerDuty(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('ABSENT', 'Absent'),
    ]
    volunteer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': CustomUser.NORMAL_VOLUNTEER}, related_name='duties')
    duty_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.volunteer.username} - {self.duty_name} ({self.status})"

class Attendance(models.Model):
    volunteer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')

    class Meta:
        unique_together = ('volunteer', 'date')

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.volunteer.username} - {self.date}: {status}"

class PujaEvent(models.Model):
    EVENT_TYPES = [
        ('STHAPANA', 'Sthapana'),
        ('DAILY_AARTI', 'Daily Aarti'),
        ('BHAJAN_KIRTAN', 'Bhajan / Kirtan'),
        ('CULTURAL_PROGRAM', 'Cultural Program'),
        ('BHANDARA_PRASAD', 'Bhandara / Prasad'),
        ('VISARJAN', 'Visarjan'),
        ('OTHER', 'Other'),
    ]
    title = models.CharField(max_length=100)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, default='Main Pandal')

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Quotation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='quotations')
    item_description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='quotations/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Quote from {self.vendor.name} - Rs. {self.amount}"

class VendorPayment(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('ONLINE', 'Online'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CASH')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment to {self.vendor.name} - Rs. {self.amount_paid}"

class InventoryItem(models.Model):
    CATEGORIES = [
        ('PUJA_SAMAGRI', 'Puja Samagri'),
        ('CHAIRS_TENTS', 'Chairs / Tents'),
        ('LIGHTS', 'Lights'),
        ('SOUND_EQUIPMENT', 'Sound Equipment'),
        ('DECORATION_ITEMS', 'Decoration Items'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORIES)
    total_quantity = models.IntegerField(default=0)
    available_quantity = models.IntegerField(default=0)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    handled_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.quantity} x {self.item.name}"

class PrasadPlanner(models.Model):
    date = models.DateField(default=timezone.now)
    expected_people = models.IntegerField(default=100)
    food_items = models.TextField(help_text="Comma-separated list of food items")
    quantity_calculations = models.TextField(help_text="Calculated ingredient quantities (e.g. Rice: 10kg, etc.)", blank=True, null=True)
    volunteers_assigned = models.ManyToManyField(CustomUser, blank=True, limit_choices_to={'role': CustomUser.NORMAL_VOLUNTEER})

    def __str__(self):
        return f"Prasad Plan for {self.date} (Headcount: {self.expected_people})"

class Announcement(models.Model):
    CATEGORIES = [
        ('PUJA_TIMING', 'Puja Timing'),
        ('VOLUNTEER_MESSAGE', 'Volunteer Message'),
        ('EMERGENCY_NOTICE', 'Emergency Notice'),
        ('EVENT_REMINDER', 'Event Reminder'),
        ('GENERAL', 'General'),
    ]
    title = models.CharField(max_length=150)
    message = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORIES, default='GENERAL')
    created_at = models.DateTimeField(default=timezone.now)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.get_category_display()}: {self.title}"

class GalleryAlbum(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class GalleryMedia(models.Model):
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name='media_files')
    file = models.FileField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Media in {self.album.title}"

class PujaConfiguration(models.Model):
    previous_year_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True, verbose_name="Previous Year Carry Forward Balance")

    def __str__(self):
        return f"Puja Settings (Prev Year Balance: Rs. {self.previous_year_balance})"
