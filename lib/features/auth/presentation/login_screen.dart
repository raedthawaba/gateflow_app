import "package:flutter/material.dart";
import "package:go_router/go_router.dart";
import "package:font_awesome_flutter/font_awesome_flutter.dart";

import "../../core/widgets/custom_input.dart";
import "../../core/widgets/custom_button.dart";

/// شاشة تسجيل الدخول
/// Login screen
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      // محاكاة تسجيل الدخول
      await Future.delayed(const Duration(seconds: 1));

      // في التطبيق الحقيقي، سيتم التحقق من البيانات مع الخادم
      if (_usernameController.text.isNotEmpty &&
          _passwordController.text.isNotEmpty) {
        if (mounted) {
          context.go("/dashboard");
        }
      } else {
        if (mounted) {
          _showError("بيانات الدخول غير صحيحة");
        }
      }
    } catch (e) {
      if (mounted) {
        _showError(e.toString());
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _buildLogo(),
                  const SizedBox(height: 48),
                  _buildTitle(),
                  const SizedBox(height: 8),
                  _buildSubtitle(),
                  const SizedBox(height: 32),
                  _buildUsernameField(),
                  const SizedBox(height: 16),
                  _buildPasswordField(),
                  const SizedBox(height: 24),
                  _buildLoginButton(),
                  const SizedBox(height: 24),
                  _buildVersionInfo(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// بناء الشعار
  Widget _buildLogo() {
    return Column(
      children: [
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primary,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Theme.of(context)
                    .colorScheme
                    .primary
                    .withOpacity(0.3),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: const Icon(
            Icons.security,
            size: 60,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          "GateFlow",
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: Theme.of(context).colorScheme.primary,
              ),
        ),
      ],
    );
  }

  /// بناء العنوان
  Widget _buildTitle() {
    return Text(
      "مرحباً بعودتك",
      textAlign: TextAlign.center,
      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
    );
  }

  /// بناء العنوان الفرعي
  Widget _buildSubtitle() {
    return Text(
      "سجل دخولك للوصول إلى النظام",
      textAlign: TextAlign.center,
      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
    );
  }

  /// بناء حقل اسم المستخدم
  Widget _buildUsernameField() {
    return CustomInput(
      label: "اسم المستخدم",
      hint: "أدخل اسم المستخدم",
      controller: _usernameController,
      keyboardType: TextInputType.text,
      prefixIcon: const Icon(Icons.person_outline),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return "اسم المستخدم مطلوب";
        }
        if (value.length < 3) {
          return "اسم المستخدم يجب أن يكون 3 أحرف على الأقل";
        }
        return null;
      },
    );
  }

  /// بناء حقل كلمة المرور
  Widget _buildPasswordField() {
    return CustomInput(
      label: "كلمة المرور",
      hint: "أدخل كلمة المرور",
      controller: _passwordController,
      keyboardType: TextInputType.text,
      obscureText: _obscurePassword,
      prefixIcon: const Icon(Icons.lock_outline),
      suffixIcon: IconButton(
        icon: Icon(
          _obscurePassword ? Icons.visibility_off : Icons.visibility,
        ),
        onPressed: () {
          setState(() {
            _obscurePassword = !_obscurePassword;
          });
        },
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return "كلمة المرور مطلوبة";
        }
        if (value.length < 6) {
          return "كلمة المرور يجب أن تكون 6 أحرف على الأقل";
        }
        return null;
      },
    );
  }

  /// بناء زر تسجيل الدخول
  Widget _buildLoginButton() {
    return CustomButton(
      text: "تسجيل الدخول",
      isLoading: _isLoading,
      onPressed: _handleLogin,
      icon: Icons.login,
    );
  }

  /// بناء معلومات الإصدار
  Widget _buildVersionInfo() {
    return Text(
      "الإصدار 1.0.0",
      textAlign: TextAlign.center,
      style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
    );
  }
}
