import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// إعدادات الثيم الخاصة بالنظام
class AppTheme {
  // ألوان النظام الرئيسية
  static const Color primaryColor = Color(0xFF1A237E); // أزرق عسكري داكن
  static const Color secondaryColor = Color(0xFF455A64); // رمادي معدني
  static const Color accentColor = Color(0xFFFFC107); // ذهبي للتحذيرات
  static const Color successColor = Color(0xFF4CAF50); // أخضر للنجاح
  static const Color errorColor = Color(0xFFF44336); // أحمر للأخطاء
  static const Color warningColor = Color(0xFFFF9800); // برتقالي للتحذيرات
  static const Color infoColor = Color(0xFF2196F3); // أزرق للمعلومات

  // ألوان الأقسام
  static const Color armamentColor = Color(0xFFB71C1C); // أحمر للتسليح
  static const Color supplyColor = Color(0xFF2E7D32); // أخضر للامداد
  static const Color technicalColor = Color(0xFF1565C0); // أزرق للشعبة الفنية
  static const Color hrColor = Color(0xFF6A1B9A); // بنفسجي للبشرية

  // الثيم الفاتح
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        primary: primaryColor,
        secondary: secondaryColor,
        tertiary: accentColor,
        error: errorColor,
        surface: Colors.grey[50]!,
        onSurface: Colors.grey[900]!,
      ),
      scaffoldBackgroundColor: Colors.grey[50],
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
      ),
      drawerTheme: DrawerThemeData(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
      ),
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        surfaceTintColor: Colors.white,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(
            horizontal: 24,
            vertical: 12,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: GoogleFonts.cairo(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryColor,
          padding: const EdgeInsets.symmetric(
            horizontal: 24,
            vertical: 12,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: GoogleFonts.cairo(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryColor,
          textStyle: GoogleFonts.cairo(
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Colors.grey300),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Colors.grey300),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: primaryColor, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: errorColor),
        ),
        labelStyle: GoogleFonts.cairo(
          color: Colors.grey[700],
        ),
        hintStyle: GoogleFonts.cairo(
          color: Colors.grey[500],
        ),
      ),
      textTheme: GoogleFonts.cairoTextTheme(),
      dividerTheme: const DividerThemeData(
        color: Colors.grey200,
        thickness: 1,
      ),
    );
  }

  // الثيم الداكن
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        primary: primaryColor,
        secondary: secondaryColor,
        tertiary: accentColor,
        error: errorColor,
        surface: Colors.grey[900]!,
        onSurface: Colors.grey[100]!,
        brightness: Brightness.dark,
      ),
      scaffoldBackgroundColor: Colors.grey[900],
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
      ),
      drawerTheme: DrawerThemeData(
        backgroundColor: Colors.grey[850],
        surfaceTintColor: Colors.grey[850],
      ),
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        surfaceTintColor: Colors.grey[850],
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(
            horizontal: 24,
            vertical: 12,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: GoogleFonts.cairo(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryColor,
          padding: const EdgeInsets.symmetric(
            horizontal: 24,
            vertical: 12,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: GoogleFonts.cairo(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryColor,
          textStyle: GoogleFonts.cairo(
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.grey[800],
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Colors.grey600),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Colors.grey600),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: primaryColor, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: errorColor),
        ),
        labelStyle: GoogleFonts.cairo(
          color: Colors.grey[400],
        ),
        hintStyle: GoogleFonts.cairo(
          color: Colors.grey[500],
        ),
      ),
      textTheme: GoogleFonts.cairoTextTheme(ThemeData.dark().textTheme),
      dividerTheme: const DividerThemeData(
        color: Colors.grey700,
        thickness: 1,
      ),
    );
  }

  /// دالة مساعدة للحصول على لون القسم
  static Color getDepartmentColor(String department) {
    switch (department.toLowerCase()) {
      case 'armament':
      case 'تسليح':
        return armamentColor;
      case 'supply':
      case 'امداد':
        return supplyColor;
      case 'technical':
      case 'تقني':
        return technicalColor;
      case 'human_resources':
      case 'بشرية':
        return hrColor;
      default:
        return primaryColor;
    }
  }

  /// دالة مساعدة للحصول على أيقونة القسم
  static IconData getDepartmentIcon(String department) {
    switch (department.toLowerCase()) {
      case 'armament':
      case 'تسليح':
        return Icons.security;
      case 'supply':
      case 'امداد':
        return Icons.inventory_2;
      case 'technical':
      case 'تقني':
        return Icons.build;
      case 'human_resources':
      case 'بشرية':
        return Icons.people;
      default:
        return Icons.dashboard;
    }
  }
}

/// إضافة Extensions مفيدة
extension ThemeExtension on BuildContext {
  ThemeData get theme => Theme.of(this);
  Color get primaryColor => theme.colorScheme.primary;
  Color get secondaryColor => theme.colorScheme.secondary;
  Color get errorColor => theme.colorScheme.error;
  TextTheme get textTheme => theme.textTheme;
}
