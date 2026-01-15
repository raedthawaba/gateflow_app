import "package:flutter/material.dart";
import "package:go_router/go_router.dart";
import "package:font_awesome_flutter/font_awesome_flutter.dart";

import "../../../core/theme/app_theme.dart";

/// لوحة المراقبة الرئيسية
/// Main dashboard screen
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    DashboardContent(),
    GatesListScreen(),
    PermitsListScreen(),
    TravelersListScreen(),
    ScannerScreen(),
    AlertsListScreen(),
  ];

  final List<String> _titles = [
    "لوحة التحكم",
    "البوابات",
    "التصاريح",
    "المسافرين",
    "الماسح الضوئي",
    "التنبيهات",
  ];

  final List<IconData> _icons = [
    Icons.dashboard,
    Icons.gate,
    Icons.assignment,
    Icons.people,
    Icons.qr_code_scanner,
    Icons.notifications,
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_selectedIndex]),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              context.go("/login");
            },
          ),
        ],
      ),
      body: _screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        destinations: List.generate(
          _titles.length,
          (index) => NavigationDestination(
            icon: Icon(_icons[index]),
            label: _titles[index],
          ),
        ),
      ),
    );
  }
}

/// محتوى لوحة التحكم
/// Dashboard content
class DashboardContent extends StatelessWidget {
  const DashboardContent({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildWelcomeSection(),
          const SizedBox(height: 24),
          _buildStatisticsGrid(),
          const SizedBox(height: 24),
          _buildRecentActivitySection(),
        ],
      ),
    );
  }

  /// بناء قسم الترحيب
  Widget _buildWelcomeSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).colorScheme.primary,
            Theme.of(context).colorScheme.primaryContainer,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "مرحباً،",
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onPrimary,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            "مشرف النظام",
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: Theme.of(context).colorScheme.onPrimary,
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),
          Text(
            "هنا ملخص لحالة النظام اليوم",
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context)
                      .colorScheme
                      .onPrimary
                      .withOpacity(0.8),
                ),
          ),
        ],
      ),
    );
  }

  /// بناء شبكة الإحصائيات
  Widget _buildStatisticsGrid() {
    final statistics = [
      {"icon": Icons.gate, "label": "البوابات النشطة", "value": "12", "color": AppTheme.successColor},
      {"icon": Icons.assignment, "label": "تصاريح اليوم", "value": "45", "color": AppTheme.infoColor},
      {"icon": Icons.people, "label": "مسافرين حالياً", "value": "128", "color": AppTheme.warningColor},
      {"icon": Icons.notifications_active, "label": "تنبيهات جديدة", "value": "3", "color": AppTheme.errorColor},
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
      itemCount: statistics.length,
      itemBuilder: (context, index) {
        final stat = statistics[index];
        return _buildStatCard(
          context,
          stat["icon"] as IconData,
          stat["label"] as String,
          stat["value"] as String,
          stat["color"] as Color,
        );
      },
    );
  }

  /// بناء بطاقة إحصائية
  Widget _buildStatCard(
    BuildContext context,
    IconData icon,
    String label,
    String value,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color),
            ),
            const Spacer(),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  /// بناء قسم النشاط الأخير
  Widget _buildRecentActivitySection() {
    final activities = [
      {"title": "دخول مسافر - بوابة 1", "time": "منذ 5 دقائق", "icon": Icons.login, "color": AppTheme.successColor},
      {"title": "إنشاء تصريح جديد", "time": "منذ 15 دقيقة", "icon": Icons.add_circle, "color": AppTheme.infoColor},
      {"title": "تنبيه - تصريح منتهي", "time": "منذ 30 دقيقة", "icon": Icons.warning, "color": AppTheme.warningColor},
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "النشاط الأخير",
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
            const SizedBox(height: 16),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: activities.length,
              separatorBuilder: (context, index) => const Divider(),
              itemBuilder: (context, index) {
                final activity = activities[index];
                return ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: (activity["color"] as Color).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      activity["icon"] as IconData,
                      color: activity["color"] as Color,
                      size: 20,
                    ),
                  ),
                  title: Text(activity["title"] as String),
                  subtitle: Text(activity["time"] as String),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

/// شاشة قائمة البوابات (مؤقتة)
class GatesListScreen extends StatelessWidget {
  const GatesListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text("شاشة البوابات قيد التطوير"),
    );
  }
}

/// شاشة قائمة التصاريح (مؤقتة)
class PermitsListScreen extends StatelessWidget {
  const PermitsListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text("شاشة التصاريح قيد التطوير"),
    );
  }
}

/// شاشة قائمة المسافرين (مؤقتة)
class TravelersListScreen extends StatelessWidget {
  const TravelersListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text("شاشة المسافرين قيد التطوير"),
    );
  }
}

/// شاشة الماسح الضوئي (مؤقتة)
class ScannerScreen extends StatelessWidget {
  const ScannerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text("شاشة الماسح الضوئي قيد التطوير"),
    );
  }
}

/// شاشة التنبيهات (مؤقتة)
class AlertsListScreen extends StatelessWidget {
  const AlertsListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text("شاشة التنبيهات قيد التطوير"),
    );
  }
}
