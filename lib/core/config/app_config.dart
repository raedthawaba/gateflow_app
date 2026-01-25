import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// إعدادات التطبيق الثابتة
class AppConfig {
  static const String appName = 'النظام العسكري الموحد';
  static const String appVersion = '1.0.0';
  static const String apiBaseUrl = 'https://api.military-system.local';

  // إعدادات التصاريح
  static const int tokenExpiryHours = 24;
  static const int refreshTokenExpiryDays = 7;

  // إعدادات التخزين المحلي
  static const String prefsAuthToken = 'auth_token';
  static const String prefsRefreshToken = 'refresh_token';
  static const String prefsUserData = 'user_data';
  static const String prefsAppLanguage = 'app_language';
  static const String prefsThemeMode = 'theme_mode';

  // أنواع المستخدمين
  static const String userTypeAdmin = 'admin';
  static const String userTypeArmament = 'armament';
  static const String userTypeSupply = 'supply';
  static const String userTypeTechnical = 'technical';
  static const String userTypeHR = 'human_resources';

  // أسماء الأقسام بالعربية
  static const Map<String, String> departmentNames = {
    'admin': 'لوحة المسؤول',
    'armament': 'قسم التسليح',
    'supply': 'قسم الامداد',
    'technical': 'الشعبة الفنية',
    'human_resources': 'قسم البشرية',
  };

  // قائمة الأقسام المتاحة
  static const List<String> availableDepartments = [
    'armament',
    'supply',
    'technical',
    'human_resources',
  ];

  static bool _initialized = false;

  /// تهيئة الإعدادات
  static Future<void> initialize() async {
    if (_initialized) return;

    // تهيئة التخزين المشترك
    await SharedPreferences.getInstance();

    _initialized = true;
    if (kDebugMode) {
      print('AppConfig initialized successfully');
    }
  }

  /// التحقق من التهيئة
  static bool get isInitialized => _initialized;

  /// الحصول على عنوان URL للـ API
  static String getApiUrl(String endpoint) {
    return '$apiBaseUrl/api/v1/$endpoint';
  }

  /// التحقق من صلاحية نوع المستخدم
  static bool isValidUserType(String userType) {
    return [
      userTypeAdmin,
      userTypeArmament,
      userTypeSupply,
      userTypeTechnical,
      userTypeHR,
    ].contains(userType);
  }

  /// الحصول على اسم القسم بالعربية
  static String getDepartmentNameArabic(String department) {
    return departmentNames[department] ?? department;
  }

  /// التحقق إذا كان المستخدم مسؤول
  static bool isAdmin(String userType) {
    return userType == userTypeAdmin;
  }

  /// التحقق إذا كان المستخدم مسؤول قسم
  static bool isDepartmentHead(String userType) {
    return isValidUserType(userType) && userType != userTypeAdmin;
  }
}

/// نموذج إعدادات المستخدم
class UserSettings {
  final String language;
  final ThemeMode themeMode;
  final bool notificationsEnabled;
  final bool biometricEnabled;

  const UserSettings({
    required this.language,
    required this.themeMode,
    required this.notificationsEnabled,
    required this.biometricEnabled,
  });

  factory UserSettings.defaults() {
    return const UserSettings(
      language: 'ar',
      themeMode: ThemeMode.system,
      notificationsEnabled: true,
      biometricEnabled: false,
    );
  }

  factory UserSettings.fromJson(Map<String, dynamic> json) {
    return UserSettings(
      language: json['language'] ?? 'ar',
      themeMode: ThemeMode.values[json['themeMode'] ?? 0],
      notificationsEnabled: json['notificationsEnabled'] ?? true,
      biometricEnabled: json['biometricEnabled'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'language': language,
      'themeMode': themeMode.index,
      'notificationsEnabled': notificationsEnabled,
      'biometricEnabled': biometricEnabled,
    };
  }
}

/// أنواع أوضاع الثيم
enum ThemeMode {
  light,
  dark,
  system,
}

/// نموذج بيانات الإشعارات
class NotificationSettings {
  final bool newRequests;
  final bool approvalUpdates;
  final bool systemAlerts;
  final bool dailyReports;
  final int alertFrequencyHours;

  const NotificationSettings({
    required this.newRequests,
    required this.approvalUpdates,
    required this.systemAlerts,
    required this.dailyReports,
    required this.alertFrequencyHours,
  });

  factory NotificationSettings.defaults() {
    return const NotificationSettings(
      newRequests: true,
      approvalUpdates: true,
      systemAlerts: true,
      dailyReports: false,
      alertFrequencyHours: 1,
    );
  }

  factory NotificationSettings.fromJson(Map<String, dynamic> json) {
    return NotificationSettings(
      newRequests: json['newRequests'] ?? true,
      approvalUpdates: json['approvalUpdates'] ?? true,
      systemAlerts: json['systemAlerts'] ?? true,
      dailyReports: json['dailyReports'] ?? false,
      alertFrequencyHours: json['alertFrequencyHours'] ?? 1,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'newRequests': newRequests,
      'approvalUpdates': approvalUpdates,
      'systemAlerts': systemAlerts,
      'dailyReports': dailyReports,
      'alertFrequencyHours': alertFrequencyHours,
    };
  }
}
