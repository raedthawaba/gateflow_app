import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../core/widgets/custom_button.dart';
import '../../core/widgets/custom_input.dart';
import '../../core/services/auth_service.dart';
import '../../core/config/app_config.dart';

/// شاشة تسجيل الدخول
class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);
    final usernameController = TextEditingController();
    final passwordController = TextEditingController();
    final formKey = GlobalKey<FormState>();

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // الشعار والعنوان
                  const LogoSection(),
                  const SizedBox(height: 48),

                  // حقل اسم المستخدم
                  CustomInput(
                    label: 'اسم المستخدم',
                    hint: 'أدخل اسم المستخدم',
                    controller: usernameController,
                    keyboardType: TextInputType.text,
                    textInputAction: TextInputAction.next,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'يرجى إدخال اسم المستخدم';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // حقل كلمة المرور
                  PasswordInput(
                    label: 'كلمة المرور',
                    hint: 'أدخل كلمة المرور',
                    controller: passwordController,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'يرجى إدخال كلمة المرور';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 24),

                  // رسالة الخطأ
                  if (authState.isError)
                    Container(
                      padding: const EdgeInsets.all(12),
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        color: Colors.red[50],
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red[200]!),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline, color: Colors.red),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              authState.error ?? 'حدث خطأ',
                              style: GoogleFonts.cairo(
                                color: Colors.red[700],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                  // زر تسجيل الدخول
                  CustomButton(
                    text: 'تسجيل الدخول',
                    isLoading: authState.isLoading,
                    onPressed: () async {
                      if (formKey.currentState!.validate()) {
                        final result = await login(
                          ref,
                          usernameController.text,
                          passwordController.text,
                        );

                        if (result.isAuthenticated) {
                          _navigateToDashboard(context, result.user!);
                        }
                      }
                    },
                  ),
                  const SizedBox(height: 24),

                  // معلومات الاختبار
                  const TestCredentialsCard(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _navigateToDashboard(BuildContext context, User user) {
    final routeName = switch (user.userType) {
      'admin' => '/admin',
      'armament' => '/armament',
      'supply' => '/supply',
      'technical' => '/technical',
      'human_resources' => '/human_resources',
      _ => '/login',
    };

    context.go(routeName);
  }
}

/// قسم الشعار
class LogoSection extends StatelessWidget {
  const LogoSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // أيقونة الشعار
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primary,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: const Icon(
            Icons.shield,
            size: 50,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 24),
        // عنوان التطبيق
        Text(
          AppConfig.appName,
          style: GoogleFonts.cairo(
            fontSize: 28,
            fontWeight: FontWeight.w700,
            color: Theme.of(context).colorScheme.onSurface,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        // وصف التطبيق
        Text(
          'نظام متكامل لإدارة الأقسام العسكرية',
          style: GoogleFonts.cairo(
            fontSize: 14,
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

/// بطاقة بيانات الاختبار
class TestCredentialsCard extends StatelessWidget {
  const TestCredentialsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.info_outline,
                  size: 20,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'بيانات الاختبار',
                  style: GoogleFonts.cairo(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildCredentialRow('المسؤول العام', 'admin', 'admin123'),
            _buildCredentialRow('قسم التسليح', 'armament', 'armament123'),
            _buildCredentialRow('قسم الامداد', 'supply', 'supply123'),
            _buildCredentialRow('الشعبة الفنية', 'technical', 'technical123'),
            _buildCredentialRow('قسم البشرية', 'hr', 'hr123'),
          ],
        ),
      ),
    );
  }

  Widget _buildCredentialRow(String title, String username, String password) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              title,
              style: GoogleFonts.cairo(
                fontSize: 13,
                color: Colors.grey[700],
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            flex: 2,
            child: Text(
              '$username / $password',
              style: GoogleFonts.cairo(
                fontSize: 12,
                color: Colors.grey[600],
                fontFamily: 'monospace',
              ),
            ),
          ),
        ],
      ),
    );
  }
}
