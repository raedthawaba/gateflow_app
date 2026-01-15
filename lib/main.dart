import "package:flutter/material.dart";
import "package:flutter_localizations/flutter_localizations.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "core/theme/app_theme.dart";
import "features/auth/presentation/login_screen.dart";
import "features/dashboard/presentation/dashboard_screen.dart";
import "features/gates/presentation/gates_list_screen.dart";
import "features/permits/presentation/permits_list_screen.dart";
import "features/travelers/presentation/travelers_list_screen.dart";
import "features/scanner/presentation/scanner_screen.dart";
import "features/alerts/presentation/alerts_list_screen.dart";

void main() {
  runApp(const GateFlowApp());
}

class GateFlowApp extends StatelessWidget {
  const GateFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ProviderScope(
      child: MaterialApp.router(
        title: "GateFlow",
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale("ar", "EG"),
          Locale("en", "US"),
        ],
        locale: const Locale("ar", "EG"),
        debugShowCheckedModeBanner: false,
        routerConfig: GoRouter(
          initialLocation: "/login",
          routes: [
            GoRoute(
              path: "/login",
              name: "login",
              builder: (context, state) => const LoginScreen(),
            ),
            GoRoute(
              path: "/dashboard",
              name: "dashboard",
              builder: (context, state) => const DashboardScreen(),
            ),
            GoRoute(
              path: "/gates",
              name: "gates",
              builder: (context, state) => const GatesListScreen(),
            ),
            GoRoute(
              path: "/permits",
              name: "permits",
              builder: (context, state) => const PermitsListScreen(),
            ),
            GoRoute(
              path: "/travelers",
              name: "travelers",
              builder: (context, state) => const TravelersListScreen(),
            ),
            GoRoute(
              path: "/scanner",
              name: "scanner",
              builder: (context, state) => const ScannerScreen(),
            ),
            GoRoute(
              path: "/alerts",
              name: "alerts",
              builder: (context, state) => const AlertsListScreen(),
            ),
          ],
        ),
      ),
    );
  }
}
