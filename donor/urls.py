from django.urls import path
from . import views

urlpatterns = [
    path("profile/",views.profile,name="profile",),
    path("edit-profile/",views.edit_profile,name="edit_profile",),
    path("complete-profile/",views.complete_profile,name="complete_profile",),
    
]