import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import 'core/theme/app_theme.dart';
import 'core/config/app_config.dart';
import 'core/services/storage_service.dart';
import 'core/services/auth_service.dart';
import 'features/auth/presentation/login_screen.dart';
import 'features/admin/presentation/admin_dashboard_screen.dart';
import 'features/armament/presentation/armament_dashboard_screen.dart';
import 'features/supply/presentation/supply_dashboard_screen.dart';
import 'features/technical/presentation/technical_dashboard_screen.dart';
import 'features/human_resources/presentation/hr_dashboard_screen.dart';

/// نقطة الدخول الرئيسية للنظام
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // تهيئة الإعدادات
  await AppConfig.initialize();
  
  // تهيئة خدمات التخزين والمصادقة
  await StorageService.initialize();
  await AuthService.initialize();

  runApp(const MilitarySystemApp());
}

class MilitarySystemApp extends ConsumerWidget {
  const MilitarySystemApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: AppConfig.appName,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      locale: const Locale('ar', 'SA'),
      supportedLocales: const [
        Locale('ar', 'SA'),
        Locale('en', 'US'),
      ],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      routerConfig: ref.watch(goRouterProvider),
      debugShowCheckedModeBanner: false,
    );
  }
}

/// مزود التوجيه الرئيسي للنظام
final goRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/login',
    routes: [
      // شاشة تسجيل الدخول
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),

      // لوحة تحكم المسؤول - تعرض جميع الأقسام
      GoRoute(
        path: '/admin',
        name: 'admin',
        builder: (context, state) => const AdminDashboardScreen(),
        routes: [
          GoRoute(
            path: 'armament',
            name: 'admin_armament',
            builder: (context, state) => const ArmamentDashboardScreen(),
          ),
          GoRoute(
            path: 'supply',
            name: 'admin_supply',
            builder: (context, state) => const SupplyDashboardScreen(),
          ),
          GoRoute(
            path: 'technical',
            name: 'admin_technical',
            builder: (context, state) => const TechnicalDashboardScreen(),
          ),
          GoRoute(
            path: 'human_resources',
            name: 'admin_hr',
            builder: (context, state) => const HRDashboardScreen(),
          ),
        ],
      ),

      // قسم التسليح
      GoRoute(
        path: '/armament',
        name: 'armament',
        builder: (context, state) => const ArmamentDashboardScreen(),
      ),

      // قسم الامداد
      GoRoute(
        path: '/supply',
        name: 'supply',
        builder: (context, state) => const SupplyDashboardScreen(),
      ),

      // قسم الشعبه الفنية
      GoRoute(
        path: '/technical',
        name: 'technical',
        builder: (context, state) => const TechnicalDashboardScreen(),
      ),

      // قسم البشرية
      GoRoute(
        path: '/human_resources',
        name: 'human_resources',
        builder: (context, state) => const HRDashboardScreen(),
      ),
    ],
    redirect: (context, state) {
      final isLogin = state.matchedLocation == '/login';
      final isAuthenticated = authState.value?.isAuthenticated ?? false;

      if (!isAuthenticated && !isLogin) {
        return '/login';
      }

      if (isAuthenticated && isLogin) {
        // توجيه حسب نوع المستخدم
        final userType = authState.value?.userType;
        if (userType == 'admin') {
          return '/admin';
        } else if (userType == 'armament') {
          return '/armament';
        } else if (userType == 'supply') {
          return '/supply';
        } else if (userType == 'technical') {
          return '/technical';
        } else if (userType == 'human_resources') {
          return '/human_resources';
        }
      }

      return null;
    },
  );
});

/// نموذج بيانات المستخدم
class User {
  final String id;
  final String name;
  final String email;
  final String userType;
  final String? department;
  final String? rank;
  final String? phone;
  final DateTime? lastLogin;
  final bool isActive;

  const User({
    required this.id,
    required this.name,
    required this.email,
    required this.userType,
    this.department,
    this.rank,
    this.phone,
    this.lastLogin,
    this.isActive = true,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      userType: json['userType'] ?? '',
      department: json['department'],
      rank: json['rank'],
      phone: json['phone'],
      lastLogin: json['lastLogin'] != null 
          ? DateTime.parse(json['lastLogin']) 
          : null,
      isActive: json['isActive'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'userType': userType,
      'department': department,
      'rank': rank,
      'phone': phone,
      'lastLogin': lastLogin?.toIso8601String(),
      'isActive': isActive,
    };
  }

  bool get isAdmin => userType == 'admin';
  bool get isArmamentOfficer => userType == 'armament';
  bool get isSupplyOfficer => userType == 'supply';
  bool get isTechnicalOfficer => userType == 'technical';
  bool get isHROfficer => userType == 'human_resources';
}

/// حالات المصادقة
enum AuthStatus {
  unknown,
  authenticated,
  unauthenticated,
  loading,
  error,
}

/// حالة المصادقة
class AuthState {
  final User? user;
  final AuthStatus status;
  final String? error;

  const AuthState({
    this.user,
    this.status = AuthStatus.unknown,
    this.error,
  });

  factory AuthState.initial() {
    return const AuthState(status: AuthStatus.unknown);
  }

  factory AuthState.authenticated(User user) {
    return AuthState(
      user: user,
      status: AuthStatus.authenticated,
    );
  }

  factory AuthState.unauthenticated() {
    return const AuthState(status: AuthStatus.unauthenticated);
  }

  factory AuthState.error(String message) {
    return AuthState(
      status: AuthStatus.error,
      error: message,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
  bool get isError => status == AuthStatus.error;

  AuthState copyWith({
    User? user,
    AuthStatus? status,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      status: status ?? this.status,
      error: error ?? this.error,
    );
  }
}
