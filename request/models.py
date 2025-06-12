from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Environment(models.Model):
    """محیط متغیرها برای استفاده در درخواست‌ها"""
    name = models.CharField(max_length=200, verbose_name="نام محیط")
    variables = models.JSONField(default=dict, verbose_name="متغیرها")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "محیط"
        verbose_name_plural = "محیط‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Collection(models.Model):
    """کالکشن درخواست‌ها"""
    name = models.CharField(max_length=200, verbose_name="نام کالکشن")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "کالکشن"
        verbose_name_plural = "کالکشن‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class APIRequest(models.Model):
    """مدل اصلی برای درخواست‌های API"""
    
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ]
    
    BODY_TYPE_CHOICES = [
        ('none', 'None'),
        ('form-data', 'Form Data'),
        ('x-www-form-urlencoded', 'URL Encoded'),
        ('raw', 'Raw'),
        ('binary', 'Binary'),
    ]
    
    RAW_TYPE_CHOICES = [
        ('text', 'Text'),
        ('json', 'JSON'),
        ('javascript', 'JavaScript'),
        ('html', 'HTML'),
        ('xml', 'XML'),
    ]

    # اطلاعات اصلی درخواست
    name = models.CharField(max_length=200, verbose_name="نام درخواست")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='GET', verbose_name="متد")
    url = models.URLField(max_length=2000, verbose_name="آدرس URL")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    
    # Headers
    headers = models.JSONField(default=dict, verbose_name="هدرها")
    
    # Parameters (Query params)
    params = models.JSONField(default=dict, verbose_name="پارامترها")
    
    # Authorization
    auth_type = models.CharField(max_length=50, blank=True, verbose_name="نوع احراز هویت")
    auth_data = models.JSONField(default=dict, verbose_name="داده‌های احراز هویت")
    
    # Body
    body_type = models.CharField(max_length=30, choices=BODY_TYPE_CHOICES, default='none', verbose_name="نوع بدنه")
    body_raw = models.TextField(blank=True, verbose_name="متن خام")
    body_raw_type = models.CharField(max_length=20, choices=RAW_TYPE_CHOICES, default='text', verbose_name="نوع متن خام")
    body_form_data = models.JSONField(default=dict, verbose_name="داده‌های فرم")
    body_urlencoded = models.JSONField(default=dict, verbose_name="داده‌های URL Encoded")
    
    # Settings
    timeout = models.IntegerField(default=30, verbose_name="تایم اوت (ثانیه)")
    follow_redirects = models.BooleanField(default=True, verbose_name="دنبال کردن ریدایرکت")
    
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True, blank=True, verbose_name="کالکشن")
    environment = models.ForeignKey(Environment, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="محیط")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "درخواست API"
        verbose_name_plural = "درخواست‌های API"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.method} {self.name}"
    
    def get_full_url(self):
        """URL کامل با پارامترها"""
        if not self.params:
            return self.url
        
        params_str = '&'.join([f"{k}={v}" for k, v in self.params.items() if v])
        separator = '&' if '?' in self.url else '?'
        return f"{self.url}{separator}{params_str}" if params_str else self.url


class RequestHistory(models.Model):
    """تاریخچه اجرای درخواست‌ها"""
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
    ]

    # Request Info
    request = models.ForeignKey(APIRequest, on_delete=models.CASCADE, null=True, blank=True, verbose_name="درخواست")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="کاربر")
    
    # Request snapshot (در زمان اجرا)
    method = models.CharField(max_length=10, verbose_name="متد")
    url = models.URLField(max_length=2000, verbose_name="آدرس URL")
    headers = models.JSONField(default=dict, verbose_name="هدرها")
    body = models.TextField(blank=True, verbose_name="بدنه درخواست")
    
    # Response Info
    status_code = models.IntegerField(null=True, blank=True, verbose_name="کد وضعیت")
    response_headers = models.JSONField(default=dict, verbose_name="هدرهای پاسخ")
    response_body = models.TextField(blank=True, verbose_name="بدنه پاسخ")
    response_time = models.FloatField(null=True, blank=True, verbose_name="زمان پاسخ (ثانیه)")
    response_size = models.IntegerField(null=True, blank=True, verbose_name="اندازه پاسخ (بایت)")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="وضعیت")
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")
    
    # Timestamps
    executed_at = models.DateTimeField(default=timezone.now, verbose_name="زمان اجرا")

    class Meta:
        verbose_name = "تاریخچه درخواست"
        verbose_name_plural = "تاریخچه درخواست‌ها"
        ordering = ['-executed_at']

    def __str__(self):
        return f"{self.method} {self.url} - {self.status_code or 'Error'}"
    
    def get_response_json(self):
        """تبدیل پاسخ به JSON اگر ممکن باشد"""
        try:
            return json.loads(self.response_body)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def is_success(self):
        """آیا درخواست موفق بوده؟"""
        return 200 <= (self.status_code or 0) < 300


class SavedResponse(models.Model):
    """پاسخ‌های ذخیره شده"""
    name = models.CharField(max_length=200, verbose_name="نام پاسخ")
    history = models.ForeignKey(RequestHistory, on_delete=models.CASCADE, verbose_name="تاریخچه")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ذخیره")

    class Meta:
        verbose_name = "پاسخ ذخیره شده"
        verbose_name_plural = "پاسخ‌های ذخیره شده"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
