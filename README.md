# 🚀 Iran Postman

یک ابزار قدرتمند و کامل برای تست API مشابه Postman که با Django و Python ساخته شده است.

## ✨ ویژگی‌ها

### 🌟 ویژگی‌های اصلی
- **درخواست سریع**: ارسال درخواست بدون نیاز به ذخیره
- **مدیریت کالکشن**: سازماندهی درخواست‌ها در کالکشن‌ها
- **تاریخچه کامل**: ذخیره و مشاهده تمام درخواست‌های ارسال شده
- **محیط‌های متغیر**: مدیریت متغیرهای محیط برای آدرس‌ها و کلیدها
- **پاسخ‌های ذخیره شده**: ذخیره پاسخ‌های مهم برای مراجعه آینده

### 🛠️ قابلیت‌های پیشرفته
- پشتیبانی از تمام متدهای HTTP (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- انواع مختلف بدنه درخواست (Raw, Form Data, URL Encoded)
- مدیریت هدرها و پارامترها
- نمایش زیبا و فرمت شده پاسخ‌ها (JSON, XML, HTML)
- آمار و داشبورد جامع
- رابط کاربری فارسی و زیبا

### 🎨 طراحی UI/UX
- طراحی مدرن با Bootstrap 5
- پشتیبانی کامل از زبان فارسی (RTL)
- رنگ‌بندی زیبا و gradient ها
- آیکون‌های Bootstrap Icons
- Responsive Design برای موبایل و تبلت

## 🏗️ معماری پروژه

```
iranpostman/
├── iranpostman/          # پروژه اصلی Django
│   ├── settings.py       # تنظیمات پروژه
│   ├── urls.py          # URL routing اصلی
│   └── wsgi.py          # WSGI configuration
├── request/             # اپلیکیشن اصلی
│   ├── models.py        # مدل‌های دیتابیس
│   ├── views.py         # View ها و API endpoints
│   ├── serializers.py   # DRF Serializers
│   ├── services.py      # سرویس اجرای درخواست‌ها
│   ├── admin.py         # پنل ادمین
│   └── urls.py          # URL routing اپ
├── templates/           # قالب‌های HTML
│   ├── base.html        # قالب پایه
│   └── request/         # قالب‌های اپ request
├── static/              # فایل‌های static
├── media/               # فایل‌های آپلود شده
└── requirements.txt     # dependencies
```

## 🛠️ نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.8+
- pip
- virtualenv (اختیاری اما پیشنهادی)

### مراحل نصب

1. **کلون کردن پروژه**
```bash
git clone <repository-url>
cd iranpostman
```

2. **ایجاد محیط مجازی**
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# یا
env\Scripts\activate     # Windows
```

3. **نصب dependencies**
```bash
pip install -r requirements.txt
```

4. **اجرای migration ها**
```bash
cd iranpostman
python manage.py migrate
```

5. **ایجاد superuser**
```bash
python manage.py createsuperuser
```

6. **اجرای سرور**
```bash
python manage.py runserver
```

7. **دسترسی به اپلیکیشن**
- مراجعه به: `http://localhost:8000`
- پنل ادمین: `http://localhost:8000/admin`

## 📚 استفاده

### 🚀 درخواست سریع
1. به صفحه اصلی بروید
2. متد HTTP را انتخاب کنید
3. URL را وارد کنید
4. پارامترها، هدرها و بدنه را تنظیم کنید
5. روی "ارسال" کلیک کنید

### 📁 مدیریت کالکشن‌ها
1. به بخش "کالکشن‌ها" بروید
2. "کالکشن جدید" را کلیک کنید
3. نام و توضیحات را وارد کنید
4. درخواست‌هایتان را در کالکشن سازماندهی کنید

### 🌍 محیط‌های متغیر
1. به بخش "محیط‌ها" بروید
2. "محیط جدید" را کلیک کنید
3. متغیرهای مورد نیاز را تعریف کنید (مثل BASE_URL, API_KEY)
4. در درخواست‌هایتان از این متغیرها استفاده کنید

### 📈 مشاهده تاریخچه
1. به بخش "تاریخچه" بروید
2. تمام درخواست‌های ارسال شده را مشاهده کنید
3. فیلترها و جستجو را استفاده کنید
4. روی "جزئیات" کلیک کنید تا تمام اطلاعات را ببینید

## 🔧 فناوری‌های استفاده شده

### Backend
- **Django 5.2.3**: فریمورک اصلی وب
- **Django REST Framework**: برای API endpoints
- **Django CORS Headers**: برای CORS policy
- **Requests**: برای ارسال درخواست‌های HTTP
- **SQLite**: دیتابیس (قابل تغییر به PostgreSQL/MySQL)

### Frontend
- **Bootstrap 5**: فریمورک CSS
- **Bootstrap Icons**: آیکون‌ها
- **Axios**: کتابخانه HTTP client
- **Vanilla JavaScript**: برای تعاملات

### ابزارها
- **WhiteNoise**: سرو کردن فایل‌های static
- **Python Decouple**: مدیریت تنظیمات
- **dj-database-url**: تنظیم دیتابیس از URL

## 🚀 قابلیت‌های آینده

- [ ] پشتیبانی از احراز هویت (OAuth, JWT, Basic Auth)
- [ ] Code Generation (تولید کد Python, JavaScript, cURL)
- [ ] Import/Export کالکشن‌ها (Postman format)
- [ ] Team Collaboration
- [ ] Mock Server
- [ ] Test Runner و Automation
- [ ] GraphQL Support
- [ ] WebSocket Testing
- [ ] Performance Testing
- [ ] API Documentation Generator

## 🤝 مشارکت

مشارکت‌های شما خوشامد است! لطفاً:

1. Fork کنید
2. Branch جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. Push کنید (`git push origin feature/amazing-feature`)
5. Pull Request ایجاد کنید

## 📞 پشتیبانی

اگر مشکلی داشتید یا سوالی بود:

- Issue جدید در GitHub ایجاد کنید
- ایمیل بفرستید: [your-email@example.com]

## 📝 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. فایل [LICENSE](LICENSE) را برای جزئیات بیشتر مطالعه کنید.

---

**ساخته شده با ❤️ در ایران 🇮🇷** 