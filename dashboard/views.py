from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from donor.models import Donor
from blood.models import BloodRequest, BloodInventory, Donation
from django.db.models import Q
from django.db.models import Sum
from accounts.models import ContactMessage
from django.core.mail import send_mail
# =========================================================
# ADMIN DASHBOARD
# =========================================================
@login_required
def admin_dashboard(request):

    # Only staff/admin users can access the admin dashboard
    if not request.user.is_staff:
        messages.error(
            request,
            "Please login using the Admin Login page."
        )
        return redirect("login")

    # ==============================
    # USER STATISTICS
    # ==============================

    total_users = User.objects.filter(is_staff=False).count()

    active_users = User.objects.filter(
        is_staff=False,
        is_active=True
    ).count()

    inactive_users = User.objects.filter(
        is_staff=False,
        is_active=False
    ).count()

    # ==============================
    # DONOR STATISTICS
    # ==============================

    total_donors = Donor.objects.count()

    # ==============================
    # BLOOD REQUEST STATISTICS
    # ==============================

    total_blood_requests = BloodRequest.objects.count()

    pending_blood_requests = BloodRequest.objects.filter(
        status="Pending"
    ).count()

    approved_blood_requests = BloodRequest.objects.filter(
        status="Approved"
    ).count()

    fulfilled_blood_requests = BloodRequest.objects.filter(
        status="Fulfilled"
    ).count()

    rejected_blood_requests = BloodRequest.objects.filter(
        status="Rejected"
    ).count()

    # ==============================
    # DONATION STATISTICS
    # ==============================

    total_donations = Donation.objects.count()

    pending_donations = Donation.objects.filter(
        status="Pending"
    ).count()

    approved_donations = Donation.objects.filter(
        status="Approved"
    ).count()

    rejected_donations = Donation.objects.filter(
        status="Rejected"
    ).count()

    # Total units from approved donations
    total_donated_units = Donation.objects.filter(
        status="Approved"
    ).aggregate(
        total=Sum("units_donated")
    )["total"] or 0

    # ==============================
    # BLOOD INVENTORY
    # ==============================

    inventory = BloodInventory.objects.all().order_by("blood_group")

    total_inventory_units = inventory.aggregate(
        total=Sum("units_available")
    )["total"] or 0

    # ==============================
    # CONTEXT
    # ==============================

    context = {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,

        "total_donors": total_donors,

        "total_blood_requests": total_blood_requests,
        "pending_blood_requests": pending_blood_requests,
        "approved_blood_requests": approved_blood_requests,
        "fulfilled_blood_requests": fulfilled_blood_requests,
        "rejected_blood_requests": rejected_blood_requests,

        "total_donations": total_donations,
        "pending_donations": pending_donations,
        "approved_donations": approved_donations,
        "rejected_donations": rejected_donations,
        "total_donated_units": total_donated_units,

        "inventory": inventory,
        "total_inventory_units": total_inventory_units,
    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )
# =========================================================
# MANAGE USERS
# =========================================================

@login_required
def manage_users(request):

    # Only staff/admin users can access this page
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("home")

    # -----------------------------------------------------
    # Get ONLY normal users
    # Admin/staff accounts are excluded.
    # Superusers are also excluded.
    # -----------------------------------------------------

    users = (
        User.objects
        .filter(
            is_staff=False,
            is_superuser=False
        )
        .select_related("donor")
        .order_by("-date_joined")
    )

    # -----------------------------------------------------
    # Summary counts
    # -----------------------------------------------------

    total_users = users.count()

    active_users = users.filter(
        is_active=True
    ).count()

    # Since admins are excluded above,
    # this represents the number of normal users.
    total_admins = User.objects.filter(
        is_staff=True
    ).count()

    total_donors = Donor.objects.count()

    # -----------------------------------------------------
    # Search & Filter
    # -----------------------------------------------------

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    status_filter = request.GET.get(
        "status",
        ""
    ).strip()

    role_filter = request.GET.get(
        "role",
        ""
    ).strip()

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            |
            Q(first_name__icontains=search_query)
            |
            Q(last_name__icontains=search_query)
            |
            Q(email__icontains=search_query)
        )

    # -----------------------------------------------------
    # Account Status Filter
    # -----------------------------------------------------

    if status_filter == "active":

        users = users.filter(
            is_active=True
        )

    elif status_filter == "inactive":

        users = users.filter(
            is_active=False
        )

    # -----------------------------------------------------
    # Role Filter
    # -----------------------------------------------------
    # Since admins are already excluded,
    # "admin" will return no users.
    # "user" keeps the normal-user list.
    # -----------------------------------------------------

    if role_filter == "admin":

        users = users.none()

    elif role_filter == "user":

        users = users.filter(
            is_staff=False,
            is_superuser=False
        )

    # -----------------------------------------------------
    # Context
    # -----------------------------------------------------

    context = {
        "users": users,
        "total_users": total_users,
        "active_users": active_users,
        "total_admins": total_admins,
        "total_donors": total_donors,
    }

    return render(
        request,
        "manage_users.html",
        context
    )


# =========================================================
# VIEW SPECIFIC USER
# =========================================================

@login_required
def view_user(request, user_id):

    # Only admins can access this page
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("home")

    # -----------------------------------------------------
    # Get ONLY a normal user.
    #
    # This prevents an admin/staff account from being
    # treated as a normal user.
    # -----------------------------------------------------

    selected_user = get_object_or_404(
        User,
        id=user_id,
        is_staff=False,
        is_superuser=False
    )

    # -----------------------------------------------------
    # Get the donor profile belonging to THIS user
    # -----------------------------------------------------

    donor = Donor.objects.filter(
        user=selected_user
    ).first()

    # -----------------------------------------------------
    # Get blood requests belonging to THIS user
    # -----------------------------------------------------

    blood_requests = (
        BloodRequest.objects
        .filter(
            user=selected_user
        )
        .order_by("-requested_on")
    )

    # -----------------------------------------------------
    # Request statistics
    # -----------------------------------------------------

    total_requests = blood_requests.count()

    pending_requests = blood_requests.filter(
        status__iexact="Pending"
    ).count()

    approved_requests = blood_requests.filter(
        status__iexact="Approved"
    ).count()

    fulfilled_requests = blood_requests.filter(
        status__iexact="Fulfilled"
    ).count()

    rejected_requests = blood_requests.filter(
        status__iexact="Rejected"
    ).count()

    # -----------------------------------------------------
    # Context
    # -----------------------------------------------------

    context = {

        # IMPORTANT:
        # This is the selected user,
        # NOT request.user (the logged-in admin).
        "selected_user": selected_user,

        # Selected user's donor profile
        "donor": donor,

        # Selected user's blood requests
        "blood_requests": blood_requests,

        # Request statistics
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "fulfilled_requests": fulfilled_requests,
        "rejected_requests": rejected_requests,
    }

    return render(
        request,
        "view_user.html",
        context
    )
# =========================================================
# ACTIVATE / DEACTIVATE USER
# =========================================================
@login_required
def toggle_user_status(request, user_id):
    # -----------------------------------------------------
    # Only staff/admin users can access this function
    # -----------------------------------------------------
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to perform this action."
        )
        return redirect("home")
    # -----------------------------------------------------
    # Get ONLY a normal user
    #
    # Admin and superuser accounts are protected.
    # -----------------------------------------------------
    user = get_object_or_404(
        User,
        id=user_id,
        is_staff=False,
        is_superuser=False
    )
    # -----------------------------------------------------
    # Toggle account status
    # -----------------------------------------------------
    if user.is_active:
        user.is_active = False
        messages.success(
            request,
            f"{user.username} has been deactivated successfully."
        )
    else:
        user.is_active = True
        messages.success(
            request,
            f"{user.username} has been activated successfully."
        )
    # -----------------------------------------------------
    # Save the updated status
    # -----------------------------------------------------
    user.save()
    # -----------------------------------------------------
    # Return to Manage Users
    # -----------------------------------------------------
    return redirect("manage_users")
# =========================================================
# MANAGE DONORS
# =========================================================

@login_required
def manage_donors(request):
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("home")
    donors = (
        Donor.objects
        .select_related("user")
        .order_by("-user__date_joined")
    )
    search_query = request.GET.get(
        "q",
        ""
    ).strip()
    if search_query:
        donors = donors.filter(
            Q(user__username__icontains=search_query)
            |
            Q(user__first_name__icontains=search_query)
            |
            Q(user__last_name__icontains=search_query)
            |
            Q(user__email__icontains=search_query)
            |
            Q(blood_group__icontains=search_query)
            |
            Q(city__icontains=search_query)
        )
    blood_group_filter = request.GET.get(
        "blood_group",
        ""
    ).strip()
    if blood_group_filter:
        donors = donors.filter(
            blood_group=blood_group_filter
        )
    status_filter = request.GET.get(
        "status",
        ""
    ).strip()
    if status_filter == "active":
        donors = donors.filter(
            user__is_active=True
        )
    elif status_filter == "inactive":
        donors = donors.filter(
            user__is_active=False
        )
    total_donors = Donor.objects.count()
    active_donors = Donor.objects.filter(
        user__is_active=True
    ).count()
    inactive_donors = Donor.objects.filter(
        user__is_active=False
    ).count()
    context = {
        "donors": donors,
        "total_donors": total_donors,
        "active_donors": active_donors,
        "inactive_donors": inactive_donors,
        "search_query": search_query,
        "blood_group_filter": blood_group_filter,
        "status_filter": status_filter,
    }
    return render(
        request,
        "manage_donors.html",
        context
    )
# =========================================================
# VIEW SPECIFIC DONOR
# =========================================================

@login_required
def view_donor(request, donor_id):
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("home")
    donor = get_object_or_404(
        Donor.objects.select_related("user"),
        id=donor_id
    )
    context = {
        "donor": donor,
    }
    return render(
        request,
        "view_donor.html",
        context
    )
# =========================================================
# MANAGE DONATIONS
# =========================================================

@login_required
def manage_donations(request):

    # Only staff/admin users can access this page
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("home")
    donations = (
        Donation.objects
        .select_related("donor", "donor__user")
        .order_by("-donation_date", "-id")
    )
    search_query = request.GET.get(
        "q",
        ""
    ).strip()
    if search_query:
        donations = donations.filter(
            Q(donor__user__username__icontains=search_query)
            |
            Q(donor__user__first_name__icontains=search_query)
            |
            Q(donor__user__last_name__icontains=search_query)
            |
            Q(blood_group__icontains=search_query)
            |
            Q(hospital_name__icontains=search_query)
            |
            Q(city__icontains=search_query)
        )
    status_filter = request.GET.get(
        "status",
        ""
    ).strip()
    if status_filter:
        donations = donations.filter(
            status__iexact=status_filter
        )
    all_donations = Donation.objects.all()
    total_donations = all_donations.count()
    pending_donations = all_donations.filter(
        status__iexact="Pending"
    ).count()
    approved_donations = all_donations.filter(
        status__iexact="Approved"
    ).count()
    rejected_donations = all_donations.filter(
        status__iexact="Rejected"
    ).count()
    context = {
        "donations": donations,
        "total_donations": total_donations,
        "pending_donations": pending_donations,
        "approved_donations": approved_donations,
        "rejected_donations": rejected_donations,
        "search_query": search_query,
        "status_filter": status_filter,
    }
    return render(
        request,
        "manage_donations.html",
        context
    )
# =========================================================
# APPROVE DONATION
# =========================================================
@login_required
def approve_donation(request, donation_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to perform this action."
        )
        return redirect("home")

    if request.method != "POST":
        return redirect("manage_donations")

    donation = get_object_or_404(
        Donation,
        id=donation_id
    )

    if donation.status != "Pending":
        messages.warning(
            request,
            "This donation has already been processed."
        )
        return redirect("manage_donations")

    # Add donated units to inventory
    inventory, created = BloodInventory.objects.get_or_create(
        blood_group=donation.blood_group,
        defaults={
            "units_available": 0
        }
    )

    inventory.units_available += donation.units_donated
    inventory.save()

    # Change donation status
    donation.status = "Approved"
    donation.save()

    # -----------------------------------------
    # SEND APPROVAL EMAIL TO DONOR
    # -----------------------------------------

    donor_email = donation.donor.user.email

    if donor_email:

        send_mail(
            subject="BloodBridge - Donation Approved",

            message=(
                f"Hello {donation.donor.user.get_full_name() or donation.donor.user.username},\n\n"

                "Good news! Your blood donation has been approved "
                "by the BloodBridge administration team.\n\n"

                f"Blood Group: {donation.blood_group}\n"
                f"Units Donated: {donation.units_donated}\n"
                f"Donation Date: {donation.donation_date}\n"
                f"Status: {donation.status}\n\n"

                "Your donation has also been added to the BloodBridge "
                "blood inventory and can help patients in need.\n\n"

                "Thank you for your valuable contribution and for helping "
                "save lives.\n\n"

                "BloodBridge Team"
            ),

            from_email=None,

            recipient_list=[
                donor_email
            ],

            fail_silently=False,
        )

    messages.success(
        request,
        f"Donation approved successfully. "
        f"{donation.units_donated} unit(s) of "
        f"{donation.blood_group} added to inventory."
    )

    return redirect("manage_donations")


# =========================================================
# REJECT DONATION
# =========================================================

@login_required
def reject_donation(request, donation_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to perform this action."
        )
        return redirect("home")

    if request.method != "POST":
        return redirect("manage_donations")

    donation = get_object_or_404(
        Donation,
        id=donation_id
    )

    if donation.status != "Pending":
        messages.warning(
            request,
            "This donation has already been processed."
        )
        return redirect("manage_donations")

    # Change donation status
    donation.status = "Rejected"
    donation.save()

    # -----------------------------------------
    # SEND REJECTION EMAIL TO DONOR
    # -----------------------------------------

    donor_email = donation.donor.user.email

    if donor_email:

        send_mail(
            subject="BloodBridge - Donation Request Rejected",

            message=(
                f"Hello {donation.donor.user.get_full_name() or donation.donor.user.username},\n\n"

                "We are sorry to inform you that your blood donation "
                "request has been rejected by the BloodBridge "
                "administration team.\n\n"

                f"Blood Group: {donation.blood_group}\n"
                f"Units Donated: {donation.units_donated}\n"
                f"Donation Date: {donation.donation_date}\n"
                f"Status: {donation.status}\n\n"

                "If you believe this was done in error or you need "
                "additional information, please contact the BloodBridge "
                "administration team.\n\n"

                "Thank you for your willingness to contribute.\n\n"

                "BloodBridge Team"
            ),

            from_email=None,

            recipient_list=[
                donor_email
            ],

            fail_silently=False,
        )

    messages.success(
        request,
        "Donation request rejected successfully."
    )
    return redirect("manage_donations")
@login_required
def manage_contact_messages(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )

        return redirect("login")

    contact_messages = ContactMessage.objects.select_related(
        "user"
    ).order_by("-created_at")

    return render(
        request,
        "manage_contact_messages.html",
        {
            "contact_messages": contact_messages
        }
    )