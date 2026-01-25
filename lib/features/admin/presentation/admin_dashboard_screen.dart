import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/custom_button.dart';
import '../../../core/services/auth_service.dart';

/// لوحة تحكم المسؤول - تعرض جميع الأقسام
class AdminDashboardScreen extends ConsumerWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'لوحة تحكم المسؤول',
          style: GoogleFonts.cairo(),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            onPressed: () => _showLogoutDialog(context, ref),
            icon: const Icon(Icons.logout),
            tooltip: 'تسجيل الخروج',
          ),
        ],
      ),
      drawer: _buildDrawer(context, ref),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // بطاقة الترحيب
            _buildWelcomeCard(context, authState.user),
            const SizedBox(height: 24),

            // قسم الأقسام
            _buildSectionTitle('إدارة الأقسام'),
            const SizedBox(height: 12),

            // بطاقات الأقسام
            _buildDepartmentCard(
              context: context,
              title: 'قسم التسليح',
              subtitle: 'إدارة الأسلحة والمعدات العسكرية',
              icon: Icons.security,
              color: AppTheme.armamentColor,
              onTap: () => context.go('/admin/armament'),
            ),
            _buildDepartmentCard(
              context: context,
              title: 'قسم الامداد',
              subtitle: 'إدارة التوريد والتموين',
              icon: Icons.inventory_2,
              color: AppTheme.supplyColor,
              onTap: () => context.go('/admin/supply'),
            ),
            _buildDepartmentCard(
              context: context,
              title: 'الشعبة الفنية',
              subtitle: 'الصيانة والدعم الفني',
              icon: Icons.build,
              color: AppTheme.technicalColor,
              onTap: () => context.go('/admin/technical'),
            ),
            _buildDepartmentCard(
              context: context,
              title: 'قسم البشرية',
              subtitle: 'إدارة الموارد البشرية',
              icon: Icons.people,
              color: AppTheme.hrColor,
              onTap: () => context.go('/admin/human_resources'),
            ),
            const SizedBox(height: 24),

            // قسم الإحصائيات
            _buildSectionTitle('الإحصائيات العامة'),
            const SizedBox(height: 12),
            _buildStatsGrid(context),
          ],
        ),
      ),
    );
  }

  /// بناء بطاقة الترحيب
  Widget _buildWelcomeCard(BuildContext context, User? user) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.admin_panel_settings,
                size: 32,
                color: AppTheme.primaryColor,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'مرحباً، ${user?.name ?? 'المسؤول'}',
                    style: GoogleFonts.cairo(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user?.rank ?? 'عقيد',
                    style: GoogleFonts.cairo(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                  Text(
                    user?.department ?? 'الإدارة العامة',
                    style: GoogleFonts.cairo(
                      fontSize: 13,
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// بناء عنوان القسم
  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(right: 4),
      child: Text(
        title,
        style: GoogleFonts.cairo(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: Colors.grey[800],
        ),
      ),
    );
  }

  /// بناء بطاقة القسم
  Widget _buildDepartmentCard({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  size: 28,
                  color: color,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: GoogleFonts.cairo(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: GoogleFonts.cairo(
                        fontSize: 13,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                size: 18,
                color: Colors.grey[400],
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// بناء شبكة الإحصائيات
  Widget _buildStatsGrid(BuildContext context) {
    final stats = [
      {'title': 'إجمالي المستخدمين', 'value': '156', 'icon': Icons.people, 'color': Colors.blue},
      {'title': 'الطلبات المعلقة', 'value': '23', 'icon': Icons.pending_actions, 'color': Colors.orange},
      {'title': 'التنبيهات الجديدة', 'value': '7', 'icon': Icons.notifications, 'color': Colors.red},
      {'title': 'العمليات اليوم', 'value': '89', 'icon': Icons.assessment, 'color': Colors.green},
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: stats.length,
      itemBuilder: (context, index) {
        final stat = stats[index];
        return Card(
          elevation: 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  stat['icon'] as IconData,
                  size: 28,
                  color: stat['color'] as Color,
                ),
                const SizedBox(height: 8),
                Text(
                  stat['value'] as String,
                  style: GoogleFonts.cairo(
                    fontSize: 24,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  stat['title'] as String,
                  style: GoogleFonts.cairo(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  /// بناء القائمة الجانبية
  Widget _buildDrawer(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return Drawer(
      child: Column(
        children: [
          // رأس القائمة
          Container(
            padding: const EdgeInsets.only(
              top: 60,
              right: 16,
              left: 16,
              bottom: 20,
            ),
            decoration: BoxDecoration(
              color: AppTheme.primaryColor,
            ),
            child: Row(
              children: [
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.admin_panel_settings,
                    color: Colors.white,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        authState.user?.name ?? 'المسؤول',
                        style: GoogleFonts.cairo(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        authState.user?.email ?? 'admin@military.system',
                        style: GoogleFonts.cairo(
                          fontSize: 12,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // قائمة الأقسام
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              children: [
                _buildDrawerItem(
                  context: context,
                  icon: Icons.dashboard,
                  title: 'الرئيسية',
                  route: '/admin',
                  isSelected: true,
                ),
                const Divider(height: 1),
                _buildDrawerHeader('الأقسام'),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.security,
                  title: 'قسم التسليح',
                  route: '/admin/armament',
                  color: AppTheme.armamentColor,
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.inventory_2,
                  title: 'قسم الامداد',
                  route: '/admin/supply',
                  color: AppTheme.supplyColor,
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.build,
                  title: 'الشعبة الفنية',
                  route: '/admin/technical',
                  color: AppTheme.technicalColor,
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.people,
                  title: 'قسم البشرية',
                  route: '/admin/human_resources',
                  color: AppTheme.hrColor,
                ),
                const Divider(height: 1),
                _buildDrawerHeader('الإعدادات'),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.settings,
                  title: 'الإعدادات',
                  route: '/admin/settings',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.analytics,
                  title: 'التقارير',
                  route: '/admin/reports',
                ),
              ],
            ),
          ),

          // زر تسجيل الخروج
          Padding(
            padding: const EdgeInsets.all(16),
            child: CustomButton(
              text: 'تسجيل الخروج',
              onPressed: () => _showLogoutDialog(context, ref),
              backgroundColor: Colors.red[50],
              foregroundColor: Colors.red,
            ),
          ),
        ],
      ),
    );
  }

  /// بناء عنصر القائمة
  Widget _buildDrawerItem({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String route,
    Color? color,
    bool isSelected = false,
  }) {
    return ListTile(
      leading: Icon(
        icon,
        color: isSelected
            ? AppTheme.primaryColor
            : color ?? Colors.grey[700],
      ),
      title: Text(
        title,
        style: GoogleFonts.cairo(
          fontSize: 14,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
          color: isSelected
              ? AppTheme.primaryColor
              : Colors.grey[800],
        ),
      ),
      selected: isSelected,
      selectedTileColor: AppTheme.primaryColor.withOpacity(0.1),
      onTap: () {
        context.go(route);
        Navigator.pop(context);
      },
    );
  }

  /// بناء رأس القائمة
  Widget _buildDrawerHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(
        top: 16,
        right: 16,
        bottom: 8,
        left: 16,
      ),
      child: Text(
        title,
        style: GoogleFonts.cairo(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: Colors.grey[500],
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  /// عرض مربع حوار تسجيل الخروج
  void _showLogoutDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'تسجيل الخروج',
          style: GoogleFonts.cairo(),
        ),
        content: Text(
          'هل أنت متأكد من تسجيل الخروج؟',
          style: GoogleFonts.cairo(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'إلغاء',
              style: GoogleFonts.cairo(),
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              await logout(ref);
              context.go('/login');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: Text(
              'تسجيل الخروج',
              style: GoogleFonts.cairo(),
            ),
          ),
        ],
      ),
    );
  }
}
