import os

# Create directories
dirs = [
    "lib/dashboard",
    "lib/settings",
    "lib/gates",
    "lib/weapons",
    "assets/translations"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

# Create files
files = {
    "lib/dashboard/dashboard_screen.dart": '''import "package:flutter/material.dart";

class DashboardScreen extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(title: Text("لوحة المراقبة")),
            body: GridView.count(
                crossAxisCount: 2,
                padding: EdgeInsets.all(16),
                children: [
                    _buildStatCard("المسافرين اليوم", "0", Icons.people),
                    _buildStatCard("السندات النشطة", "0", Icons.card_membership),
                    _buildStatCard("التنبيهات", "0", Icons.notifications),
                    _buildStatCard("الكاميرات", "0", Icons.camera_alt),
                ],
            ),
        );
    }

    Widget _buildStatCard(String title, String value, IconData icon) {
        return Card(
            child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                    Icon(icon, size: 40, color: Color(0xFF1E3A8A)),
                    SizedBox(height: 8),
                    Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                    Text(title, style: TextStyle(color: Colors.grey)),
                ],
            ),
        );
    }
}
''',
    "lib/settings/settings_screen.dart": '''import "package:flutter/material.dart";

class SettingsScreen extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(title: Text("الإعدادات")),
            body: ListView(
                padding: EdgeInsets.all(16),
                children: [
                    ListTile(
                        leading: Icon(Icons.language),
                        title: Text("اللغة"),
                        subtitle: Text("العربية"),
                        onTap: () {},
                    ),
                    Divider(),
                    ListTile(
                        leading: Icon(Icons.info),
                        title: Text("حول التطبيق"),
                        subtitle: Text("GateFlow v1.0.0"),
                        onTap: () {},
                    ),
                ],
            ),
        );
    }
}
''',
    "lib/gates/gates_list_screen.dart": '''import "package:flutter/material.dart";

class GatesListScreen extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(title: Text("إدارة النقاط")),
            body: Center(
                child: Text("إدارة نقاط الدخول والخروج"),
            ),
            floatingActionButton: FloatingActionButton(
                onPressed: () {},
                child: Icon(Icons.add),
            ),
        );
    }
}
''',
    "lib/gates/gates_repository.dart": '''class GatesRepository {
    Future<List<dynamic>> getGates({int? cityId}) async {
        return [];
    }
}
''',
    "lib/weapons/weapons_list_screen.dart": '''import "package:flutter/material.dart";

class WeaponsListScreen extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(title: Text("إدارة الأسلحة")),
            body: Center(
                child: Text("إدارة الأسلحة الشخصية"),
            ),
            floatingActionButton: FloatingActionButton(
                onPressed: () {},
                child: Icon(Icons.add),
            ),
        );
    }
}
''',
    "lib/weapons/weapons_repository.dart": '''class WeaponsRepository {
    Future<List<dynamic>> getWeapons({int? travelerId}) async {
        return [];
    }
}
''',
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Created: {path}")

print("\\n✅ All remaining files created successfully!")
