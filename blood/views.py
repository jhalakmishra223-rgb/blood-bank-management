from django.db.models import Sum
from .models import BloodInventory
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BloodRequestForm
from .models import BloodRequest
from django.db.models import Q
from django.shortcuts import get_object_or_404
from donor.models import Donor
from .models import Donation
from .forms import DonationForm
from django.core.mail import send_mail
from django.conf import settings
# Recipient Blood Group -> Compatible Donor Blood Groups
BLOOD_COMPATIBILITY = {
    "O-": ["O-"],
    "O+": ["O-","O+",],
    "A-": ["O-","A-",],
    "A+": ["O-","O+","A-","A+",],
    "B-": ["O-","B-",],
    "B+": ["O-","O+","B-","B+",],
    "AB-": ["O-", "A-","B-","AB-",],
    "AB+": ["O-","O+","A-","A+","B-","B+","AB-","AB+",],
}
def initialize_inventory():
    """
    Ensure that all standard blood groups exist
    in the BloodInventory table.
    """
    for blood_group, _ in BloodInventory.BLOOD_GROUP_CHOICES:
        BloodInventory.objects.get_or_create(
            blood_group=blood_group,
            defaults={
                "units_available": 0
            }
        )
def blood_inventory(request):
    initialize_inventory()
    inventory = BloodInventory.objects.all().order_by("blood_group")
    total_groups = inventory.count()
    total_units = inventory.aggregate(
        total=Sum("units_available")
    )["total"] or 0
    latest = inventory.order_by("-last_updated").first()
    context = {
        "inventory": inventory,
        "total_groups": total_groups,
        "total_units": total_units,
        "latest": latest,
    }
    return render(
        request,
        "blood_inventory.html",
        context,
    )
@login_required
def request_blood(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")
    # Get logged-in user's donor profile
    donor = getattr(request.user, "donor", None)
    if request.method == "POST":
        # Get request type directly from HTML
        request_for = request.POST.get("request_for", "self")
        # Create the form
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            # Attach logged-in user
            blood_request.user = request.user
            # Save request type
            if request_for == "self":
                blood_request.request_for = "self"
            elif request_for == "other":
                blood_request.request_for = "other"
            else:
                messages.error(
                    request,
                    "Invalid request type selected."
                )
                return redirect("request_blood")
            # Default status
            blood_request.status = "Pending"
            # -----------------------------------------
            # REQUEST FOR MYSELF
            # -----------------------------------------
            if request_for == "self":
                # User must have donor profile and blood group
                if not donor or not donor.blood_group:
                    messages.error(
                        request,
                        "Please complete your donor profile and add your blood group first."
                    )
                    return redirect("request_blood")
                # Automatically use logged-in user's name
                full_name = request.user.get_full_name()
                if full_name:
                    blood_request.patient_name = full_name
                else:
                    blood_request.patient_name = request.user.username
                # Check blood compatibility
                compatible_groups = BLOOD_COMPATIBILITY.get(
                    donor.blood_group,
                    []
                )
                if blood_request.blood_group not in compatible_groups:
                    messages.error(
                        request,
                        f"{blood_request.blood_group} blood is not compatible "
                        f"with your registered blood group "
                        f"({donor.blood_group})."
                    )
                    return redirect("request_blood")
            # -----------------------------------------
            # REQUEST FOR SOMEONE ELSE
            # -----------------------------------------

            elif request_for == "other":

                if not blood_request.patient_name.strip():

                    messages.error(
                        request,
                        "Please enter the patient's name."
                    )

                    return redirect("request_blood")

            # -----------------------------------------
            # SAVE REQUEST
            # -----------------------------------------
            blood_request.save()
            # -----------------------------------------
            # SEND EMAIL NOTIFICATION
            # -----------------------------------------
            send_mail(
                subject="BloodBridge - Blood Request Submitted",
                message=f"""
Hello {request.user.get_full_name() or request.user.username},

Your blood request has been successfully submitted to BloodBridge.
Request Details
-------------------------
 Patient Name: {blood_request.patient_name}
    Blood Group: {blood_request.blood_group}
    Request For: {blood_request.request_for}
    Status: {blood_request.status}
-------------------------

Your request is currently pending review by the BloodBridge administrative team.
You can check the status of your request from your
BloodBridge dashboard.

Thank you for using BloodBridge.
            
BloodBridge Team
            """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
            messages.success(
                request,
                "Blood request submitted successfully."
            )
            return redirect("my_requests")
        else:
            # Show form errors in terminal
            print("========== FORM ERRORS ==========")
            for field, errors in form.errors.items():
                print("FIELD:", field)
                print("ERROR:", errors)
            print("=================================")
    else:
        form = BloodRequestForm()
    # -----------------------------------------
    # COMPATIBLE BLOOD GROUPS
    # -----------------------------------------
    compatible_groups = []
    if donor and donor.blood_group:
        compatible_groups = BLOOD_COMPATIBILITY.get(
            donor.blood_group,
            []
        )
    # -----------------------------------------
    # ALL BLOOD GROUPS
    # -----------------------------------------
    all_blood_groups = [
        choice[0]
        for choice in BloodInventory.BLOOD_GROUP_CHOICES
    ]
    context = {
        "form": form,
        "donor": donor,
        "compatible_groups": compatible_groups,
        "all_blood_groups": all_blood_groups,
    }
    return render(
        request,
        "request_blood.html",
        context
    )
@login_required
def my_requests(request):
    # Admins should not access the user request history.
    if request.user.is_staff:
        return redirect("admin_dashboard")
    # Get all blood requests made by the currently logged-in user.
    requests = (
        BloodRequest.objects
        .filter(user=request.user)
        .order_by("-requested_on")
    )
    # Calculate request statistics.
    total_requests = requests.count()
    pending_requests = requests.filter(status="Pending").count()
    approved_requests = requests.filter(status="Approved").count()
    fulfilled_requests = requests.filter(status="Fulfilled").count()
    context = {
        "requests": requests,
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "fulfilled_requests": fulfilled_requests,
    }
    return render(
        request,
        "my_requests.html",
        context
    )
@login_required
def manage_blood_requests(request):
    # Only staff members can access this page.
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to access this page.")
        return redirect("home")

    # Start with base queryset ordered by newest requests first
    requests = BloodRequest.objects.all().order_by("-requested_on")

    # Extract filter parameters from URL query string
    search_query = request.GET.get('q', '').strip()
    blood_group = request.GET.get('blood_group', '').strip()
    status = request.GET.get('status', '').strip()

    # 1. Search filter (Patient name, Hospital, or City)
    if search_query:
        requests = requests.filter(
            Q(patient_name__icontains=search_query) |
            Q(hospital_name__icontains=search_query) |
            Q(city__icontains=search_query)
        )

    # 2. Blood Group filter
    if blood_group:
        requests = requests.filter(blood_group__iexact=blood_group)

    # 3. Status filter
    if status:
        requests = requests.filter(status__iexact=status)

    return render(
        request,
        "manage_blood_requests.html",
        {
            "requests": requests,
        },
    )
@login_required
def approve_request(request, request_id):
    # Only admins can approve requests.
    if not request.user.is_staff:
        messages.error(request, "You are not authorized.")
        return redirect("home")
    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id
    )
    # Update status
    blood_request.status = "Approved"
    blood_request.save()
    # Send approval email to the requester
    send_mail(
        subject="BloodBridge - Blood Request Approved",
        message=f"""
       
 Hello {blood_request.user.get_full_name() or blood_request.user.username},
 
Good news! Your blood request has been approved by the BloodBridge administrative team.
Request Details
-------------------------
Patient Name: {blood_request.patient_name}
Blood Group: {blood_request.blood_group}
Units Required: {blood_request.units_required}
Status: Approved
-------------------------

Your request has been approved and can now proceed to the fulfillment stage.
You can check the latest status of your request from your BloodBridge dashboard.

Thank you for using BloodBridge.
BloodBridge Team
         """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[blood_request.user.email],
        fail_silently=False,
    )
    messages.success(
        request,
        f"Blood request for {blood_request.patient_name} approved successfully."
    )
    return redirect("manage_blood_requests")
@login_required
def reject_request(request, request_id):
    # Only admins can reject requests.
    if not request.user.is_staff:
        messages.error(request, "You are not authorized.")
        return redirect("home")
    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id
    )
    # Update status
    blood_request.status = "Rejected"
    blood_request.save()
    # Send rejection email to the requester
    send_mail(
        subject="BloodBridge - Blood Request Rejected",
        message=f"""
Hello {blood_request.user.get_full_name() or blood_request.user.username},
        
We are sorry to inform you that your blood request has been rejected by the BloodBridge administrative team.
Request Details
-------------------------
Patient Name: {blood_request.patient_name}
    Blood Group: {blood_request.blood_group}
    Units Required: {blood_request.units_required}
    Status: Rejected
-------------------------
Please contact the BloodBridge administration team if you need
further information regarding this request.
You can check the latest status from your BloodBridge dashboard.
    
Thank you for using BloodBridge.
BloodBridge Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[blood_request.user.email],
        fail_silently=False,
    )
    messages.success(
        request,
        f"Blood request for {blood_request.patient_name} rejected successfully."
    )
    return redirect("manage_blood_requests")
@login_required
def fulfill_request(request, request_id):

    # Only admins can fulfill requests.
    if not request.user.is_staff:
        messages.error(request, "You are not authorized.")
        return redirect("home")
    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id
    )
    # Only approved requests can be fulfilled.
    if blood_request.status != "Approved":
        messages.error(
            request,
            "Only approved requests can be fulfilled."
        )
        return redirect("manage_blood_requests")
    # Find inventory for the requested blood group.
    inventory = get_object_or_404(
        BloodInventory,
        blood_group=blood_request.blood_group
    )
    # Check if enough units are available.
    if inventory.units_available < blood_request.units_required:
        messages.error(
            request,
            f"Only {inventory.units_available} units of "
            f"{inventory.blood_group} are available."
        )
        return redirect("manage_blood_requests")
    # Deduct units from inventory.
    inventory.units_available -= blood_request.units_required
    inventory.save()
    # Mark request as fulfilled.
    blood_request.status = "Fulfilled"
    blood_request.save()
    # Send fulfillment email to the requester
    send_mail(
        subject="BloodBridge - Blood Request Fulfilled",
        message=f"""
Hello {blood_request.user.get_full_name() or blood_request.user.username},
Your blood request has been successfully fulfilled by the BloodBridge team.
Request Details
-------------------------
Patient Name: {blood_request.patient_name}
Blood Group: {blood_request.blood_group}
Units Required: {blood_request.units_required}
Status: Fulfilled
-------------------------
The requested blood units have been deducted from the available
BloodBridge inventory.
Thank you for using BloodBridge.
BloodBridge Team
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[blood_request.user.email],
        fail_silently=False,
    )
    messages.success(
        request,
        f"Blood request for {blood_request.patient_name} has been fulfilled."
    )
    return redirect("manage_blood_requests")
@login_required
def manage_inventory(request):
    # Only staff members can access this page.
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("home")
    initialize_inventory()
    # Fetch all blood inventory records.
    inventory_list = (
        BloodInventory.objects
        .all()
        .order_by("blood_group")
    )
    return render(
        request,
        "manage_inventory.html",
        {
            "inventory_list": inventory_list,
        }
    )
@login_required
def update_inventory(request, inventory_id):
    # Only admins can update inventory.
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("home")
    # Get the inventory record.
    inventory = get_object_or_404(
        BloodInventory,
        id=inventory_id
    )
    # Only allow POST requests.
    if request.method == "POST":
        units = request.POST.get("units")
        try:
            units = int(units)
            # Validate input.
            if units <= 0:
                messages.error(
                    request,
                    "Please enter a positive number of units."
                )
            else:
                # Increase inventory.
                inventory.units_available += units
                # Save changes.
                inventory.save()
                messages.success(
                    request,
                    f"{units} units added successfully to {inventory.blood_group}."
                )
        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter a valid number."
            )
    return redirect("manage_inventory")
@login_required
def donate_blood(request):
    donor = Donor.objects.filter(
        user=request.user
    ).first()
    if donor is None:
        messages.warning(
            request,
            "Please complete your donor profile before donating blood."
        )
        return redirect("create_profile")
    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(
                commit=False
            )
            donation.donor = donor
            # New donations always start as Pending
            donation.status = "Pending"
            donation.save()
            # ----------------------------------------
            # SEND DONATION SUBMISSION EMAIL
            # -----------------------------------------
            user_email = request.user.email
            if user_email:
                send_mail(
                    subject="BloodBridge - Donation Request Submitted",
                    message=(
                        f"Hello {request.user.get_full_name() or request.user.username},\n\n"
                        "Your blood donation request has been submitted successfully "
                        "and is currently pending admin approval.\n\n"
                        f"Donation Date: {donation.donation_date}\n"
                        f"Status: {donation.status}\n\n"
                        "You will receive another email when an administrator "
                        "approves or rejects your donation.\n\n"
                        "Thank you for helping save lives through BloodBridge.\n\n"
                        "BloodBridge Team"
                    ),
                    from_email=None,
                    recipient_list=[
                        user_email
                    ],
                    fail_silently=False,
                )
            messages.success(
                request,
                "Your blood donation request has been submitted successfully and is pending admin approval."
            )
            return redirect("dashboard")
    else:
        form = DonationForm()
    return render(
        request,
        "donate_blood.html",
        {
            "form": form
        }
    )
@login_required
def my_donations(request):
    donor = Donor.objects.filter(
        user=request.user
    ).first()
    if donor is None:
        messages.warning(
            request,
            "Please complete your donor profile first."
        )
        return redirect("create_profile")
    donations = Donation.objects.filter(
        donor=donor
    ).order_by("-donation_date", "-id")
    total_donations = donations.count()
    pending_donations = donations.filter(
        status__iexact="Pending"
    ).count()
    approved_donations = donations.filter(
        status__iexact="Approved"
    ).count()
    rejected_donations = donations.filter(
        status__iexact="Rejected"
    ).count()
    context = {
        "donations": donations,
        "total_donations": total_donations,
        "pending_donations": pending_donations,
        "approved_donations": approved_donations,
        "rejected_donations": rejected_donations,
    }
    return render(
        request,
        "my_donations.html",
        context
    )