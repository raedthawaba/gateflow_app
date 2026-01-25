import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../main.dart';
import 'storage_service.dart';
import '../config/app_config.dart';

/// خدمة إدارة المصادقة
class AuthService {
  static bool _initialized = false;

  /// تهيئة الخدمة
  static Future<void> initialize() async {
    if (_initialized) return;
    await StorageService.initialize();
    _initialized = true;
  }

  /// التحقق من التهيئة
  static bool get isInitialized => _initialized;

  /// تسجيل الدخول
  static Future<AuthState> login(String username, String password) async {
    try {
      // محاكاة طلب API
      await Future.delayed(const Duration(seconds: 1));

      // التحقق من بيانات الدخول (تجريبي)
      if (username == 'admin' && password == 'admin123') {
        final user = User(
          id: '1',
          name: 'المسؤول العام',
          email: 'admin@military.system',
          userType: 'admin',
          department: 'الإدارة العامة',
          rank: 'عقيد',
          phone: '0555123456',
          lastLogin: DateTime.now(),
        );

        // حفظ البيانات
        await StorageService.saveAuthToken('admin_token_${DateTime.now().millisecondsSinceEpoch}');
        await StorageService.saveUserData(user.toJson());

        return AuthState.authenticated(user);
      }

      if (username == 'armament' && password == 'armament123') {
        final user = User(
          id: '2',
          name: 'مسؤول التسليح',
          email: 'armament@military.system',
          userType: 'armament',
          department: 'قسم التسليح',
          rank: 'رائد',
          phone: '0555234567',
          lastLogin: DateTime.now(),
        );

        await StorageService.saveAuthToken('armament_token_${DateTime.now().millisecondsSinceEpoch}');
        await StorageService.saveUserData(user.toJson());

        return AuthState.authenticated(user);
      }

      if (username == 'supply' && password == 'supply123') {
        final user = User(
          id: '3',
          name: 'مسؤول الامداد',
          email: 'supply@military.system',
          userType: 'supply',
          department: 'قسم الامداد',
          rank: 'مقدم',
          phone: '0555345678',
          lastLogin: DateTime.now(),
        );

        await StorageService.saveAuthToken('supply_token_${DateTime.now().millisecondsSinceEpoch}');
        await StorageService.saveUserData(user.toJson());

        return AuthState.authenticated(user);
      }

      if (username == 'technical' && password == 'technical123') {
        final user = User(
          id: '4',
          name: 'مسؤول الشعبة الفنية',
          email: 'technical@military.system',
          userType: 'technical',
          department: 'الشعبة الفنية',
          rank: 'نقيب',
          phone: '0555456789',
          lastLogin: DateTime.now(),
        );

        await StorageService.saveAuthToken('technical_token_${DateTime.now().millisecondsSinceEpoch}');
        await StorageService.saveUserData(user.toJson());

        return AuthState.authenticated(user);
      }

      if (username == 'hr' && password == 'hr123') {
        final user = User(
          id: '5',
          name: 'مسؤول البشرية',
          email: 'hr@military.system',
          userType: 'human_resources',
          department: 'قسم البشرية',
          rank: 'رائد',
          phone: '0555567890',
          lastLogin: DateTime.now(),
        );

        await StorageService.saveAuthToken('hr_token_${DateTime.now().millisecondsSinceEpoch}');
        await StorageService.saveUserData(user.toJson());

        return AuthState.authenticated(user);
      }

      return AuthState.error('اسم المستخدم أو كلمة المرور غير صحيحة');
    } catch (e) {
      return AuthState.error('حدث خطأ أثناء تسجيل الدخول');
    }
  }

  /// تسجيل الخروج
  static Future<void> logout() async {
    await StorageService.clearAuthToken();
    await StorageService.clearRefreshToken();
    await StorageService.clearUserData();
  }

  /// التحقق من حالة تسجيل الدخول
  static Future<AuthState> checkAuthStatus() async {
    try {
      final token = StorageService.getAuthToken();
      final userData = StorageService.getUserData();

      if (token != null && userData != null) {
        final user = User.fromJson(userData);
        return AuthState.authenticated(user);
      }

      return AuthState.unauthenticated();
    } catch (e) {
      return AuthState.unauthenticated();
    }
  }

  /// تحديث بيانات المستخدم
  static Future<void> updateUserData(Map<String, dynamic> data) async {
    await StorageService.saveUserData(data);
  }

  /// التحقق من صلاحية التوكن
  static Future<bool> validateToken() async {
    final token = StorageService.getAuthToken();
    return token != null && token.isNotEmpty;
  }
}

/// مزود حالة المصادقة
final authStateProvider = StateProvider<AuthState>((ref) {
  return AuthState.initial();
});

/// مزود تحميل حالة المصادقة
final authStateFutureProvider = FutureProvider<AuthState>((ref) async {
  return AuthService.checkAuthStatus();
});

/// دالة تسجيل الدخول
Future<AuthState> login(WidgetRef ref, String username, String password) async {
  ref.read(authStateProvider.notifier).state = AuthState(
    status: AuthStatus.loading,
  );

  final result = await AuthService.login(username, password);
  
  ref.read(authStateProvider.notifier).state = result;
  
  return result;
}

/// دالة تسجيل الخروج
Future<void> logout(WidgetRef ref) async {
  await AuthService.logout();
  ref.read(authStateProvider.notifier).state = AuthState.unauthenticated();
}

/// دالة التحقق من تسجيل الدخول
Future<AuthState> checkAuth(WidgetRef ref) async {
  final result = await AuthService.checkAuthStatus();
  ref.read(authStateProvider.notifier).state = result;
  return result;
}
