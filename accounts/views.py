from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from donor.models import Donor
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from .forms import ContactMessageForm
from donor.models import Donor
from blood.models import BloodInventory, BloodRequest

def home(request):
    # -----------------------------------------
    # TOTAL DONORS
    # -----------------------------------------
    total_donors = Donor.objects.count()
    # -----------------------------------------
    # TOTAL AVAILABLE BLOOD UNITS
    # -----------------------------------------
    total_units = BloodInventory.objects.aggregate(
        total=Sum("units_available")
    )["total"] or 0
    # -----------------------------------------
    # TOTAL BLOOD REQUESTS
    # -----------------------------------------
    total_requests = BloodRequest.objects.count()
    # -----------------------------------------
    # BLOOD INVENTORY
    # -----------------------------------------
    inventory = BloodInventory.objects.all().order_by(
        "blood_group"
    )
    context = {
        "total_donors": total_donors,
        "total_units": total_units,
        "total_requests": total_requests,
        "inventory": inventory,

        # Kept as requested for now
        "partner_hospitals": 150,
    }
    return render(
        request,
        "home.html",
        context
    )
def donors(request):
    return render(request, "donors.html")
def services(request):
    return render(request, "services.html")
def contact(request):
    return render(request, "contact.html")
def login(request):
    print(">>>>>>>> USER LOGIN VIEW <<<<<<<<")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user is not None:
            # Admins are not allowed here
            if user.is_staff:
                messages.error(
                    request,
                    "Administrators must use the Admin Login page."
                )
                return redirect("login")
            auth_login(request, user)
            messages.success(
                request,
                "Login Successful!"
            )
            return redirect("dashboard")
        messages.error(
            request,
            "Invalid Username or Password."
        )
        return redirect("login")
    return render(request, "login.html")
def signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        # Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")
        # Check username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("signup")
        # Check email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )
        user.save()
        Donor.objects.create(
    user=user
)
        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")
    return render(request, "signup.html")
def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")
@login_required
def dashboard(request):
    if request.user.is_staff:
        messages.error(
            request,
            "Administrators must use the Admin Login page."
        )
        return redirect("admin_login")
    donor = request.user.donor
    fields = [
        donor.age,
        donor.gender,
        donor.blood_group,
        donor.phone,
        donor.address,
        donor.city,
        donor.state,
        donor.profile_picture,
    ]
    completed = sum(bool(field) for field in fields)
    total_fields = len(fields)
    profile_completion = int(
        (completed / total_fields) * 100
    )
    profile_completed = completed == total_fields
    context = {
        "donor": donor,
        "profile_completion": profile_completion,
        "profile_completed": profile_completed,
    }
    return render(
        request,
        "dashboard.html",
        context
    )
@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("change_password")
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password changed successfully.")
        return redirect("dashboard")
    return render(request, "change_password.html")
def admin_login(request):

    print(">>>>>>>> ADMIN LOGIN VIEW <<<<<<<<")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if not user.is_staff:
                messages.error(
                    request,
                    "Access denied. Please login using the User Login page."
                )
                return redirect("admin_login")

            auth_login(request, user)

            messages.success(
                request,
                "Welcome Admin!"
            )

            return redirect("admin_dashboard")

        else:
            messages.error(
                request,
                "Invalid username or password."
            )
            return redirect("admin_login")

    return render(request, "admin_login.html")
def contact(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            # Connect message to logged-in user
            if request.user.is_authenticated:
                contact_message.user = request.user
            contact_message.save()
            # Send email notification to admin
            send_mail(
                subject=f"BloodBridge Contact Message - {contact_message.get_subject_display()}",
                message=(
                    f"New message received from BloodBridge.\n\n"
                    f"Name: {contact_message.full_name}\n"
                    f"Email: {contact_message.email}\n"
                    f"Subject: {contact_message.get_subject_display()}\n\n"
                    f"Message:\n"
                    f"{contact_message.message}\n\n"
                    f"Submitted at: {contact_message.created_at}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    settings.ADMIN_EMAIL
                ],

                fail_silently=True,
            )
            # Confirmation email to user
            send_mail(
                subject="BloodBridge - Message Received",
                message=(
                    f"Hello {contact_message.full_name},\n\n"
                    f"Thank you for contacting BloodBridge.\n\n"
                    f"We have received your message regarding "
                    f"'{contact_message.get_subject_display()}'.\n\n"
                    f"Our team will review your message and get back to you "
                    f"as soon as possible.\n\n"
                    f"Regards,\n"
                    f"BloodBridge Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    contact_message.email
                ],

                fail_silently=True,
            )
            messages.success(
                request,
                "Your message has been sent successfully. Our team will get back to you soon."
            )
            return redirect("contact")
    else:
        # Pre-fill user information if logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                "full_name": request.user.get_full_name()
                or request.user.username,

                "email": request.user.email,
            }
        form = ContactMessageForm(
            initial=initial_data
        )
    return render(
        request,
        "contact.html",
        {
            "form": form
        }
    )
