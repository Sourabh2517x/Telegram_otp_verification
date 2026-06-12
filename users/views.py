import json
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .forms import RegisterForm, LoginForm, OTPForm
from .models import User, OTP
from .utils import create_and_send_otp,generate_token
import logging
from django.views.decorators.http import require_POST
from django.core.cache import cache

logger = logging.getLogger(__name__)


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phoneno"]
            username = form.cleaned_data["username"]

            # Create user only if not exists
            User.objects.create_user(phoneno=phone, username=username)

            return redirect("verify_otp", phone=phone)

    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phoneno"]

            user = User.objects.filter(phoneno=phone).first()

            if not user:
                return redirect("register")

            # If Telegram not connected → go to verify page first
            if not user.telegram_chat_id:
                return redirect("verify_otp", phone=phone)

            # Send OTP
            error = create_and_send_otp(user)

            if error:
                return render(
                    request,
                    "users/login.html",
                    {"form": form, "error": error},
                )

            return redirect("verify_otp", phone=phone)

    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def index(request):
    return render(request, "users/index.html")


@csrf_exempt  # Disable CSRF since Telegram won't send CSRF tokens
def telegram_webhook(request):

    # Verify request is actually from Telegram using secret token
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != settings.TELEGRAM_WEBHOOK_SECRET:
        return JsonResponse({"status": "unauthorized"}, status=403)

    # Only allow POST requests (Telegram sends POST updates)
    if request.method != "POST":
        return JsonResponse({"status": "method not allowed"}, status=405)

    # Parse incoming JSON safely
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "bad request"}, status=400)

    # Extract message object from Telegram update
    message = data.get("message")
    if not message:
        return JsonResponse({"status": "ignored"})

    # Extract text and chat_id (user identifier on Telegram)
    text = message.get("text")
    chat_id = message.get("chat", {}).get("id")

    if not text or not chat_id:
        # Ignore non-text messages
        return JsonResponse({"status": "ignored"})

    if text.startswith("/start"):
        parts = text.split()

        if len(parts) > 1:
            token = parts[1]

            #  Validate token from cache 
            user_id = cache.get(token)
            if not user_id:
                return JsonResponse({"status": "invalid_or_expired"})

            user = User.objects.filter(id=user_id).first()
            if not user:
                return JsonResponse({"status": "invalid_user"})

            if user.telegram_chat_id:
                return JsonResponse({"status": "already_linked"})

            user.telegram_chat_id = chat_id
            user.save()

            error = create_and_send_otp(user)
            if error:
                logger.error("OTP send failed")

            return JsonResponse({"status": "linked"})

    return JsonResponse({"status": "ok"})


def verify_otp(request, phone):
    user = get_object_or_404(User, phoneno=phone)
    otp_obj = OTP.objects.filter(user=user).order_by("-created").first()

    token = generate_token(user)
    telegram_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={token}"

    form = OTPForm(request.POST or None)

    context = {
        "phone": phone,
        "telegram_link": telegram_link,
        "telegram_connected": bool(user.telegram_chat_id),
        "remaining_time": otp_obj.remaining_time if otp_obj else 0,
        "form": form,
    }

    if request.method == "POST" and form.is_valid():
        entered_otp = form.cleaned_data["otp"]

        #  Prevent crash
        if not otp_obj:
            context["error"] = "No OTP found. Please resend"
            return render(request, "users/verify.html", context)

        if otp_obj.is_expired:
            context["error"] = "OTP expired. Please resend"
            return render(request, "users/verify.html", context)

        #  Secure comparison
        if otp_obj.verify_code(entered_otp):
            otp_obj.is_used = True
            otp_obj.save()

            auth_login(request, user)
            return redirect("index")

        context["error"] = "Invalid OTP"
        return render(request, "users/verify.html", context)

    return render(request, "users/verify.html", context)


@require_POST  # for only post request
def resend_otp(request, phone):
    user = get_object_or_404(User, phoneno=phone)

    #  Get latest OTP
    last_otp = OTP.objects.filter(user=user).order_by("-created").first()

    context = {
        "phone": phone,
        "telegram_connected": True,
        "remaining_time": 0,
        "error": None,
    }

    #  Cooldown check
    if last_otp and last_otp.remaining_time > 0:
        context["remaining_time"] = last_otp.remaining_time
        return render(request, "users/verify.html", context)

    #  Send new OTP
    error = create_and_send_otp(user)

    if error:
        context["error"] = error
        return render(request, "users/verify.html", context)

    return redirect("verify_otp", phone=phone)
