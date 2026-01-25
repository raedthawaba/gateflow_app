#!/bin/bash

# ============================================
# سكريبت إعداد ورفع مستودع GateFlow إلى GitHub
# ============================================

# ألوان للطباعة
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   إعداد مستودع GateFlow - GitHub${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# دالة للطباعة الملونة
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# التحقق من وجود Git
if ! command -v git &> /dev/null; then
    print_error "Git غير مثبت. يرجى تثبيت Git أولاً."
    exit 1
fi
print_status "Git مثبت بنجاح"

# التحقق من وجود مستودع Git
if [ ! -d .git ]; then
    print_warning "جاري تهيئة مستودع Git..."
    git init
    git branch -M main
else
    print_status "المستودع موجود مسبقاً"
fi

# إضافة remote
if ! git remote get-url origin &> /dev/null; then
    print_warning "جاري إضافة remote..."
    git remote add origin https://github.com/raedthawaba/gateflow_app.git
else
    print_warning "Remote موجود مسبقاً، جاري التحديث..."
    git remote set-url origin https://github.com/raedthawaba/gateflow_app.git
fi
print_status "Remote مُكوّن"

# إنشاء ملف README إذا لم يوجد
if [ ! -f README.md ]; then
    print_warning "جاري إنشاء README.md..."
    cat > README.md << 'EOF'
# GateFlow System

نظام GateFlow لإدارة حركة المسافرين والسندات الزمنية عبر نقاط متعددة.

## الوصف
منصة إدارية رقمية متكاملة تهدف إلى إدارة حركة المسافرين عبر نقاط دخول متعددة، مع التركيز على:
- إصدار السندات الزمنية الرقمية
- التحقق الآلي من قائمة المطلوبين
- التكامل مع كاميرات المراقبة
- العمل دون اتصال بالإنترنت (Offline-first)

## التقنيات
- **Frontend**: Flutter
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL / SQLite
- **Authentication**: JWT

## الأدوار
- System Admin
- Supervisor
- Entry Officer
- Exit Officer
- Viewer

## الترخيص
MIT License
EOF
    git add README.md
    git commit -m "Add initial README"
    print_status "README.md تم إنشاؤه وإضافته"
else
    print_status "README.md موجود"
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}   خطوات المصادقة ورفع المستودع${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# التحقق من وجود GitHub CLI
if command -v gh &> /dev/null; then
    print_status "GitHub CLI موجود"
    echo ""
    echo "اختر طريقة المصادقة:"
    echo "1. استخدام GitHub CLI (gh auth login)"
    echo "2. استخدام Personal Access Token"
    echo ""
    read -p "اختر رقم العملية (1-2): " auth_choice
    
    if [ "$auth_choice" == "1" ]; then
        print_warning "جاري فتح مصادقة GitHub CLI..."
        gh auth login
    else
        print_warning "جاري طلب Personal Access Token..."
        echo ""
        echo "للحصول على Personal Access Token:"
        echo "1. اذهب إلى: https://github.com/settings/tokens"
        echo "2. اضغط على 'Generate new token (classic)'"
        echo "3. اختر الصلاحيات: repo, workflow"
        echo "4. انسخ الـ Token"
        echo ""
        read -p "أدخل Personal Access Token: " gh_token
        echo ""
        
        # استخدام الـ Token للمصادقة
        echo $gh_token | gh auth login --with-token
    fi
else
    print_warning "GitHub CLI غير مثبت"
    echo ""
    echo "لل رفع المستودع، تحتاج إلى المصادقة:"
    echo ""
    echo "الطريقة الأولى: Personal Access Token"
    echo "-----------------------------------"
    echo "1. اذهب إلى: https://github.com/settings/tokens"
    echo "2. اضغط على 'Generate new token (classic)'"
    echo "3. اختر الصلاحيات: repo, workflow"
    echo "4. انسخ الـ Token"
    echo ""
    echo "الطريقة الثانية: SSH Key"
    echo "-----------------------"
    echo "1. أنشئ SSH Key: ssh-keygen -t ed25519 -C 'your_email@example.com'"
    echo "2. أضف الـ Key إلى SSH Agent"
    echo "3. انسخ الـ Public Key إلى GitHub"
    echo ""
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}   رفع المستودع${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# طلب اسم المستخدم
read -p "أدخل اسم مستخدم GitHub: " github_username

# إضافة credentials باستخدام git credential
echo ""
print_warning "سيُطلب منك إدخال credentials للمصادقة"
echo ""

# محاولة الرفع
if git push -u origin main; then
    echo ""
    print_status "تم رفع المستودع بنجاح!"
    echo ""
    echo -e "${GREEN}رابط المستودع:${NC} https://github.com/$github_username/gateflow_app"
    echo -e "${GREEN}رابط Pages:${NC} https://$username.github.io/gateflow_app"
else
    echo ""
    print_error "حدث خطأ أثناء الرفع"
    echo ""
    echo "إذا واجهت خطأ في المصادقة، جرب:"
    echo "1. git config --global credential.helper cache"
    echo "2. git push again"
    echo ""
    echo "أو استخدم Personal Access Token كـ password:"
    echo "git remote set-url origin https://USERNAME:TOKEN@github.com/USERNAME/gateflow_app.git"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   إكمال الإعداد${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# إضافة .gitignore إذا لم يوجد
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# Flutter
.DS_Store
.dart_tool/
.packages
build/
.pub/
.idea/
.vscode/
*.iml

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.venv/
venv/
ENV/
*.egg-info/
dist/
build/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
Thumbs.db
.DS_Store
EOF
    git add .gitignore
    print_status ".gitignore تم إنشاؤه"
fi

# إنشاء الهيكل الكامل للمشروع
echo ""
print_warning "جاري إنشاء هيكل المشروع الكامل..."

# إنشاء مجلدات Flutter
directories=(
    "lib/core/config"
    "lib/core/services"
    "lib/core/guards"
    "lib/core/network"
    "lib/core/utils"
    "lib/core/widgets"
    "lib/core/extensions"
    "lib/auth/models"
    "lib/travelers/models"
    "lib/permits/models"
    "lib/scanner/models"
    "lib/cameras/models"
    "lib/alerts/models"
    "lib/reports/models"
    "assets/images/logo"
    "assets/icons"
    "assets/fonts/Cairo"
    "assets/fonts/Inter"
    "assets/translations"
    "test"
    "integration_test"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
done

# إنشاء ملفات أساسية

# pubspec.yaml
cat > pubspec.yaml << 'EOF'
name: gateflow_app
description: نظام GateFlow لإدارة حركة المسافرين والسندات الزمنية
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: '>=3.10.0'

dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter
  flutter_bloc: ^8.1.3
  dio: ^5.4.0
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  mobile_scanner: ^3.5.0
  qr_flutter: ^4.1.0
  intl: ^0.18.1
  connectivity_plus: ^5.0.2
  flutter_local_notifications: ^16.3.0
  camera: ^0.10.5
  uuid: ^4.2.1
  logger: ^2.0.2+1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.1
  build_runner: ^2.4.8
  bloc_test: ^9.1.5

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/icons/
    - assets/fonts/
    - assets/translations/
EOF

# requirements.txt (Backend)
mkdir -p backend
cat > backend/requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic[email]==2.5.3
qrcode[pil]==7.4.2
apscheduler==3.10.4
redis==5.0.1
pytest==7.4.4
pytest-asyncio==0.23.3
EOF

# git add all
git add -A
git commit -m "Add complete project structure" 2>/dev/null || true

print_status "هيكل المشروع تم إنشاؤه"

echo ""
print_status "تم إعداد المستودع بنجاح!"
echo ""
echo "للرفع إلى GitHub، قم بتنفيذ:"
echo "  git push -u origin main"
echo ""
echo "أو شغل هذا السكريبت مرة أخرى:"
echo "  bash setup_github.sh"
