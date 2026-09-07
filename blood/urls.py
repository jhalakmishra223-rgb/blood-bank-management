from django.urls import path
from . import views
urlpatterns = [
    path("inventory/",views.blood_inventory,name="blood_inventory",),
     path("request/",views.request_blood,name="request_blood"),
     path("my-requests/",views.my_requests,name="my_requests",),
     path("manage-requests/",views.manage_blood_requests,name="manage_blood_requests",),
     path("approve-request/<int:request_id>/",views.approve_request,name="approve_request",),
     path("reject-request/<int:request_id>/",views.reject_request,name="reject_request",),
     path("fulfill-request/<int:request_id>/",views.fulfill_request,name="fulfill_request",),
     path("manage-inventory/",views.manage_inventory,name="manage_inventory",),
     path("update-inventory/<int:inventory_id>/",views.update_inventory,name="update_inventory",),
     path("donate-blood/",views.donate_blood,name="donate_blood"),
     path("my-donations/",views.my_donations,name="my_donations"),
]