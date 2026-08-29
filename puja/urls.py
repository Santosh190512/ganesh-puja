from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Root
    path('', views.dashboard_view, name='dashboard'),
    
    # Auth & Accounts
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/profile/', views.profile_view, name='profile'),
    
    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/add/', views.announcement_add, name='announcement_add'),
    
    # Gallery
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('gallery/album/add/', views.album_add, name='album_add'),
    path('gallery/media/add/', views.media_add, name='media_add'),
    
    # Donations
    path('donations/', views.donation_list, name='donation_list'),
    path('donations/add/', views.donation_add, name='donation_add'),
    path('donations/receipt/<int:pk>/', views.donation_receipt, name='donation_receipt'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    
    # Volunteers
    path('volunteers/', views.volunteer_list, name='volunteer_list'),
    path('volunteers/teams/', views.team_list, name='team_list'),
    path('volunteers/teams/add/', views.team_add, name='team_add'),
    path('volunteers/duty/assign/', views.duty_assign, name='duty_assign'),
    path('volunteers/duty/my/', views.my_duties, name='my_duties'),
    path('volunteers/duty/<int:pk>/update/', views.duty_update, name='duty_update'),
    path('volunteers/attendance/', views.attendance_sheet, name='attendance_sheet'),
    
    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.event_add, name='event_add'),
    
    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_add, name='inventory_add'),
    path('inventory/transaction/add/', views.inventory_transaction, name='inventory_transaction'),
    
    # Vendors
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/add/', views.vendor_add, name='vendor_add'),
    path('vendors/<int:pk>/payment/add/', views.vendor_payment_add, name='vendor_payment_add'),
    path('vendors/quotations/add/', views.quotation_add, name='quotation_add'),
    
    # Prasad
    path('prasad/', views.prasad_list, name='prasad_list'),
    path('prasad/add/', views.prasad_add, name='prasad_add'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
]
