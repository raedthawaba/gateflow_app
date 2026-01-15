# GateFlow System

نظام GateFlow لإدارة حركة المسافرين والسندات الزمنية عبر نقاط متعددة.

## الوصف

منصة إدارية رقمية متكاملة تهدف إلى إدارة حركة المسافرين عبر نقاط دخول متعددة، مع التركيز على:

- **إصدار السندات الزمنية الرقمية** - إنشاء وإدارة سندات الدخول والخروج
- **التحقق الآلي من قائمة المطلوبين** - مطابقة فورية مع قواعد البيانات
- **التكامل مع كاميرات المراقبة** - توثيق بصري للحركة
- **العمل دون اتصال بالإنترنت** - Offline-first architecture

## التقنيات

- **Frontend**: Flutter (Android, iOS, Web)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL / SQLite
- **Authentication**: JWT with RBAC

## الأدوار

| الدور | الوصف |
|-------|-------|
| System Admin | إدارة كاملة للنظام |
| Supervisor | مراقبة وتقارير وتنبيهات |
| Entry Officer | إدخال مسافرين وإصدار سندات |
| Exit Officer | تسجيل خروج المسافرين |
| Viewer | عرض فقط |

## هيكل المشروع

```
gateflow_app/
├── android/          # ملفات Android الأصلية
├── ios/              # ملفات iOS الأصلية
├── web/              # ملفات Web
├── lib/              # الكود المصدري Flutter
│   ├── core/         # المكونات الأساسية المشتركة
│   ├── auth/         # وحدة المصادقة
│   ├── travelers/    # وحدة المسافرين
│   ├── permits/      # وحدة السندات
│   ├── scanner/      # وحدة المسح الضوئي
│   ├── cameras/      # وحدة الكاميرات
│   ├── alerts/       # وحدة التنبيهات
│   ├── reports/      # وحدة التقارير
│   └── ...
├── assets/           # الملفات الثابتة
├── test/             # اختبارات الوحدة
└── pubspec.yaml      # تبعيات المشروع
```

## البدء

### المتطلبات

- Flutter SDK 3.0+
- Dart SDK 3.0+
- Android Studio / VS Code

### التثبيت

```bash
# استنساخ المستودع
git clone https://github.com/raedthawaba/gateflow_app.git

# الدخول للمجلد
cd gateflow_app

# تثبيت التبعيات
flutter pub get

# تشغيل التطبيق
flutter run
```

## الترخيص

MIT License

---

**GateFlow** - إدارة آمنة ومنظمة لحركة المسافرين

