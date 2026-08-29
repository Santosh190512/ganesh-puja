from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, VolunteerTeam, Donation, Expense, VolunteerDuty, 
                     Attendance, PujaEvent, Vendor, Quotation, VendorPayment, 
                     InventoryItem, StockTransaction, PrasadPlanner, Announcement, 
                     GalleryAlbum, GalleryMedia, PujaConfiguration, HouseDonation)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'team', 'mobile', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'team', 'mobile')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'team', 'mobile')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(VolunteerTeam)
admin.site.register(Donation)
admin.site.register(Expense)
admin.site.register(VolunteerDuty)
admin.site.register(Attendance)
admin.site.register(PujaEvent)
admin.site.register(Vendor)
admin.site.register(Quotation)
admin.site.register(VendorPayment)
admin.site.register(InventoryItem)
admin.site.register(StockTransaction)
admin.site.register(PrasadPlanner)
admin.site.register(Announcement)
admin.site.register(GalleryAlbum)
admin.site.register(GalleryMedia)
admin.site.register(PujaConfiguration)
admin.site.register(HouseDonation)

