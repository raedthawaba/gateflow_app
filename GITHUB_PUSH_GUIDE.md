# دليل استرجاع المشروع النظيف - GateFlow App

## المشكلة والحل

واجهنا مشاكل في رفع الملفات مباشرة من بيئة التطوير السحابية بسبب مشاكل الشبكة. يرجى اتباع هذه الخطوات للحصول على النسخة النظيفة من المشروع على جهازك المحلي.

---

## الطريقة 1: حذف المشروع القديم وسحب النسخة الجديدة

افتح Terminal في جهازك وانفذ الأوامر التالية بالترتيب:

```bash
# 1. الانتقال إلى مجلد المشروع (استبدل المسار بموقع مشروعك)
cd /path/to/your/project

# 2. حذف مجلد .git لإعادة تعيين التاريخ
rm -rf .git

# 3. إعادة تهيئة Git
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"

# 4. إضافة المستودع البعيد
git remote add origin https://github.com/raedthawaba/gateflow_app.git

# 5. جلب جميع الفروع
git fetch origin

# 6. حذف الفرع المحلي الرئيسي
git branch -D main

# 7. إنشاء فرع رئيسي جديد من الفرع البعيد
git checkout -b main origin/main

# 8. حذف جميع الملفات المحلية غير المتتبعة
git clean -fd

# 9. جلب الملفات النظيفة
git pull origin main --force
```

---

## الطريقة 2: إذا أردت الاحتفاظ بالتغييرات المحلية

إذا كان لديك تغييرات محلية لا تريد فقدانها:

```bash
# 1. إحفظ التغييرات المحلية
git add .
git commit -m "Local changes backup"

# 2. اسحب التغييرات الجديدة من المستودع
git fetch origin
git reset --hard origin/main

# 3. راجع الملفات الجديدة
ls -la lib/
```

---

## الطريقة 3:克隆 المشروع من جديد

إذا كانت الطريقة الأولى لا تعمل:

```bash
# 1. احذف المجلد القديم
rm -rf gateflow_app

# 2. استنسخ المشروع من جديد
git clone https://github.com/raedthawaba/gateflow_app.git

# 3. ادخل مجلد المشروع
cd gateflow_app

# 4. تأكد من أنك على الفرع الرئيسي
git checkout main
```

---

## الخطوة 2: تشغيل المشروع

بعد الحصول على الملفات، نفذ:

```bash
# الحصول على التبعيات
flutter pub get

# تشغيل المشروع
flutter run
```

---

## الهيكلية الجديدة للمشروع

```
gateflow_app/
├── lib/
│   ├── main.dart                 # نقطة الدخول الرئيسية
│   ├── core/
│   │   ├── theme/
│   │   │   └── app_theme.dart    # إعدادات الثيم (Material 3)
│   │   └── widgets/
│   │       ├── custom_button.dart  # زر مخصص
│   │       └── custom_input.dart   # حقل إدخال مخصص
│   └── features/
│       ├── auth/
│       │   └── presentation/
│       │       └── login_screen.dart  # شاشة تسجيل الدخول
│       ├── dashboard/
│       │   └── presentation/
│       │       └── dashboard_screen.dart  # لوحة التحكم الرئيسية
│       ├── gates/
│       │   └── presentation/
│       │       └── gates_list_screen.dart  # قائمة البوابات
│       ├── permits/
│       │   └── presentation/
│       │       └── permits_list_screen.dart  # قائمة التصاريح
│       ├── travelers/
│       │   └── presentation/
│       │       └── travelers_list_screen.dart  # قائمة المسافرين
│       ├── scanner/
│       │   └── presentation/
│       │       └── scanner_screen.dart  # الماسح الضوئي
│       └── alerts/
│           └── presentation/
│               └── alerts_list_screen.dart  # قائمة التنبيهات
├── pubspec.yaml                  # تبعيات المشروع
└── assets/                       # الأصول (أيقونات، صور، ترجمات)
```

---

## التقنيات المستخدمة في النسخة النظيفة

- **State Management**: Riverpod (بدلاً من BLoC)
- **Navigation**: GoRouter (للإعلانات التوجيهية)
- **UI Framework**: Material 3
- **HTTP Client**: Dio
- **Icons**: Font Awesome Flutter
- **Architecture**: Feature-First (تنظيم حسب المميزات)

---

## المشاكل المحتملة وحلولها

### مشكلة: رفض الاتصال بالمستودع

```bash
# تحقق من الاتصال
ping github.com

# أو استخدم VPN إذا كان محجوباً في منطقتك
```

### مشكلة: فشل في سحب الملفات

```bash
# جرب_force pull
git pull origin main --force --allow-unrelated-histories
```

### مشكلة: عدم التعرف على Flutter

```bash
# تحقق من تثبيت Flutter
flutter --version

# إذا لم يكن مثبتاً، حمله من:
# https://docs.flutter.dev/get-started/install
```

### مشكلة: خطأ في التوكن

```bash
# إذا طلب كلمة مرور، أدخل Personal Access Token وليس كلمة المرور العادية
# أنشئ توكن من: https://github.com/settings/tokens
```

---

## الأوامر المفيدة

```bash
# تحديث التبعيات
flutter pub upgrade

# تنظيف المشروع
flutter clean

# إعادة بناء المشروع
flutter pub get
flutter run

# التحقق من تحليل الكود
flutter analyze

# تشغيل الاختبارات
flutter test
```

---

## الخطوات التالية (المرحلة 2)

بعد التأكد من عمل المشروع بنجاح، سننتقل إلى:

1. ربط شاشة تسجيل الدخول بـ API
2. إنشاء شاشة البوابات (Gates) مع البيانات الحقيقية
3. إضافة شاشة التصاريح (Permits)
4. ربط الماسح الضوئي (QR/Barcode Scanner)
5. إضافة نظام التنبيهات (Push Notifications)

---

## مقارنة الهيكل القديم والجديد

### الهيكل القديم (المشاكل):
```
lib/
├── auth/           # BLoC pattern
├── core/           # mixed files
├── gates/
├── permits/
├── travelers/
└── ...
```

### الهيكل الجديد (النظيف):
```
lib/
├── core/
│   ├── theme/      # centralized theming
│   └── widgets/    # reusable components
└── features/
    ├── auth/       # login screen only
    ├── dashboard/  # main screen
    ├── gates/
    ├── permits/
    ├── travelers/
    ├── scanner/
    └── alerts/
```

---

## معلومات الاتصال

إذا واجهتك أي مشاكل، تواصل معنا للحصول على المساعدة.

---

**تم إنشاء هذا الدليل بواسطة MiniMax Agent**
