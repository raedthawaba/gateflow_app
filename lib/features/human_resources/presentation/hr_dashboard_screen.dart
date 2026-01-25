import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/custom_button.dart';
import '../../../core/services/auth_service.dart';

/// لوحة تحكم قسم البشرية
class HRDashboardScreen extends ConsumerWidget {
  const HRDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'قسم البشرية',
          style: GoogleFonts.cairo(),
        ),
        centerTitle: true,
        backgroundColor: AppTheme.hrColor,
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

            // قسم الإجراءات السريعة
            _buildSectionTitle('الإجراءات السريعة'),
            const SizedBox(height: 12),
            _buildQuickActions(context),
            const SizedBox(height: 24),

            // قسم إدارة الأفراد
            _buildSectionTitle('إدارة الأفراد'),
            const SizedBox(height: 12),
            _buildHRManagementCards(context),
            const SizedBox(height: 24),

            // قسم الإحصائيات
            _buildSectionTitle('إحصائيات القسم'),
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
                color: AppTheme.hrColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.people,
                size: 32,
                color: AppTheme.hrColor,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'مرحباً، ${user?.name ?? 'مسؤول البشرية'}',
                    style: GoogleFonts.cairo(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user?.rank ?? 'رائد',
                    style: GoogleFonts.cairo(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                  Text(
                    'قسم البشرية',
                    style: GoogleFonts.cairo(
                      fontSize: 13,
                      color: AppTheme.hrColor,
                      fontWeight: FontWeight.w500,
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

  /// بناء الإجراءات السريعة
  Widget _buildQuickActions(BuildContext context) {
    final actions = [
      {'title': 'إضافة فرد', 'icon: Icons.person_add', 'color': Colors.green},
      {'title': 'إجازات', 'icon': Icons.beach_access, 'color': Colors.blue},
      {'title': 'ترقيات', 'icon: Icons.trending_up', 'color': Colors.orange},
      {'title': 'تقارير', 'icon: Icons.assessment', 'color: Colors.purple},
    ];

    return Row(
      children: actions.map((action) {
        return Expanded(
          child: Card(
            elevation: 1,
            margin: const EdgeInsets.symmetric(horizontal: 4),
            child: InkWell(
              onTap: () {},
              borderRadius: BorderRadius.circular(12),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  children: [
                    Icon(
                      action['icon'] as IconData,
                      size: 28,
                      color: action['color'] as Color,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      action['title'] as String,
                      style: GoogleFonts.cairo(
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  /// بناء بطاقات إدارة الأفراد
  Widget _buildHRManagementCards(BuildContext context) {
    final cards = [
      {'title': 'الضباط', 'subtitle: 'القادة والضباط', 'count': '85 ضابط', 'icon: Icons.military_tech},
      {'title': 'الجنود', 'subtitle: 'الجنود النظاميين', 'count': '420 جندي', 'icon: Icons.groups},
      {'title': 'الموظفون', 'subtitle: 'الموظفون المدنيون', 'count': '65 موظف', 'icon: Icons.badge},
      {'title': 'الوحدات', 'subtitle: 'الوحدات العسكرية', 'count': '12 وحدة', 'icon: Icons.location_city},
    ];

    return Column(
      children: cards.map((card) {
        return Card(
          elevation: 2,
          margin: const EdgeInsets.symmetric(vertical: 6),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: InkWell(
            onTap: () {},
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppTheme.hrColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      card['icon'] as IconData,
                      size: 26,
                      color: AppTheme.hrColor,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          card['title'] as String,
                          style: GoogleFonts.cairo(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          card['subtitle'] as String,
                          style: GoogleFonts.cairo(
                            fontSize: 13,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: AppTheme.hrColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      card['count'] as String,
                      style: GoogleFonts.cairo(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.hrColor,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  /// بناء شبكة الإحصائيات
  Widget _buildStatsGrid(BuildContext context) {
    final stats = [
      {'title': 'إجمالي الأفراد', 'value': '570', 'icon': Icons.people, 'color': AppTheme.hrColor},
      {'title': 'إجازات', 'value': '23', 'icon': Icons.beach_access, 'color': Colors.orange},
      {'title': 'مهام خاصة', 'value': '8', 'icon: Icons.assignment', 'color': Colors.blue},
      {'title': 'طلبات جديدة', 'value': '12', 'icon: Icons.notification_add', 'color': Colors.green},
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.4,
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
                  size: 26,
                  color: stat['color'] as Color,
                ),
                const SizedBox(height: 8),
                Text(
                  stat['value'] as String,
                  style: GoogleFonts.cairo(
                    fontSize: 22,
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
          Container(
            padding: const EdgeInsets.only(
              top: 60,
              right: 16,
              left: 16,
              bottom: 20,
            ),
            decoration: const BoxDecoration(
              color: AppTheme.hrColor,
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
                    Icons.people,
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
                        authState.user?.name ?? 'مسؤول البشرية',
                        style: GoogleFonts.cairo(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        'قسم البشرية',
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
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              children: [
                _buildDrawerItem(
                  context: context,
                  icon: Icons.dashboard,
                  title: 'الرئيسية',
                  route: '/human_resources',
                  isSelected: true,
                ),
                const Divider(height: 1),
                _buildDrawerHeader('إدارة الأفراد'),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.military_tech,
                  title: 'الضباط',
                  route: '/human_resources/officers',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.groups,
                  title: 'الجنود',
                  route: '/human_resources/soldiers',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.badge,
                  title: 'الموظفون',
                  route: '/human_resources/civilians',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.location_city,
                  title: 'الوحدات',
                  route: '/human_resources/units',
                ),
                const Divider(height: 1),
                _buildDrawerHeader('العمليات'),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.person_add,
                  title: 'إضافة فرد',
                  route: '/human_resources/add',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.beach_access,
                  title: 'الإجازات',
                  route: '/human_resources/leaves',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.assignment,
                  title: 'التقارير',
                  route: '/human_resources/reports',
                ),
              ],
            ),
          ),
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

  Widget _buildDrawerItem({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String route,
    bool isSelected = false,
  }) {
    return ListTile(
      leading: Icon(
        icon,
        color: isSelected ? AppTheme.hrColor : Colors.grey[700],
      ),
      title: Text(
        title,
        style: GoogleFonts.cairo(
          fontSize: 14,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
          color: isSelected ? AppTheme.hrColor : Colors.grey[800],
        ),
      ),
      selected: isSelected,
      selectedTileColor: AppTheme.hrColor.withOpacity(0.1),
      onTap: () {
        context.go(route);
        Navigator.pop(context);
      },
    );
  }

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

  void _showLogoutDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('تسجيل الخروج', style: GoogleFonts.cairo()),
        content: Text('هل أنت متأكد من تسجيل الخروج؟', style: GoogleFonts.cairo()),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('إلغاء', style: GoogleFonts.cairo()),
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
            child: Text('تسجيل الخروج', style: GoogleFonts.cairo()),
          ),
        ],
      ),
    );
  }
}
