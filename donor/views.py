from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Donor
@login_required
def profile(request):
    donor = request.user.donor
    profile_completed = all([
        donor.age,
        donor.gender,
        donor.blood_group,
        donor.phone,
        donor.address,
        donor.city,
        donor.state,
    ])
    if not profile_completed:
        messages.warning(
            request,
            "Please complete your profile first."
        )
        return redirect("complete_profile")
    context = {
        "donor": donor
    }
    return render(
        request,
        "profile.html",
        context
    )
@login_required
def edit_profile(request):

    donor = request.user.donor

    profile_completed = all([
        donor.age,
        donor.gender,
        donor.blood_group,
        donor.phone,
        donor.address,
        donor.city,
        donor.state,
    ])

    if not profile_completed:

        messages.warning(
            request,
            "Please complete your profile first."
        )

        return redirect("complete_profile")

    if request.method == "POST":

        donor.age = request.POST.get("age")
        donor.gender = request.POST.get("gender")
        donor.blood_group = request.POST.get("blood_group")
        donor.phone = request.POST.get("phone")
        donor.address = request.POST.get("address")
        donor.city = request.POST.get("city")
        donor.state = request.POST.get("state")

        if request.FILES.get("profile_picture"):
            donor.profile_picture = request.FILES.get("profile_picture")

        donor.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("profile")

    return render(
        request,
        "edit_profile.html",
        {
            "donor": donor
        }
    )
@login_required
def complete_profile(request):
    donor = request.user.donor
    if request.method == "POST":
        donor.age = request.POST.get("age")
        donor.gender = request.POST.get("gender")
        donor.blood_group = request.POST.get("blood_group")
        donor.phone = request.POST.get("phone")
        donor.address = request.POST.get("address")
        donor.city = request.POST.get("city")
        donor.state = request.POST.get("state")
        if request.FILES.get("profile_picture"):
            donor.profile_picture = request.FILES.get("profile_picture")
        donor.save()
        messages.success(
            request,
            "Profile completed successfully!"
        )
        return redirect("profile")
    return render(
        request,
        "complete_profile.html",
        {
            "donor": donor
        }
    )
def donors(request):
    donors = Donor.objects.select_related("user").all().order_by("user__username")

    context = {
        "donors": donors,
        "total_donors": donors.count(),
    }

    return render(
        request,
        "donors.html",
        context
    )