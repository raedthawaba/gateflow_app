import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

/// خدمة إدارة التخزين المحلي
class StorageService {
  static SharedPreferences? _prefs;
  static bool _initialized = false;

  /// تهيئة الخدمة
  static Future<void> initialize() async {
    if (_initialized) return;
    
    _prefs = await SharedPreferences.getInstance();
    _initialized = true;
  }

  /// التحقق من التهيئة
  static bool get isInitialized => _initialized;

  /// الحصول على قيمة نصية
  static String? getString(String key) {
    return _prefs?.getString(key);
  }

  /// تعيين قيمة نصية
  static Future<bool> setString(String key, String value) async {
    return _prefs?.setString(key, value) ?? Future.value(false);
  }

  /// الحصول على قيمة عددية
  static int? getInt(String key) {
    return _prefs?.getInt(key);
  }

  /// تعيين قيمة عددية
  static Future<bool> setInt(String key, int value) async {
    return _prefs?.setInt(key, value) ?? Future.value(false);
  }

  /// الحصول على قيمة منطقية
  static bool? getBool(String key) {
    return _prefs?.getBool(key);
  }

  /// تعيين قيمة منطقية
  static Future<bool> setBool(String key, bool value) async {
    return _prefs?.setBool(key, value) ?? Future.value(false);
  }

  /// الحصول على قائمة
  static List<String>? getStringList(String key) {
    return _prefs?.getStringList(key);
  }

  /// تعيين قائمة
  static Future<bool> setStringList(String key, List<String> value) async {
    return _prefs?.setStringList(key, value) ?? Future.value(false);
  }

  /// حذف مفتاح
  static Future<bool> remove(String key) async {
    return _prefs?.remove(key) ?? Future.value(false);
  }

  /// مسح جميع البيانات
  static Future<bool> clearAll() async {
    return _prefs?.clear() ?? Future.value(false);
  }

  // ============ دوال محددة للتطبيق ============

  /// حفظ توكن المصادقة
  static Future<bool> saveAuthToken(String token) async {
    return setString(AppConfig.prefsAuthToken, token);
  }

  /// الحصول على توكن المصادقة
  static String? getAuthToken() {
    return getString(AppConfig.prefsAuthToken);
  }

  /// حذف توكن المصادقة
  static Future<bool> clearAuthToken() async {
    return remove(AppConfig.prefsAuthToken);
  }

  /// حفظ توكن التحديث
  static Future<bool> saveRefreshToken(String token) async {
    return setString(AppConfig.prefsRefreshToken, token);
  }

  /// الحصول على توكن التحديث
  static String? getRefreshToken() {
    return getString(AppConfig.prefsRefreshToken);
  }

  /// حذف توكن التحديث
  static Future<bool> clearRefreshToken() async {
    return remove(AppConfig.prefsRefreshToken);
  }

  /// حفظ بيانات المستخدم
  static Future<bool> saveUserData(Map<String, dynamic> userData) async {
    return setString(AppConfig.prefsUserData, jsonEncode(userData));
  }

  /// الحصول على بيانات المستخدم
  static Map<String, dynamic>? getUserData() {
    final data = getString(AppConfig.prefsUserData);
    if (data == null) return null;
    
    try {
      return jsonDecode(data) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  /// حذف بيانات المستخدم
  static Future<bool> clearUserData() async {
    return remove(AppConfig.prefsUserData);
  }

  /// حفظ لغة التطبيق
  static Future<bool> saveAppLanguage(String language) async {
    return setString(AppConfig.prefsAppLanguage, language);
  }

  /// الحصول على لغة التطبيق
  static String? getAppLanguage() {
    return getString(AppConfig.prefsAppLanguage);
  }

  /// حفظ وضع الثيم
  static Future<bool> saveThemeMode(int modeIndex) async {
    return setInt(AppConfig.prefsThemeMode, modeIndex);
  }

  /// الحصول على وضع الثيم
  static int? getThemeMode() {
    return getInt(AppConfig.prefsThemeMode);
  }

  /// التحقق من أول استخدام
  static bool isFirstLaunch() {
    return getBool('is_first_launch') ?? true;
  }

  /// تعيين أول استخدام
  static Future<bool> setFirstLaunch(bool value) async {
    return setBool('is_first_launch', value);
  }

  /// حفظ آخر عملية فحص
  static Future<bool> saveLastSync(DateTime dateTime) async {
    return setString('last_sync', dateTime.toIso8601String());
  }

  /// الحصول على آخر عملية فحص
  static DateTime? getLastSync() {
    final dateStr = getString('last_sync');
    if (dateStr == null) return null;
    
    try {
      return DateTime.parse(dateStr);
    } catch (e) {
      return null;
    }
  }

  /// حفظ إعدادات الإشعارات
  static Future<bool> saveNotificationSettings(Map<String, dynamic> settings) async {
    return setString('notification_settings', jsonEncode(settings));
  }

  /// الحصول على إعدادات الإشعارات
  static Map<String, dynamic>? getNotificationSettings() {
    final data = getString('notification_settings');
    if (data == null) return null;
    
    try {
      return jsonDecode(data) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  /// حفظ بيانات مؤقتة
  static Future<bool> saveTempData(String key, Map<String, dynamic> data) async {
    return setString('temp_$key', jsonEncode(data));
  }

  /// الحصول على بيانات مؤقتة
  static Map<String, dynamic>? getTempData(String key) {
    final data = getString('temp_$key');
    if (data == null) return null;
    
    try {
      return jsonDecode(data) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  /// حذف بيانات مؤقتة
  static Future<bool> clearTempData(String key) async {
    return remove('temp_$key');
  }
}
