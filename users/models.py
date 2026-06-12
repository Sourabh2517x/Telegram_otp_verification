from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from model_utils.models import TimeStampedModel
from django.contrib.auth.hashers import make_password, check_password

# Custom user model
class User(AbstractUser):
    phoneno = models.CharField(max_length=10, unique=True)
    telegram_chat_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.username


#  OTP model using TimeStampedModel
class OTP(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=128)
    is_used = models.BooleanField(default=False)
    
    def set_code(self, raw_code):
        self.code = make_password(str(raw_code))

    def verify_code(self, raw_code):
        return check_password(raw_code, self.code)

    def __str__(self):
        return f"{self.user.username} - {self.code}"

    #  OTP expiry logic
    @property
    def remaining_time(self):
        elapsed = (timezone.now() - self.created).total_seconds()
        return max(0, int(30 - elapsed))

    @property
    def is_expired(self):
        return self.remaining_time == 0 or self.is_used
