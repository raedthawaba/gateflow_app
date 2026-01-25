import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/custom_button.dart';
import '../../../core/services/auth_service.dart';

/// لوحة تحكم قسم الامداد
class SupplyDashboardScreen extends ConsumerWidget {
  const SupplyDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'قسم الامداد',
          style: GoogleFonts.cairo(),
        ),
        centerTitle: true,
        backgroundColor: AppTheme.supplyColor,
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

            // قسم إدارة التموين
            _buildSectionTitle('إدارة التموين'),
            const SizedBox(height: 12),
            _buildSupplyManagementCards(context),
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
                color: AppTheme.supplyColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.inventory_2,
                size: 32,
                color: AppTheme.supplyColor,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'مرحباً، ${user?.name ?? 'مسؤول الامداد'}',
                    style: GoogleFonts.cairo(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user?.rank ?? 'مقدم',
                    style: GoogleFonts.cairo(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                  Text(
                    'قسم الامداد',
                    style: GoogleFonts.cairo(
                      fontSize: 13,
                      color: AppTheme.supplyColor,
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
      {'title': 'إضافة صنف', 'icon': Icons.add_box, 'color': Colors.green},
      {'title': 'طلب توريد', 'icon': Icons.shopping_cart, 'color': Colors.blue},
      {'title': 'صرف', 'icon': Icons.point_of_sale, 'color': Colors.orange},
      {'title': 'جرد', 'icon': Icons.inventory, 'color': Colors.purple},
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

  /// بناء بطاقات إدارة التموين
  Widget _buildSupplyManagementCards(BuildContext context) {
    final cards = [
      {'title': 'المواد الغذائية', 'subtitle': 'المؤن والطعام', 'count': '45 صنف', 'icon': Icons.restaurant},
      {'title': 'المواد الطبية', 'subtitle': 'الأدوية والمستلزمات', 'count': '120 صنف', 'icon': Icons.medical_services},
      {'title': 'الوقود', subtitle: 'البنزين والديزل', 'count: '5,000 لتر', 'icon': Icons.local_gas_station},
      {'title': 'قطع الغيار', subtitle: 'مستلزمات المركبات', 'count': '340 صنف', 'icon': Icons.settings},
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
                      color: AppTheme.supplyColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      card['icon'] as IconData,
                      size: 26,
                      color: AppTheme.supplyColor,
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
                      color: AppTheme.supplyColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      card['count'] as String,
                      style: GoogleFonts.cairo(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.supplyColor,
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
      {'title': 'إجمالي الأصناف', 'value': '510', 'icon': Icons.category, 'color': AppTheme.supplyColor},
      {'title': 'طلبات معلقة', 'value': '18', 'icon': Icons.pending_actions, 'color': Colors.orange},
      {'title': ' منخفض المخزون', 'value': '12', 'icon': Icons.warning, 'color': Colors.red},
      {'title': 'عمليات اليوم', 'value': '25', 'icon': Icons.swap_horiz, 'color': Colors.green},
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
              color: AppTheme.supplyColor,
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
                    Icons.inventory_2,
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
                        authState.user?.name ?? 'مسؤول الامداد',
                        style: GoogleFonts.cairo(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        'قسم الامداد',
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
                  route: '/supply',
                  isSelected: true,
                ),
                const Divider(height: 1),
                _buildDrawerHeader('إدارة المخزون'),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.restaurant,
                  title: 'المواد الغذائية',
                  route: '/supply/food',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.medical_services,
                  title: 'المواد الطبية',
                  route: '/supply/medical',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.local_gas_station,
                  title: 'الوقود',
                  route: '/supply/fuel',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.settings,
                  title: 'قطع الغيار',
                  route: '/supply/spare',
                ),
                const Divider(height: 1),
                _buildDrawerHeader('العمليات'),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.shopping_cart,
                  title: 'الطلبات',
                  route: '/supply/orders',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.inventory,
                  title: 'الجرد',
                  route: '/supply/inventory',
                ),
                _buildDrawerItem(
                  context: context,
                  icon: Icons.assignment,
                  title: 'التقارير',
                  route: '/supply/reports',
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
        color: isSelected ? AppTheme.supplyColor : Colors.grey[700],
      ),
      title: Text(
        title,
        style: GoogleFonts.cairo(
          fontSize: 14,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
          color: isSelected ? AppTheme.supplyColor : Colors.grey[800],
        ),
      ),
      selected: isSelected,
      selectedTileColor: AppTheme.supplyColor.withOpacity(0.1),
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
