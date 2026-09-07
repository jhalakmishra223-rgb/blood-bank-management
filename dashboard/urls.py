from django.urls import path
from . import views

urlpatterns = [
    path("admin-dashboard/",views.admin_dashboard,name="admin_dashboard",),
     path("manage-users/",views.manage_users,name="manage_users",),
      path("manage-users/<int:user_id>/",views.view_user,name="view_user",),
      path("manage-users/<int:user_id>/toggle-status/",views.toggle_user_status,name="toggle_user_status"),
      path("manage-donors/",views.manage_donors,name="manage_donors"),
      path("manage-donors/<int:donor_id>/",views.view_donor,name="view_donor"),
      path("manage-donations/",views.manage_donations,name="manage_donations"),
      path("manage-donations/approve/<int:donation_id>/",views.approve_donation,name="approve_donation"),
      path("manage-donations/reject/<int:donation_id>/",views.reject_donation,name="reject_donation"),
      path("manage-contact-messages/",views.manage_contact_messages,name="manage_contact_messages"),
      
]