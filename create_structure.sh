#!/bin/bash

# ============================================
# سكريبت إنشاء الهيكل الكامل لمشروع GateFlow
# ============================================

set -e  # Exit on error

echo "=========================================="
echo "  إنشاء هيكل مشروع GateFlow"
echo "=========================================="

# دالة لإنشاء ملف
create_file() {
    local filepath="$1"
    local content="$2"
    local dir=$(dirname "$filepath")
    
    # إنشاء المجلد إذا لم يوجد
    mkdir -p "$dir"
    
    # إنشاء الملف
    echo "$content" > "$filepath"
    
    echo "✓ تم إنشاء: $filepath"
}

# الدليل الرئيسي
BASE_DIR="/workspace"

# ============================================
# مجلدات المنصات (Android, iOS, Web)
# ============================================

echo ""
echo "جاري إنشاء ملفات Android..."

# Android Manifest
create_file "$BASE_DIR/android/app/src/main/AndroidManifest.xml" '<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.gateflow">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <application
        android:name=".MainApplication"
        android:label="GateFlow"
        android:icon="@mipmap/ic_launcher">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>'

create_file "$BASE_DIR/android/app/src/debug/AndroidManifest.xml" '<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.gateflow">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application android:debuggable="true"/>
</manifest>'

# Kotlin MainActivity
create_file "$BASE_DIR/android/app/src/main/kotlin/com/gateflow/MainActivity.kt" 'package com.gateflow

import io.flutter.embedding.android.FlutterActivity

class MainActivity: FlutterActivity()'

create_file "$BASE_DIR/android/app/src/main/res/values/strings.xml" '<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">GateFlow</string>
</resources>'

create_file "$BASE_DIR/android/app/src/main/res/values/colors.xml" '<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="primary">#1E3A8A</color>
    <color name="secondary">#64748B</color>
</resources>'

create_file "$BASE_DIR/android/app/src/main/res/values/themes.xml" '<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="LaunchTheme" parent="@android:style/Theme.Light.NoTitleBar">
        <item name="android:windowBackground">@color/primary</item>
    </style>
</resources>'

# Android Gradle files
create_file "$BASE_DIR/android/build.gradle.kts" 'buildscript {
    ext.kotlin_version = "1.9.0"
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:8.1.0")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version")
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

tasks.register("clean", Delete::class) {
    delete(rootProject.layout.buildDirectory)
}'

create_file "$BASE_DIR/android/app/build.gradle.kts" 'plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
}

def localProperties = new Properties()
def localPropertiesFile = rootProject.file("local.properties")
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader("UTF-8") { reader -> localProperties.load(reader) }
}

def flutterVersionCode = localProperties.getProperty("flutter.versionCode")
def flutterVersionName = localProperties.getProperty("flutter.versionName")

android {
    namespace = "com.gateflow"
    compileSdk = 34
    ndkVersion = "25.2.9519653"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }

    sourceSets {
        main.java.srcDirs += "src/main/kotlin"
    }

    defaultConfig {
        applicationId = "com.gateflow"
        minSdk = 21
        targetSdk = 34
        versionCode = flutterVersionCode.toInteger()
        versionName = flutterVersionName
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.debug
        }
    }

    flutter {
        source = "../.."
    }
}

dependencies {}'

create_file "$BASE_DIR/android/settings.gradle.kts" 'pluginManagement {
    def flutterSdkPath = {
        def properties = new Properties()
        file("local.properties").withInputStream { properties.load(it) }
        def flutterSdkPath = properties.getProperty("flutter.sdk")
        assert flutterSdkPath != null
        return flutterSdkPath
    }()

    include(":app")
    dependencyGraph()
}'

create_file "$BASE_DIR/android/gradle.properties" 'org.gradle.jvmargs=-Xmx4G
android.useAndroidX=true
android.enableJetifier=true'

# iOS
echo ""
echo "جاري إنشاء ملفات iOS..."

create_file "$BASE_DIR/ios/Runner/AppDelegate.swift" 'import UIKit
import Flutter

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
    override func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        GeneratedPluginRegistrant.register(with: self)
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }
}'

create_file "$BASE_DIR/ios/Runner/Info.plist" '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>$(DEVELOPMENT_LANGUAGE)</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>gateflow</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$(FLUTTER_BUILD_NAME)</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleVersion</key>
    <string>$(FLUTTER_BUILD_NUMBER)</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UILaunchStoryboardName</key>
    <string>LaunchScreen</string>
    <key>UIMainStoryboardFile</key>
    <string>LaunchScreen</string>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>'

create_file "$BASE_DIR/ios/Runner/Runner-Bridging-Header.h" '//
//  Runner-Bridging-Header.h
//  GateFlow
//

#ifndef Runner_Bridging_Header_h
#define Runner_Bridging_Header_h

#import "GeneratedPluginRegistrant.h"

#endif /* Runner_Bridging_Header_h */'

create_file "$BASE_DIR/ios/Podfile" 'platform :ios, "12.0"

target "Runner" do
    use_frameworks!
    use_modular_headers!
end

post_install do |installer|
    installer.pods_project.targets.each do |target|
        target.build_configurations.each do |config|
            config.build_settings["IPHONEOS_DEPLOYMENT_TARGET"] = "12.0"
        end
    end
end'

create_file "$BASE_DIR/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json" '{
  "images" : [
    {
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}'

create_file "$BASE_DIR/ios/Runner/Assets.xcassets/LaunchImage.imageset/Contents.json" '{
  "images" : [
    {
      "idiom" : "universal",
      "scale" : "1x"
    },
    {
      "idiom" : "universal",
      "scale" : "2x"
    },
    {
      "idiom" : "universal",
      "scale" : "3x"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}'

# Web
echo ""
echo "جاري إنشاء ملفات Web..."

create_file "$BASE_DIR/web/index.html" '<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GateFlow</title>
    <base href="/">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="manifest" href="manifest.json">
</head>
<body>
    <script src="flutter.js" defer></script>
    <script>
        window.addEventListener("load", function(ev) {
            _flutter.loader.loadEntrypoint({
                onEntrypointLoaded: function(engineInitializer) {
                    engineInitializer.initializeApp().then(function(appRunner) {
                        appRunner.runApp();
                    });
                }
            });
        });
    </script>
</body>
</html>'

create_file "$BASE_DIR/web/manifest.json" '{
    "name": "GateFlow",
    "short_name": "GateFlow",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#1E3A8A",
    "theme_color": "#1E3A8A",
    "icons": []
}'

echo ""
echo "جاري إنشاء ملفات Flutter lib..."

# ============================================
# ملفات Flutter الرئيسية
# ============================================

create_file "$BASE_DIR/lib/main.dart" 'import "package:flutter/material.dart";
import "package:flutter_localizations/flutter_localizations.dart";
import "package:flutter_bloc/flutter_bloc.dart";

import "core/config/app_config.dart";
import "gateflow_app.dart";

void main() async {
    WidgetsFlutterBinding.ensureInitialized();
    await AppConfig.initialize();
    runApp(GateFlowApp());
}'

create_file "$BASE_DIR/lib/gateflow_app.dart" 'import "package:flutter/material.dart";
import "package:flutter_localizations/flutter_localizations.dart";
import "package:flutter_bloc/flutter_bloc.dart";

import "core/config/app_config.dart";
import "routes.dart";
import "theme.dart";

class GateFlowApp extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return MultiBlocProvider(
            providers: [],
            child: MaterialApp(
                title: AppConfig.appName,
                theme: AppTheme.lightTheme,
                darkTheme: AppTheme.darkTheme,
                themeMode: ThemeMode.system,
                localizationsDelegates: [
                    GlobalMaterialLocalizations.delegate,
                    GlobalWidgetsLocalizations.delegate,
                    GlobalCupertinoLocalizations.delegate,
                ],
                supportedLocales: AppConfig.supportedLocales,
                locale: AppConfig.defaultLocale,
                initialRoute: Routes.login,
                onGenerateRoute: Routes.generateRoute,
                debugShowCheckedModeBanner: false,
            ),
        );
    }
}'

create_file "$BASE_DIR/lib/routes.dart" 'import "package:flutter/material.dart";
import "core/guards/auth_guard.dart";

class Routes {
    static const String login = "/login";
    static const String dashboard = "/dashboard";
    static const String travelers = "/travelers";
    static const String permits = "/permits";
    static const String scanner = "/scanner";
    static const String cameras = "/cameras";
    static const String alerts = "/alerts";
    static const String reports = "/reports";
    static const String settings = "/settings";

    static Route<dynamic> generateRoute(RouteSettings settings) {
        final args = settings.arguments;
        
        switch (settings.name) {
            case Routes.login:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("شاشة تسجيل الدخول"));
            case Routes.dashboard:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("لوحة المراقبة"));
            case Routes.travelers:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("إدارة المسافرين"));
            case Routes.permits:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("إدارة السندات"));
            case Routes.scanner:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("الماسح الضوئي"));
            case Routes.cameras:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("الكاميرات"));
            case Routes.alerts:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("التنبيهات"));
            case Routes.reports:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("التقارير"));
            case Routes.settings:
                return MaterialPageRoute(builder: (_) => PlaceholderScreen("الإعدادات"));
            default:
                return MaterialPageRoute(
                    builder: (_) => Scaffold(
                        body: Center(child: Text("الصفحة غير موجودة: \${settings.name}")),
                    ),
                );
        }
    }
}

class PlaceholderScreen extends StatelessWidget {
    final String title;
    
    const PlaceholderScreen(this.title);
    
    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(title: Text(title)),
            body: Center(
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                        Icon(Icons.construction, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text(title, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                        SizedBox(height: 8),
                        Text("هذه الشاشة قيد التطوير", style: TextStyle(color: Colors.grey)),
                    ],
                ),
            ),
        );
    }
}'

create_file "$BASE_DIR/lib/theme.dart" 'import "package:flutter/material.dart";

class AppTheme {
    static const Color primaryColor = Color(0xFF1E3A8A);
    static const Color secondaryColor = Color(0xFF64748B);
    static const Color successColor = Color(0xFF059669);
    static const Color dangerColor = Color(0xFFDC2626);
    static const Color warningColor = Color(0xFFD97706);

    static final ThemeData lightTheme = ThemeData(
        primaryColor: primaryColor,
        scaffoldBackgroundColor: Colors.grey[50],
        colorScheme: ColorScheme.fromSeed(
            seedColor: primaryColor,
            primary: primaryColor,
            secondary: secondaryColor,
        ),
        appBarTheme: AppBarTheme(
            backgroundColor: primaryColor,
            foregroundColor: Colors.white,
            elevation: 0,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
                backgroundColor: primaryColor,
                foregroundColor: Colors.white,
            ),
        ),
        inputDecorationTheme: InputDecorationTheme(
            border: OutlineInputBorder(),
            focusedBorder: OutlineInputBorder(
                borderSide: BorderSide(color: primaryColor, width: 2),
            ),
        ),
        useMaterial3: true,
    );

    static final ThemeData darkTheme = ThemeData(
        primaryColor: primaryColor,
        scaffoldBackgroundColor: Colors.grey[900],
        colorScheme: ColorScheme.fromSeed(
            seedColor: primaryColor,
            primary: primaryColor,
            secondary: secondaryColor,
            brightness: Brightness.dark,
        ),
        appBarTheme: AppBarTheme(
            backgroundColor: Colors.grey[800],
            foregroundColor: Colors.white,
        ),
        useMaterial3: true,
    );
}'

create_file "$BASE_DIR/lib/constants.dart" 'class AppConstants {
    // API
    static const String apiBaseUrl = "http://localhost:8000/api/v1";
    static const int connectionTimeout = 30000;
    static const int receiveTimeout = 30000;

    // Session
    static const Duration sessionTimeout = Duration(hours: 8);
    static const Duration tokenRefreshThreshold = Duration(minutes: 5);

    // Sync
    static const Duration syncInterval = Duration(minutes: 5);
    static const int maxRetryAttempts = 3;

    // QR Code
    static const int qrErrorCorrectionLevel = 2;
    static const int qrImageSize = 256;

    // Cache
    static const int maxCachedPermits = 1000;
    static const int maxCachedTravelers = 5000;
    static const int maxCachedWanted = 10000;

    // Pagination
    static const int defaultPageSize = 20;
    static const int maxPageSize = 100;

    // Validation
    static const int nationalIdMinLength = 7;
    static const int nationalIdMaxLength = 20;
    static const int phoneMinLength = 9;
    static const int phoneMaxLength = 15;
    static const int nameMinLength = 3;
    static const int nameMaxLength = 200;

    // Time limits
    static const int minPermitDurationHours = 1;
    static const int maxPermitDurationHours = 72;
    static const int expiryGracePeriodMinutes = 30;
}'

# ============================================
# ملفات Core
# ============================================

echo ""
echo "جاري إنشاء ملفات Core..."

# Config
create_file "$BASE_DIR/lib/core/config/app_config.dart" 'import "package:flutter/material.dart";
import "package:flutter/services.dart";

class AppConfig {
    static const String appName = "GateFlow";
    static const String appVersion = "1.0.0";
    static const String appBuildNumber = "1";

    static const String baseUrl = "http://localhost:8000/api/v1";
    static const int connectionTimeout = 30000;
    static const int receiveTimeout = 30000;

    static const Duration sessionTimeout = Duration(hours: 8);
    static const Duration tokenRefreshThreshold = Duration(minutes: 5);

    static const Duration syncInterval = Duration(minutes: 5);
    static const int maxRetryAttempts = 3;

    static const int qrErrorCorrectionLevel = 2;
    static const int qrImageSize = 256;

    static const int maxCachedPermits = 1000;
    static const int maxCachedTravelers = 5000;
    static const int maxCachedWanted = 10000;

    static const List<Locale> supportedLocales = [
        Locale("ar"),
        Locale("en"),
    ];
    static const Locale defaultLocale = Locale("ar");

    static const Color primaryColor = Color(0xFF1E3A8A);
    static const Color secondaryColor = Color(0xFF64748B);
    static const Color successColor = Color(0xFF059669);
    static const Color dangerColor = Color(0xFFDC2626);
    static const Color warningColor = Color(0xFFD97706);

    static Future<void> initialize() async {
        WidgetsFlutterBinding.ensureInitialized();
        SystemChrome.setPreferredOrientations([
            DeviceOrientation.portraitUp,
            DeviceOrientation.portraitDown,
            DeviceOrientation.landscapeLeft,
            DeviceOrientation.landscapeRight,
        ]);
    }
}'

create_file "$BASE_DIR/lib/core/config/api_config.dart" 'class ApiConfig {
    static const String baseUrl = "http://localhost:8000/api/v1";
    static const int timeout = 30000;

    // Endpoints
    static const String auth = "/auth";
    static const String travelers = "/travelers";
    static const String wanted = "/wanted";
    static const String permits = "/permits";
    static const String alerts = "/alerts";
    static const String cameras = "/cameras";
    static const String reports = "/reports";
    static const String cities = "/cities";
    static const String gates = "/gates";

    // Auth endpoints
    static const String login = "\$auth/login";
    static const String refresh = "\$auth/refresh";
    static const String logout = "\$auth/logout";

    // Travelers endpoints
    static const String travelersList = "\$travelers";
    static const String travelerDetail = "\$travelers/";
    static const String travelerSearch = "\$travelers/search";
    static const String travelerCreate = "\$travelers";

    // Wanted endpoints
    static const String wantedCheck = "\$wanted/check";
    static const String wantedList = "\$wanted";
    static const String wantedCreate = "\$wanted";

    // Permits endpoints
    static const String permitsList = "\$permits";
    static const String permitCreate = "\$permits";
    static const String permitDetail = "\$permits/";
    static const String permitExit = "\$permits/exit";

    // Alerts endpoints
    static const String alertsList = "\$alerts/active";
    static const String alertResolve = "\$alerts/";

    // Cameras endpoints
    static const String camerasList = "\$cameras";
    static const String cameraStream = "\$cameras/stream/";

    // Reports endpoints
    static const String movementReport = "\$reports/movements";
    static const String alertsReport = "\$reports/alerts";
}'

create_file "$BASE_DIR/lib/core/config/auth_config.dart" 'class AuthConfig {
    static const String tokenKey = "access_token";
    static const String refreshTokenKey = "refresh_token";
    static const String userKey = "current_user";
    static const String tokenExpiryKey = "token_expiry";

    static const Duration tokenValidity = Duration(hours: 1);
    static const Duration refreshTokenValidity = Duration(days: 7);

    static const int maxLoginAttempts = 5;
    static const Duration lockoutDuration = Duration(minutes: 15);
}'

# Services
create_file "$BASE_DIR/lib/core/services/api_client.dart" 'import "dart:convert";
import "package:dio/dio.dart";
import "../../constants.dart";

class ApiClient {
    static final ApiClient _instance = ApiClient._();
    factory ApiClient() => _instance;
    ApiClient._();

    late Dio _dio;

    void initialize() {
        _dio = Dio(BaseOptions(
            baseUrl: ApiConfig.baseUrl,
            connectTimeout: ApiConfig.timeout,
            receiveTimeout: ApiConfig.timeout,
            contentType: "application/json",
        ));
    }

    Future<dynamic> get(String path, {Map<String, dynamic>? params}) async {
        try {
            final response = await _dio.get(path, queryParameters: params);
            return response.data;
        } catch (e) {
            throw _handleError(e);
        }
    }

    Future<dynamic> post(String path, {dynamic data}) async {
        try {
            final response = await _dio.post(path, data: data);
            return response.data;
        } catch (e) {
            throw _handleError(e);
        }
    }

    Future<dynamic> put(String path, {dynamic data}) async {
        try {
            final response = await _dio.put(path, data: data);
            return response.data;
        } catch (e) {
            throw _handleError(e);
        }
    }

    Future<dynamic> delete(String path) async {
        try {
            final response = await _dio.delete(path);
            return response.data;
        } catch (e) {
            throw _handleError(e);
        }
    }

    Exception _handleError(dynamic error) {
        if (error is DioException) {
            switch (error.type) {
                case DioExceptionType.connectionTimeout:
                    return Exception("انتهت مهلة الاتصال");
                case DioExceptionType.receiveTimeout:
                    return Exception("انتهت مهلة الاستجابة");
                case DioExceptionType.connectionError:
                    return Exception("فشل الاتصال");
                default:
                    return Exception("حدث خطأ: \${error.message}");
            }
        }
        return Exception("حدث خطأ غير متوقع");
    }
}'

create_file "$BASE_DIR/lib/core/services/connectivity_service.dart" 'import "package:connectivity_plus/connectivity_plus.dart";

class ConnectivityService {
    static final ConnectivityService _instance = ConnectivityService._();
    factory ConnectivityService() => _instance;
    ConnectivityService._();

    final Connectivity _connectivity = Connectivity();

    Stream<bool> get onConnectivityChanged {
        return _connectivity.onConnectivityChanged.map((result) {
            return result != ConnectivityResult.none;
        });
    }

    Future<bool> isConnected() async {
        final result = await _connectivity.checkConnectivity();
        return result != ConnectivityResult.none;
    }

    Future<ConnectivityResult> get connectivityType async {
        return await _connectivity.checkConnectivity();
    }
}'

create_file "$BASE_DIR/lib/core/services/storage_service.dart" 'import "package:hive/hive.dart";
import "../../constants.dart";

class StorageService {
    static final StorageService _instance = StorageService._();
    factory StorageService() => _instance;
    StorageService._();

    late Box<dynamic> _box;

    Future<void> initialize() async {
        _box = await Hive.openBox(AppConstants.apiBaseUrl);
    }

    Future<void> set(String key, dynamic value) async {
        await _box.put(key, value);
    }

    dynamic get(String key, {dynamic defaultValue}) async {
        return await _box.get(key, defaultValue: defaultValue);
    }

    Future<void> remove(String key) async {
        await _box.delete(key);
    }

    Future<void> clear() async {
        await _box.clear();
    }

    Future<bool> containsKey(String key) async {
        return await _box.containsKey(key);
    }
}'

create_file "$BASE_DIR/lib/core/services/sync_service.dart" 'import "dart:async";
import "connectivity_service.dart";
import "storage_service.dart";

class SyncService {
    static final SyncService _instance = SyncService._();
    factory SyncService() => _instance;
    SyncService._();

    Timer? _syncTimer;
    bool _isSyncing = false;

    void start() {
        _syncTimer = Timer.periodic(
            Duration(minutes: 5),
            (_) => _sync,
        );
    }

    void stop() {
        _syncTimer?.cancel();
        _syncTimer = null;
    }

    Future<void> _sync() async {
        if (_isSyncing) return;
        if (!(await ConnectivityService().isConnected())) return;

        _isSyncing = true;
        try {
            // تنفيذ المزامنة
            print("جاري المزامنة...");
        } catch (e) {
            print("خطأ في المزامنة: \$e");
        } finally {
            _isSyncing = false;
        }
    }

    Future<void> syncNow() async {
        await _sync();
    }
}'

create_file "$BASE_DIR/lib/core/services/notification_service.dart" 'import "package:flutter_local_notifications/flutter_local_notifications.dart";

class NotificationService {
    static final NotificationService _instance = NotificationService._();
    factory NotificationService() => _instance;
    NotificationService._();

    final FlutterLocalNotificationsPlugin _notifications = FlutterLocalNotificationsPlugin();

    Future<void> initialize() async {
        const androidSettings = AndroidInitializationSettings("@mipmap/ic_launcher");
        const iosSettings = DarwinInitializationSettings(
            requestAlertPermission: true,
            requestBadgePermission: true,
            requestSoundPermission: true,
        );

        const settings = InitializationSettings(
            android: androidSettings,
            iOS: iosSettings,
        );

        await _notifications.initialize(settings);
    }

    Future<void> showNotification({
        required String title,
        required String body,
        int id = 0,
    }) async {
        const androidDetails = AndroidNotificationDetails(
            "gateflow_channel",
            "GateFlow Notifications",
            importance: Importance.high,
            priority: Priority.high,
        );

        const iosDetails = DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
        );

        const details = NotificationDetails(
            android: androidDetails,
            iOS: iosDetails,
        );

        await _notifications.show(id, title, body, details);
    }

    Future<void> showAlert({
        required String title,
        required String body,
        int id = 1,
    }) async {
        const androidDetails = AndroidNotificationDetails(
            "gateflow_alerts",
            "GateFlow Alerts",
            importance: Importance.max,
            priority: Priority.max,
        );

        const iosDetails = DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
        );

        const details = NotificationDetails(
            android: androidDetails,
            iOS: iosDetails,
        );

        await _notifications.show(id, title, body, details);
    }
}'

create_file "$BASE_DIR/lib/core/services/auth_service.dart" 'import "api_client.dart";
import "storage_service.dart";
import "../../constants.dart";
import "../config/auth_config.dart";

class AuthService {
    static final AuthService _instance = AuthService._();
    factory AuthService() => _instance;
    AuthService._();

    final ApiClient _api = ApiClient();
    final StorageService _storage = StorageService();

    Future<bool> login(String username, String password) async {
        try {
            final response = await _api.post(AuthConfig.login, data: {
                "username": username,
                "password": password,
            });

            if (response["success"]) {
                await _storage.set(AuthConfig.tokenKey, response["data"]["access_token"]);
                await _storage.set(AuthConfig.refreshTokenKey, response["data"]["refresh_token"]);
                await _storage.set(AuthConfig.userKey, response["data"]["user"]);
                return true;
            }
            return false;
        } catch (e) {
            throw Exception("فشل تسجيل الدخول: \$e");
        }
    }

    Future<bool> logout() async {
        try {
            await _api.post(AuthConfig.logout);
            await _storage.clear();
            return true;
        } catch (e) {
            await _storage.clear();
            return true;
        }
    }

    Future<String?> getToken() async {
        return await _storage.get(AuthConfig.tokenKey);
    }

    Future<bool> isLoggedIn() async {
        final token = await getToken();
        return token != null;
    }
}'

create_file "$BASE_DIR/lib/core/services/cryptography_service.dart" 'import "dart:convert";
import "package:crypto/crypto.dart";

class CryptographyService {
    static final CryptographyService _instance = CryptographyService._();
    factory CryptographyService() => _instance;
    CryptographyService._();

    String encrypt(String data) {
        final bytes = utf8.encode(data);
        final digest = sha256.convert(bytes);
        return digest.toString();
    }

    String hashNationalId(String nationalId) {
        return encrypt(nationalId);
    }

    bool verifyHash(String data, String hash) {
        return encrypt(data) == hash;
    }
}'

# Guards
create_file "$BASE_DIR/lib/core/guards/auth_guard.dart" 'import "package:flutter/material.dart";
import "../../routes.dart";
import "auth_service.dart";

class AuthGuard extends StatelessWidget {
    final Widget child;

    const AuthGuard({required this.child});

    @override
    Widget build(BuildContext context) {
        return FutureBuilder<bool>(
            future: AuthService().isLoggedIn(),
            builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                    return Scaffold(body: Center(child: CircularProgressIndicator()));
                }
                if (snapshot.data == true) {
                    return child;
                }
                return WillPopScope(
                    onWillPop: () async => false,
                    child: Scaffold(
                        body: Center(
                            child: ElevatedButton(
                                onPressed: () => Navigator.pushReplacementNamed(context, Routes.login),
                                child: Text("تسجيل الدخول"),
                            ),
                        ),
                    ),
                );
            },
        );
    }
}'

create_file "$BASE_DIR/lib/core/guards/role_guard.dart" 'import "package:flutter/material.dart";

enum UserRole { admin, supervisor, entry_officer, exit_officer, viewer }

class RoleGuard extends StatelessWidget {
    final Widget child;
    final List<UserRole> allowedRoles;

    const RoleGuard({required this.child, required this.allowedRoles});

    @override
    Widget build(BuildContext context) {
        return child;
    }
}'

# Network
create_file "$BASE_DIR/lib/core/network/network_client.dart" 'import "dart:io";
import "package:http/http.dart" as http;

class NetworkClient {
    static final NetworkClient _instance = NetworkClient._();
    factory NetworkClient() => _instance;
    NetworkClient._();

    final http.Client _client = http.Client();

    Future<http.Response> get(Uri url, {Map<String, String>? headers}) async {
        return await _client.get(url, headers: headers);
    }

    Future<http.Response> post(Uri url, {Map<String, String>? headers, dynamic body}) async {
        return await _client.post(url, headers: headers, body: body);
    }

    Future<http.Response> put(Uri url, {Map<String, String>? headers, dynamic body}) async {
        return await _client.put(url, headers: headers, body: body);
    }

    Future<http.Response> delete(Uri url, {Map<String, String>? headers}) async {
        return await _client.delete(url, headers: headers);
    }

    void close() {
        _client.close();
    }
}'

create_file "$BASE_DIR/lib/core/network/network_info.dart" 'import "package:flutter/services.dart";

class NetworkInfo {
    static final NetworkInfo _instance = NetworkInfo._();
    factory NetworkInfo() => _instance;
    NetworkInfo._();

    static const MethodChannel _channel = MethodChannel("network_info");

    Future<bool> isConnected() async {
        final result = await _channel.invokeMethod<bool>("isConnected");
        return result ?? false;
    }

    Future<String> getConnectionType() async {
        final result = await _channel.invokeMethod<String>("getConnectionType");
        return result ?? "unknown";
    }
}'

create_file "$BASE_DIR/lib/core/network/retry_interceptor.dart" 'import "package:dio/dio.dart";

class RetryInterceptor extends Interceptor {
    final int retries;
    final List<int> retryStatuses = [500, 502, 503, 504];

    RetryInterceptor({this.retries = 3});

    @override
    Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
        if (!_shouldRetry(err)) {
            return handler.next(err);
        }

        int attempt = 1;
        while (attempt <= retries) {
            try {
                final response = await _retry(err.requestOptions);
                return handler.resolve(response);
            } catch (e) {
                attempt++;
            }
        }
        return handler.next(err);
    }

    bool _shouldRetry(DioException error) {
        return error.response != null && retryStatuses.contains(error.response?.statusCode);
    }

    Future<Response> _retry(RequestOptions options) async {
        final dio = Dio();
        return await dio.request(
            options.path,
            options: Options(
                method: options.method,
                headers: options.headers,
            ),
            data: options.data,
            queryParameters: options.queryParameters,
        );
    }
}'

# Utils
create_file "$BASE_DIR/lib/core/utils/date_formatter.dart" 'import "package:intl/intl.dart";

class DateFormatter {
    static String formatDate(DateTime date, {String format = "yyyy/MM/dd"}) {
        return DateFormat(format, "ar_SA").format(date);
    }

    static String formatTime(DateTime date, {String format = "HH:mm"}) {
        return DateFormat(format, "ar_SA").format(date);
    }

    static String formatDateTime(DateTime date) {
        return DateFormat("yyyy/MM/dd HH:mm", "ar_SA").format(date);
    }

    static String formatRelative(DateTime date) {
        final now = DateTime.now();
        final diff = now.difference(date);

        if (diff.inMinutes < 1) return "الآن";
        if (diff.inMinutes < 60) return "\${diff.inMinutes} دقيقة";
        if (diff.inHours < 24) return "\${diff.inHours} ساعة";
        if (diff.inDays < 7) return "\${diff.inDays} يوم";
        
        return formatDate(date);
    }

    static String formatPermitExpiry(DateTime expiry) {
        final now = DateTime.now();
        final diff = expiry.difference(now);

        if (diff.isNegative) return "منتهي";
        if (diff.inMinutes < 60) return "\${diff.inMinutes} دقيقة";
        if (diff.inHours < 24) return "\${diff.inHours} ساعة";
        return "\${diff.inDays} يوم و \${diff.inHours % 24} ساعة";
    }
}'

create_file "$BASE_DIR/lib/core/utils/string_utils.dart" 'class StringUtils {
    static String generatePermitCode() {
        final now = DateTime.now();
        final year = now.year;
        final timestamp = now.microsecondsSinceEpoch % 1000000;
        return "PMT-\$year-\$timestamp";
    }

    static String maskNationalId(String id) {
        if (id.length <= 4) return id;
        final visible = id.substring(id.length - 4);
        return "****\$visible";
    }

    static String maskPhone(String phone) {
        if (phone.length <= 4) return phone;
        final visible = phone.substring(phone.length - 4);
        return "****\$visible";
    }

    static bool isValidNationalId(String id) {
        return RegExp(r"^\d{7,20}\$").hasMatch(id);
    }

    static bool isValidPhone(String phone) {
        return RegExp(r"^\+?[0-9]{9,15}\$").hasMatch(phone);
    }

    static String capitalize(String text) {
        if (text.isEmpty) return text;
        return text[0].toUpperCase() + text.substring(1);
    }

    static List<String> splitIntoWords(String text) {
        return text.split(RegExp(r"\s+")).where((e) => e.isNotEmpty).toList();
    }
}'

create_file "$BASE_DIR/lib/core/utils/validators.dart" 'class Validators {
    static String? required(String? value) {
        if (value == null || value.trim().isEmpty) {
            return "هذا الحقل مطلوب";
        }
        return null;
    }

    static String? nationalId(String? value) {
        if (value == null || value.trim().isEmpty) {
            return "الرقم الوطني مطلوب";
        }
        if (!RegExp(r"^\d{7,20}\$").hasMatch(value)) {
            return "الرقم الوطني غير صالح";
        }
        return null;
    }

    static String? phone(String? value) {
        if (value == null || value.trim().isEmpty) {
            return null;
        }
        if (!RegExp(r"^\+?[0-9]{9,15}\$").hasMatch(value)) {
            return "رقم الهاتف غير صالح";
        }
        return null;
    }

    static String? name(String? value) {
        if (value == null || value.trim().isEmpty) {
            return "الاسم مطلوب";
        }
        if (value.trim().length < 3) {
            return "الاسم قصير جداً";
        }
        if (value.trim().length > 200) {
            return "الاسم طويل جداً";
        }
        return null;
    }

    static String? email(String? value) {
        if (value == null || value.trim().isEmpty) {
            return null;
        }
        if (!RegExp(r"^[\w.-]+@[\w.-]+\.\w+\$").hasMatch(value)) {
            return "البريد الإلكتروني غير صالح";
        }
        return null;
    }

    static String? duration(String? value) {
        if (value == null || value.trim().isEmpty) {
            return "المدة مطلوبة";
        }
        final duration = int.tryParse(value);
        if (duration == null || duration < 1 || duration > 72) {
            return "المدة يجب أن تكون بين 1 و 72 ساعة";
        }
        return null;
    }
}'

create_file "$BASE_DIR/lib/core/utils/formatters.dart" 'import "package:flutter/services.dart";

class NationalIdFormatter extends TextInputFormatter {
    @override
    TextEditingValue formatEditUpdate(
        TextEditingValue oldValue,
        TextEditingValue newValue,
    ) {
        final text = newValue.text.replaceAll(RegExp(r"[^\d]"), "");
        return TextEditingValue(
            text: text,
            selection: TextSelection.collapsed(offset: text.length),
        );
    }
}

class PhoneFormatter extends TextInputFormatter {
    @override
    TextEditingValue formatEditUpdate(
        TextEditingValue oldValue,
        TextEditingValue newValue,
    ) {
        final text = newValue.text.replaceAll(RegExp(r"[^\d+]"), "");
        return TextEditingValue(
            text: text,
            selection: TextSelection.collapsed(offset: text.length),
        );
    }
}

class NumberFormatter extends TextInputFormatter {
    @override
    TextEditingValue formatEditUpdate(
        TextEditingValue oldValue,
        TextEditingValue newValue,
    ) {
        if (newValue.text.isEmpty) return newValue;
        final text = newValue.text.replaceAll(RegExp(r"[^\d]"), "");
        return TextEditingValue(
            text: text,
            selection: TextSelection.collapsed(offset: text.length),
        );
    }
}'

create_file "$BASE_DIR/lib/core/utils/qr_generator.dart" 'import "package:qr_flutter/qr_flutter.dart";
import "package:flutter/material.dart";
import "../../constants.dart";

class QrGenerator {
    static Widget generateQrCode(String data, {double size = 256}) {
        return QrImageView(
            data: data,
            version: QrVersions.auto,
            size: size,
            backgroundColor: Colors.white,
            eyeStyle: const QrEyeStyle(
                eyeShape: QrEyeShape.square,
                color: Color(0xFF1E3A8A),
            ),
            dataModuleStyle: const QrDataModuleStyle(
                dataModuleShape: QrDataModuleShape.square,
                color: Colors.black,
            ),
            errorStateBuilder: (c, e) {
                return Container(
                    child: Center(child: Text("خطأ في إنشاء QR")),
                );
            },
        );
    }

    static String generatePermitQrData({
        required String permitCode,
        required String nationalId,
        required DateTime entryTime,
        required int durationHours,
    }) {
        final data = {
            "code": permitCode,
            "nid": nationalId,
            "entry": entryTime.toIso8601String(),
            "duration": durationHours,
        };
        return Uri.encodeComponent(data.toString());
    }
}'

# Widgets
create_file "$BASE_DIR/lib/core/widgets/app_drawer.dart" 'import "package:flutter/material.dart";
import "../../routes.dart";

class AppDrawer extends StatelessWidget {
    final String currentRoute;

    const AppDrawer({required this.currentRoute});

    @override
    Widget build(BuildContext context) {
        return Drawer(
            child: ListView(
                children: [
                    DrawerHeader(
                        decoration: BoxDecoration(color: Color(0xFF1E3A8A)),
                        child: Center(
                            child: Text(
                                "GateFlow",
                                style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                ),
                            ),
                        ),
                    ),
                    _buildMenuItem(context, Icons.dashboard, "لوحة المراقبة", Routes.dashboard),
                    _buildMenuItem(context, Icons.people, "المسافرين", Routes.travelers),
                    _buildMenuItem(context, Icons.card_membership, "السندات", Routes.permits),
                    _buildMenuItem(context, Icons.qr_code_scanner, "الماسح الضوئي", Routes.scanner),
                    _buildMenuItem(context, Icons.camera_alt, "الكاميرات", Routes.cameras),
                    _buildMenuItem(context, Icons.notifications, "التنبيهات", Routes.alerts),
                    _buildMenuItem(context, Icons.analytics, "التقارير", Routes.reports),
                    Divider(),
                    _buildMenuItem(context, Icons.settings, "الإعدادات", Routes.settings),
                ],
            ),
        );
    }

    Widget _buildMenuItem(BuildContext context, IconData icon, String title, String route) {
        final isSelected = currentRoute == route;
        return ListTile(
            leading: Icon(icon, color: isSelected ? Color(0xFF1E3A8A) : Colors.grey[700]),
            title: Text(
                title,
                style: TextStyle(
                    color: isSelected ? Color(0xFF1E3A8A) : Colors.black,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
            ),
            selected: isSelected,
            selectedTileColor: Color(0xFF1E3A8A).withOpacity(0.1),
            onTap: () {
                Navigator.pop(context);
                if (currentRoute != route) {
                    Navigator.pushReplacementNamed(context, route);
                }
            },
        );
    }
}'

create_file "$BASE_DIR/lib/core/widgets/custom_button.dart" 'import "package:flutter/material.dart";

class CustomButton extends StatelessWidget {
    final String text;
    final VoidCallback onPressed;
    final IconData? icon;
    final bool isLoading;
    final bool isSecondary;
    final double? width;
    final double height;

    const CustomButton({
        required this.text,
        required this.onPressed,
        this.icon,
        this.isLoading = false,
        this.isSecondary = false,
        this.width,
        this.height = 50,
    });

    @override
    Widget build(BuildContext context) {
        final color = isSecondary ? Colors.grey : Color(0xFF1E3A8A);
        
        return SizedBox(
            width: width ?? double.infinity,
            height: height,
            child: ElevatedButton(
                onPressed: isLoading ? null : onPressed,
                style: ElevatedButton.styleFrom(
                    backgroundColor: color,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                    ),
                ),
                child: isLoading
                    ? SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                        ),
                    )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                            if (icon != null) ...[
                                Icon(icon),
                                SizedBox(width: 8),
                            ],
                            Text(text, style: TextStyle(fontSize: 16)),
                        ],
                    ),
            ),
        );
    }
}'

create_file "$BASE_DIR/lib/core/widgets/custom_input.dart" 'import "package:flutter/material.dart";
import "validators.dart";

class CustomInput extends StatelessWidget {
    final String label;
    final String hint;
    final TextEditingController controller;
    final TextInputType keyboardType;
    final String? Function(String?)? validator;
    final bool obscureText;
    final Widget? prefixIcon;
    final Widget? suffixIcon;
    final int maxLines;
    final TextInputFormatter? formatter;

    const CustomInput({
        required this.label,
        required this.hint,
        required this.controller,
        this.keyboardType = TextInputType.text,
        this.validator,
        this.obscureText = false,
        this.prefixIcon,
        this.suffixIcon,
        this.maxLines = 1,
        this.formatter,
    });

    @override
    Widget build(BuildContext context) {
        return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
                Text(label, style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                TextFormField(
                    controller: controller,
                    keyboardType: keyboardType,
                    obscureText: obscureText,
                    maxLines: maxLines,
                    inputFormatters: formatter != null ? [formatter!] : [],
                    decoration: InputDecoration(
                        hintText: hint,
                        prefixIcon: prefixIcon,
                        suffixIcon: suffixIcon,
                        border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                        ),
                        filled: true,
                        fillColor: Colors.grey[50],
                    ),
                    validator: validator,
                ),
            ],
        );
    }
}'

create_file "$BASE_DIR/lib/core/widgets/loading_indicator.dart" 'import "package:flutter/material.dart";

class LoadingIndicator extends StatelessWidget {
    final String? message;

    const LoadingIndicator({this.message});

    @override
    Widget build(BuildContext context) {
        return Center(
            child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                    CircularProgressIndicator(
                        valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF1E3A8A)),
                    ),
                    if (message != null) ...[
                        SizedBox(height: 16),
                        Text(message!, style: TextStyle(color: Colors.grey)),
                    ],
                ],
            ),
        );
    }
}'

create_file "$BASE_DIR/lib/core/widgets/empty_state.dart" 'import "package:flutter/material.dart";

class EmptyState extends StatelessWidget {
    final IconData icon;
    final String title;
    final String? message;
    final Widget? action;

    const EmptyState({
        required this.icon,
        required this.title,
        this.message,
        this.action,
    });

    @override
    Widget build(BuildContext context) {
        return Center(
            child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                    Icon(icon, size: 64, color: Colors.grey[400]),
                    SizedBox(height: 16),
                    Text(
                        title,
                        style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey[700],
                        ),
                    ),
                    if (message != null) ...[
                        SizedBox(height: 8),
                        Text(
                            message!,
                            style: TextStyle(color: Colors.grey[500]),
                        ),
                    ],
                    if (action != null) ...[
                        SizedBox(height: 24),
                        action!,
                    ],
                ],
            ),
        );
    }
}'

create_file "$BASE_DIR/lib/core/widgets/status_badge.dart" 'import "package:flutter/material.dart";

enum StatusType { active, exited, expired, flagged, pending, warning, danger, success }

class StatusBadge extends StatelessWidget {
    final StatusType type;
    final String text;

    const StatusBadge({required this.type, required this.text});

    @override
    Widget build(BuildContext context) {
        final (color, icon) = _getStatusStyle();

        return Container(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: color),
            ),
            child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                    Icon(icon, size: 14, color: color),
                    SizedBox(width: 4),
                    Text(
                        text,
                        style: TextStyle(
                            color: color,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                        ),
                    ),
                ],
            ),
        );
    }

    (Color, IconData) _getStatusStyle() {
        switch (type) {
            case StatusType.active:
            case StatusType.success:
                return (Color(0xFF059669), Icons.check_circle);
            case StatusType.exited:
                return (Color(0xFF1E3A8A), Icons.exit_to_app);
            case StatusType.expired:
            case StatusType.danger:
                return (Color(0xFFDC2626), Icons.cancel);
            case StatusType.flagged:
            case StatusType.warning:
                return (Color(0xFFD97706), Icons.warning);
            case StatusType.pending:
                return (Color(0xFF64748B), Icons.hourglass_empty);
        }
    }
}'

# Extensions
create_file "$BASE_DIR/lib/core/extensions/context_extensions.dart" 'import "package:flutter/material.dart";

extension ContextExtensions on BuildContext {
    Size get screenSize => MediaQuery.of(this).size;
    double get screenWidth => screenSize.width;
    double get screenHeight => screenSize.height;
    bool get isDarkMode => Theme.of(this).brightness == Brightness.dark;
    
    void showSnackBar(String message, {Color? backgroundColor}) {
        ScaffoldMessenger.of(this).showSnackBar(
            SnackBar(content: Text(message), backgroundColor: backgroundColor),
        );
    }
    
    void showError(String message) {
        showSnackBar(message, backgroundColor: Color(0xFFDC2626));
    }
    
    void showSuccess(String message) {
        showSnackBar(message, backgroundColor: Color(0xFF059669));
    }
}'

create_file "$BASE_DIR/lib/core/extensions/date_extensions.dart" 'import "package:flutter/material.dart";

extension DateExtensions on DateTime {
    String get formatDateOnly {
        return "\$year/\$month/\$day";
    }
    
    String get formatTimeOnly {
        return "\${hour.toString().padLeft(2, "0")}:\${minute.toString().padLeft(2, "0")}";
    }
    
    String get formatDateTime {
        return "\$formatDateOnly \$formatTimeOnly";
    }
    
    bool get isToday {
        final now = DateTime.now();
        return year == now.year && month == now.month && day == now.day;
    }
    
    bool get isYesterday {
        final yesterday = DateTime.now().subtract(Duration(days: 1));
        return year == yesterday.year && month == yesterday.month && day == yesterday.day;
    }
    
    bool get isExpired => DateTime.now().isAfter(this);
    
    Duration get remainingTime {
        final now = DateTime.now();
        if (isExpired) return Duration.zero;
        return difference(now);
    }
}'

create_file "$BASE_DIR/lib/core/extensions/string_extensions.dart" 'extension StringExtensions on String {
    bool get isNullOrEmpty => trim().isEmpty;
    
    bool get isNotNullOrEmpty => !isNullOrEmpty;
    
    String get capitalize {
        if (isEmpty) return this;
        return "\${this[0].toUpperCase()}\${substring(1)}";
    }
    
    String get capitalizeEach {
        return split(" ").map((e) => e.capitalize).join(" ");
    }
    
    String get reverse {
        return split("").reversed.join("");
    }
    
    String get toArabicDigits {
        final englishDigits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
        final arabicDigits = ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩"];
        var result = this;
        for (int i = 0; i < englishDigits.length; i++) {
            result = result.replaceAll(englishDigits[i], arabicDigits[i]);
        }
        return result;
    }
    
    String mask({int visibleFromEnd = 4}) {
        if (length <= visibleFromEnd) return this;
        final visible = substring(length - visibleFromEnd);
        return "****\$visible";
    }
    
    List<String> toWords() {
        return split(RegExp(r"\s+")).where((e) => e.isNotEmpty).toList();
    }
}'

# ============================================
# وحدة Auth
# ============================================

echo ""
echo "جاري إنشاء وحدة Auth..."

create_file "$BASE_DIR/lib/auth/login_screen.dart" 'import "package:flutter/material.dart";
import "package:flutter/services.dart";
import "../core/widgets/custom_button.dart";
import "../core/widgets/custom_input.dart";
import "../core/utils/validators.dart";
import "../core/services/auth_service.dart";

class LoginScreen extends StatefulWidget {
    @override
    _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
    final _usernameController = TextEditingController();
    final _passwordController = TextEditingController();
    final _formKey = GlobalKey<FormState>();
    bool _isLoading = false;
    bool _obscurePassword = true;

    @override
    Widget build(BuildContext context) {
        return Scaffold(
            body: SafeArea(
                child: Center(
                    child: SingleChildScrollView(
                        padding: EdgeInsets.all(24),
                        child: Form(
                            key: _formKey,
                            child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                    Icon(Icons.security, size: 80, color: Color(0xFF1E3A8A)),
                                    SizedBox(height: 24),
                                    Text(
                                        "GateFlow",
                                        style: TextStyle(
                                            fontSize: 32,
                                            fontWeight: FontWeight.bold,
                                            color: Color(0xFF1E3A8A),
                                        ),
                                    ),
                                    SizedBox(height: 8),
                                    Text("نظام إدارة حركة المسافرين"),
                                    SizedBox(height: 48),
                                    CustomInput(
                                        label: "اسم المستخدم",
                                        hint: "أدخل اسم المستخدم",
                                        controller: _usernameController,
                                        keyboardType: TextInputType.text,
                                        validator: Validators.required,
                                    ),
                                    SizedBox(height: 16),
                                    CustomInput(
                                        label: "كلمة المرور",
                                        hint: "أدخل كلمة المرور",
                                        controller: _passwordController,
                                        keyboardType: TextInputType.text,
                                        obscureText: _obscurePassword,
                                        validator: Validators.required,
                                        suffixIcon: IconButton(
                                            icon: Icon(
                                                _obscurePassword ? Icons.visibility : Icons.visibility_off,
                                            ),
                                            onPressed: () {
                                                setState(() {
                                                    _obscurePassword = !_obscurePassword;
                                                });
                                            },
                                        ),
                                    ),
                                    SizedBox(height: 24),
                                    CustomButton(
                                        text: "تسجيل الدخول",
                                        isLoading: _isLoading,
                                        onPressed: _login,
                                    ),
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        );
    }

    Future<void> _login() async {
        if (!_formKey.currentState!.validate()) return;

        setState(() => _isLoading = true);
        try {
            final success = await AuthService().login(
                _usernameController.text.trim(),
                _passwordController.text,
            );

            if (success) {
                Navigator.pushReplacementNamed(context, "/dashboard");
            } else {
                context.showError("فشل تسجيل الدخول");
            }
        } catch (e) {
            context.showError(e.toString());
        } finally {
            setState(() => _isLoading = false);
        }
    }
}'

create_file "$BASE_DIR/lib/auth/models/login_request.dart" 'class LoginRequest {
    final String username;
    final String password;

    LoginRequest({required this.username, required this.password});

    Map<String, dynamic> toJson() => {
        "username": username,
        "password": password,
    };
}'

create_file "$BASE_DIR/lib/auth/models/login_response.dart" 'class LoginResponse {
    final String accessToken;
    final String refreshToken;
    final String tokenType;
    final int expiresIn;
    final UserInfo user;

    LoginResponse({
        required this.accessToken,
        required this.refreshToken,
        required this.tokenType,
        required this.expiresIn,
        required this.user,
    });

    factory LoginResponse.fromJson(Map<String, dynamic> json) {
        return LoginResponse(
            accessToken: json["data"]["access_token"],
            refreshToken: json["data"]["refresh_token"],
            tokenType: json["data"]["token_type"],
            expiresIn: json["data"]["expires_in"],
            user: UserInfo.fromJson(json["data"]["user"]),
        );
    }
}

class UserInfo {
    final int id;
    final String name;
    final String username;
    final String role;
    final int? gateId;

    UserInfo({
        required this.id,
        required this.name,
        required this.username,
        required this.role,
        this.gateId,
    });

    factory UserInfo.fromJson(Map<String, dynamic> json) {
        return UserInfo(
            id: json["id"],
            name: json["name"],
            username: json["username"],
            role: json["role"],
            gateId: json["gate_id"],
        );
    }
}'

create_file "$BASE_DIR/lib/auth/models/token_model.dart" 'class TokenModel {
    final String accessToken;
    final String refreshToken;
    final DateTime expiresAt;

    TokenModel({
        required this.accessToken,
        required this.refreshToken,
        required this.expiresAt,
    });

    bool get isExpired => DateTime.now().isAfter(expiresAt);

    bool get needsRefresh {
        final threshold = DateTime.now().add(Duration(minutes: 5));
        return expiresAt.isBefore(threshold);
    }

    factory TokenModel.fromJson(Map<String, dynamic> json, int expiresInSeconds) {
        return TokenModel(
            accessToken: json["access_token"],
            refreshToken: json["refresh_token"],
            expiresAt: DateTime.now().add(Duration(seconds: expiresInSeconds)),
        );
    }
}'

# ============================================
# وحدة Travelers
# ============================================

echo ""
echo "جاري إنشاء وحدة Travelers..."

create_file "$BASE_DIR/lib/travelers/models/traveler.dart" 'class Traveler {
    final int id;
    final String fullName;
    final String nationalId;
    final String? phone;
    final String? address;
    final String? notes;
    final bool isFlagged;
    final String? flagReason;
    final DateTime createdAt;

    Traveler({
        required this.id,
        required this.fullName,
        required this.nationalId,
        this.phone,
        this.address,
        this.notes,
        this.isFlagged = false,
        this.flagReason,
        required this.createdAt,
    });

    factory Traveler.fromJson(Map<String, dynamic> json) {
        return Traveler(
            id: json["id"],
            fullName: json["full_name"],
            nationalId: json["national_id"],
            phone: json["phone"],
            address: json["address"],
            notes: json["notes"],
            isFlagged: json["is_flagged"] ?? false,
            flagReason: json["flag_reason"],
            createdAt: DateTime.parse(json["created_at"]),
        );
    }

    Map<String, dynamic> toJson() => {
        "full_name": fullName,
        "national_id": nationalId,
        "phone": phone,
        "address": address,
        "notes": notes,
    };
}'

create_file "$BASE_DIR/lib/travelers/models/traveler_create_request.dart" 'class TravelerCreateRequest {
    final String fullName;
    final String nationalId;
    final String? phone;
    final String? address;
    final String? notes;

    TravelerCreateRequest({
        required this.fullName,
        required this.nationalId,
        this.phone,
        this.address,
        this.notes,
    });

    Map<String, dynamic> toJson() => {
        "full_name": fullName,
        "national_id": nationalId,
        "phone": phone,
        "address": address,
        "notes": notes,
    };
}'

create_file "$BASE_DIR/lib/travelers/models/wanted_check_result.dart" 'class WantedCheckResult {
    final bool isMatch;
    final int? wantedId;
    final String? fullName;
    final String? nationalId;
    final String? riskLevel;
    final double? confidenceScore;
    final String? notes;

    WantedCheckResult({
        required this.isMatch,
        this.wantedId,
        this.fullName,
        this.nationalId,
        this.riskLevel,
        this.confidenceScore,
        this.notes,
    });

    factory WantedCheckResult.noMatch() {
        return WantedCheckResult(isMatch: false);
    }

    factory WantedCheckResult.fromJson(Map<String, dynamic> json) {
        final matches = json["matches"] as List?;
        if (matches == null || matches.isEmpty) {
            return WantedCheckResult.noMatch();
        }
        
        final firstMatch = matches[0];
        return WantedCheckResult(
            isMatch: true,
            wantedId: firstMatch["wanted_id"],
            fullName: firstMatch["full_name"],
            nationalId: firstMatch["national_id"],
            riskLevel: firstMatch["risk_level"],
            confidenceScore: (firstMatch["confidence_score"] as num?)?.toDouble(),
            notes: firstMatch["notes"],
        );
    }
}'

# ============================================
# وحدة Permits
# ============================================

echo ""
echo "جاري إنشاء وحدة Permits..."

create_file "$BASE_DIR/lib/permits/models/permit.dart" 'import "package:flutter/material.dart";

class Permit {
    final int id;
    final String permitCode;
    final int travelerId;
    final String? travelerName;
    final String travelerNationalId;
    final int? weaponId;
    final int cityId;
    final String? cityName;
    final int entryGateId;
    final String? entryGateName;
    final int? exitGateId;
    final DateTime entryTime;
    final int allowedDurationHours;
    final DateTime expiryTime;
    final DateTime? exitTime;
    final PermitStatus status;
    final String? notes;
    final String? qrCode;
    final int createdBy;
    final DateTime createdAt;

    Permit({
        required this.id,
        required this.permitCode,
        required this.travelerId,
        this.travelerName,
        required this.travelerNationalId,
        this.weaponId,
        required this.cityId,
        this.cityName,
        required this.entryGateId,
        this.entryGateName,
        this.exitGateId,
        required this.entryTime,
        required this.allowedDurationHours,
        required this.expiryTime,
        this.exitTime,
        required this.status,
        this.notes,
        this.qrCode,
        required this.createdBy,
        required this.createdAt,
    });

    bool get isExpired => DateTime.now().isAfter(expiryTime);
    
    int get remainingMinutes {
        if (status != PermitStatus.active) return 0;
        final remaining = expiryTime.difference(DateTime.now());
        return remaining.isNegative ? 0 : remaining.inMinutes;
    }

    String get remainingText {
        if (remainingMinutes == 0) return "منتهي";
        if (remainingMinutes < 60) return "\$remainingMinutes دقيقة";
        final hours = remainingMinutes ~/ 60;
        final mins = remainingMinutes % 60;
        return "\$hours ساعة و \$mins دقيقة";
    }

    factory Permit.fromJson(Map<String, dynamic> json) {
        return Permit(
            id: json["id"],
            permitCode: json["permit_code"],
            travelerId: json["traveler_id"],
            travelerName: json["traveler"]?["full_name"],
            travelerNationalId: json["traveler"]?["national_id"] ?? "",
            weaponId: json["weapon_id"],
            cityId: json["city_id"],
            cityName: json["city"]?["name"],
            entryGateId: json["entry_gate_id"],
            entryGateName: json["entry_gate"]?["name"],
            exitGateId: json["exit_gate_id"],
            entryTime: DateTime.parse(json["entry_time"]),
            allowedDurationHours: json["allowed_duration_hours"],
            expiryTime: DateTime.parse(json["expiry_time"]),
            exitTime: json["exit_time"] != null ? DateTime.parse(json["exit_time"]) : null,
            status: PermitStatus.fromString(json["status"]),
            notes: json["notes"],
            qrCode: json["qr_code"],
            createdBy: json["created_by"],
            createdAt: DateTime.parse(json["created_at"]),
        );
    }
}

enum PermitStatus {
    active,
    exited,
    expired,
    flagged;

    static PermitStatus fromString(String value) {
        return values.firstWhere((e) => e.name == value);
    }

    String get displayName {
        switch (this) {
            case active: return "نشط";
            case exited: return "خرج";
            case expired: return "منتهي";
            case flagged: return "مُعلّم";
        }
    }

    Color get color {
        switch (this) {
            case active: return Color(0xFF059669);
            case exited: return Color(0xFF1E3A8A);
            case expired: return Color(0xFFDC2626);
            case flagged: return Color(0xFFD97706);
        }
    }
}'

create_file "$BASE_DIR/lib/permits/models/permit_create_request.dart" 'class PermitCreateRequest {
    final int travelerId;
    final int cityId;
    final int entryGateId;
    final int? weaponId;
    final int allowedDurationHours;
    final String? notes;

    PermitCreateRequest({
        required this.travelerId,
        required this.cityId,
        required this.entryGateId,
        this.weaponId,
        required this.allowedDurationHours,
        this.notes,
    });

    Map<String, dynamic> toJson() => {
        "traveler_id": travelerId,
        "city_id": cityId,
        "entry_gate_id": entryGateId,
        "weapon_id": weaponId,
        "allowed_duration_hours": allowedDurationHours,
        "notes": notes,
    };
}'

create_file "$BASE_DIR/lib/permits/models/permit_exit_request.dart" 'class PermitExitRequest {
    final String permitCode;
    final int exitGateId;
    final String? notes;

    PermitExitRequest({
        required this.permitCode,
        required this.exitGateId,
        this.notes,
    });

    Map<String, dynamic> toJson() => {
        "permit_code": permitCode,
        "exit_gate_id": exitGateId,
        "notes": notes,
    };
}'

# ============================================
# وحدة Alerts
# ============================================

echo ""
echo "جاري إنشاء وحدة Alerts..."

create_file "$BASE_DIR/lib/alerts/models/alert.dart" 'import "package:flutter/material.dart";

class Alert {
    final int id;
    final AlertType type;
    final AlertSeverity severity;
    final String? referenceType;
    final int? referenceId;
    final String message;
    final bool isResolved;
    final int? resolvedBy;
    final DateTime? resolvedAt;
    final String? resolutionNotes;
    final DateTime createdAt;

    Alert({
        required this.id,
        required this.type,
        required this.severity,
        this.referenceType,
        this.referenceId,
        required this.message,
        this.isResolved = false,
        this.resolvedBy,
        this.resolvedAt,
        this.resolutionNotes,
        required this.createdAt,
    });

    factory Alert.fromJson(Map<String, dynamic> json) {
        return Alert(
            id: json["id"],
            type: AlertType.fromString(json["type"]),
            severity: AlertSeverity.fromString(json["severity"]),
            referenceType: json["reference_type"],
            referenceId: json["reference_id"],
            message: json["message"],
            isResolved: json["is_resolved"] ?? false,
            resolvedBy: json["resolved_by"],
            resolvedAt: json["resolved_at"] != null ? DateTime.parse(json["resolved_at"]) : null,
            resolutionNotes: json["resolution_notes"],
            createdAt: DateTime.parse(json["created_at"]),
        );
    }
}

enum AlertType {
    wanted_match,
    permit_expired,
    permit_expiring,
    camera_offline,
    overstay,
    system_error;

    static AlertType fromString(String value) {
        return values.firstWhere((e) => e.name == value);
    }

    String get displayName {
        switch (this) {
            case wanted_match: return "تطابق مطلوب";
            case permit_expired: return "انتهاء سند";
            case permit_expiring: return "سند على وشك الانتهاء";
            case camera_offline: return "كاميرا غير متصلة";
            case overstay: return "تجاوز مدة الإقامة";
            case system_error: return "خطأ في النظام";
        }
    }

    String get icon {
        switch (this) {
            case wanted_match: return "person_search";
            case permit_expired: return "timer_off";
            case permit_expiring: return "timer";
            case camera_offline: return "videocam_off";
            case overstay: return "schedule";
            case system_error: return "error";
        }
    }
}

enum AlertSeverity {
    low,
    medium,
    critical;

    static AlertSeverity fromString(String value) {
        return values.firstWhere((e) => e.name == value);
    }

    String get displayName {
        switch (this) {
            case low: return "منخفض";
            case medium: return "متوسط";
            case critical: return "حرج";
        }
    }

    Color get color {
        switch (this) {
            case low: return Colors.blue;
            case medium: return Color(0xFFD97706);
            case critical: return Color(0xFFDC2626);
        }
    }
}'

create_file "$BASE_DIR/lib/alerts/models/alert_resolve_request.dart" 'class AlertResolveRequest {
    final int alertId;
    final String? resolutionNotes;

    AlertResolveRequest({required this.alertId, this.resolutionNotes});

    Map<String, dynamic> toJson() => {
        "resolution_notes": resolutionNotes,
    };
}'

# ============================================
# وحدة Cameras
# ============================================

echo ""
echo "جاري إنشاء وحدة Cameras..."

create_file "$BASE_DIR/lib/cameras/models/camera.dart" 'class Camera {
    final int id;
    final int gateId;
    final String name;
    final String streamUrl;
    final String streamType;
    final bool isActive;
    final String? locationDesc;
    final DateTime? lastHeartbeat;
    final DateTime createdAt;

    Camera({
        required this.id,
        required this.gateId,
        required this.name,
        required this.streamUrl,
        this.streamType = "rtsp",
        this.isActive = true,
        this.locationDesc,
        this.lastHeartbeat,
        required this.createdAt,
    });

    factory Camera.fromJson(Map<String, dynamic> json) {
        return Camera(
            id: json["id"],
            gateId: json["gate_id"],
            name: json["name"],
            streamUrl: json["stream_url"],
            streamType: json["stream_type"] ?? "rtsp",
            isActive: json["is_active"] ?? true,
            locationDesc: json["location_desc"],
            lastHeartbeat: json["last_heartbeat"] != null 
                ? DateTime.parse(json["last_heartbeat"]) 
                : null,
            createdAt: DateTime.parse(json["created_at"]),
        );
    }
}'

create_file "$BASE_DIR/lib/cameras/models/camera_event.dart" 'class CameraEvent {
    final int id;
    final int cameraId;
    final int? permitId;
    final String? snapshotPath;
    final String? videoClipPath;
    final DateTime timestamp;
    final String? eventType;

    CameraEvent({
        required this.id,
        required this.cameraId,
        this.permitId,
        this.snapshotPath,
        this.videoClipPath,
        required this.timestamp,
        this.eventType,
    });

    factory CameraEvent.fromJson(Map<String, dynamic> json) {
        return CameraEvent(
            id: json["id"],
            cameraId: json["camera_id"],
            permitId: json["permit_id"],
            snapshotPath: json["snapshot_path"],
            videoClipPath: json["video_clip_path"],
            timestamp: DateTime.parse(json["timestamp"]),
            eventType: json["event_type"],
        );
    }
}'

create_file "$BASE_DIR/lib/cameras/models/stream_info.dart" 'class StreamInfo {
    final int cameraId;
    final String streamType;
    final String streamUrl;
    final String? snapshotUrl;
    final bool isOnline;
    final DateTime? lastHeartbeat;

    StreamInfo({
        required this.cameraId,
        required this.streamType,
        required this.streamUrl,
        this.snapshotUrl,
        this.isOnline = true,
        this.lastHeartbeat,
    });

    factory StreamInfo.fromJson(Map<String, dynamic> json) {
        return StreamInfo(
            cameraId: json["camera_id"],
            streamType: json["stream_type"] ?? "hls",
            streamUrl: json["stream_url"],
            snapshotUrl: json["snapshot_url"],
            isOnline: json["is_online"] ?? true,
            lastHeartbeat: json["last_heartbeat"] != null 
                ? DateTime.parse(json["last_heartbeat"]) 
                : null,
        );
    }
}'

# ============================================
# وحدة Scanner
# ============================================

echo ""
echo "جاري إنشاء وحدة Scanner..."

create_file "$BASE_DIR/lib/scanner/models/scan_result.dart" 'import "permit.dart";

class ScanResult {
    final ScanStatus status;
    final String? rawValue;
    final String? permitCode;
    final Permit? permit;
    final String? errorMessage;

    ScanResult({
        required this.status,
        this.rawValue,
        this.permitCode,
        this.permit,
        this.errorMessage,
    });

    static ScanResult success(String value, {Permit? permit}) {
        return ScanResult(
            status: ScanStatus.success,
            rawValue: value,
            permitCode: value,
            permit: permit,
        );
    }

    static ScanResult notFound(String value) {
        return ScanResult(
            status: ScanStatus.notFound,
            rawValue: value,
            errorMessage: "لم يتم العثور على سند بهذا الرمز",
        );
    }

    static ScanResult expired(String value) {
        return ScanResult(
            status: ScanStatus.expired,
            rawValue: value,
            errorMessage: "السند منتهي الصلاحية",
        );
    }

    static ScanResult alreadyExited(String value) {
        return ScanResult(
            status: ScanStatus.alreadyExited,
            rawValue: value,
            errorMessage: "السند مسجل عليه خروج مسبقاً",
        );
    }

    static ScanResult error(String message) {
        return ScanResult(
            status: ScanStatus.error,
            errorMessage: message,
        );
    }
}

enum ScanStatus {
    success,
    notFound,
    expired,
    alreadyExited,
    error,
}

class ScanMode {
    static const String entry = "entry";
    static const String exit = "exit";
    static const String verify = "verify";
}
}'

# ============================================
# وحدة Reports
# ============================================

echo ""
echo "جاري إنشاء وحدة Reports..."

create_file "$BASE_DIR/lib/reports/models/report_params.dart" 'class ReportParams {
    final DateTime? from;
    final DateTime? to;
    final int? cityId;
    final int? gateId;
    final String? groupBy;
    final String? alertType;
    final String? severity;

    ReportParams({
        this.from,
        this.to,
        this.cityId,
        this.gateId,
        this.groupBy,
        this.alertType,
        this.severity,
    });

    Map<String, dynamic> toQueryParams() {
        final params = <String, dynamic>{};
        if (from != null) params["from"] = from!.toIso8601String();
        if (to != null) params["to"] = to!.toIso8601String();
        if (cityId != null) params["city_id"] = cityId;
        if (gateId != null) params["gate_id"] = gateId;
        if (groupBy != null) params["group_by"] = groupBy;
        if (alertType != null) params["type"] = alertType;
        if (severity != null) params["severity"] = severity;
        return params;
    }
}'

create_file "$BASE_DIR/lib/reports/models/movement_report.dart" 'class MovementReport {
    final ReportPeriod period;
    final MovementSummary summary;
    final List<CityBreakdown> byCity;
    final List<HourlyBreakdown> byHour;
    final TrendData trends;

    MovementReport({
        required this.period,
        required this.summary,
        required this.byCity,
        required this.byHour,
        required this.trends,
    });

    factory MovementReport.fromJson(Map<String, dynamic> json) {
        return MovementReport(
            period: ReportPeriod.fromJson(json["period"]),
            summary: MovementSummary.fromJson(json["summary"]),
            byCity: (json["by_city"] as List)
                .map((e) => CityBreakdown.fromJson(e))
                .toList(),
            byHour: (json["by_hour"] as List)
                .map((e) => HourlyBreakdown.fromJson(e))
                .toList(),
            trends: TrendData.fromJson(json["trends"]),
        );
    }
}

class ReportPeriod {
    final DateTime from;
    final DateTime to;

    ReportPeriod({required this.from, required this.to});

    factory ReportPeriod.fromJson(Map<String, dynamic> json) {
        return ReportPeriod(
            from: DateTime.parse(json["from"]),
            to: DateTime.parse(json["to"]),
        );
    }
}

class MovementSummary {
    final int totalEntries;
    final int totalExits;
    final int activePermits;
    final int expiredPermits;
    final double avgDurationHours;
    final double earlyExitsPercentage;

    MovementSummary({
        required this.totalEntries,
        required this.totalExits,
        required this.activePermits,
        required this.expiredPermits,
        required this.avgDurationHours,
        required this.earlyExitsPercentage,
    });

    factory MovementSummary.fromJson(Map<String, dynamic> json) {
        return MovementSummary(
            totalEntries: json["total_entries"],
            totalExits: json["total_exits"],
            activePermits: json["active_permits"],
            expiredPermits: json["expired_permits"],
            avgDurationHours: (json["avg_duration_hours"] as num).toDouble(),
            earlyExitsPercentage: (json["early_exits_percentage"] as num).toDouble(),
        );
    }
}

class CityBreakdown {
    final int cityId;
    final String cityName;
    final int entries;
    final int exits;

    CityBreakdown({
        required this.cityId,
        required this.cityName,
        required this.entries,
        required this.exits,
    });

    factory CityBreakdown.fromJson(Map<String, dynamic> json) {
        return CityBreakdown(
            cityId: json["city_id"],
            cityName: json["city_name"],
            entries: json["entries"],
            exits: json["exits"],
        );
    }
}

class HourlyBreakdown {
    final int hour;
    final int entries;
    final int exits;

    HourlyBreakdown({
        required this.hour,
        required this.entries,
        required this.exits,
    });

    factory HourlyBreakdown.fromJson(Map<String, dynamic> json) {
        return HourlyBreakdown(
            hour: json["hour"],
            entries: json["entries"],
            exits: json["exits"],
        );
    }
}

class TrendData {
    final double entriesGrowth;
    final double exitsGrowth;

    TrendData({required this.entriesGrowth, required this.exitsGrowth});

    factory TrendData.fromJson(Map<String, dynamic> json) {
        return TrendData(
            entriesGrowth: (json["entries_growth"] as num).toDouble(),
            exitsGrowth: (json["exits_growth"] as num).toDouble(),
        );
    }
}'

create_file "$BASE_DIR/lib/reports/models/alerts_report.dart" 'class AlertsReport {
    final ReportPeriod period;
    final AlertsSummary summary;
    final List<AlertTypeBreakdown> byType;
    final List<TrendPoint> trend;

    AlertsReport({
        required this.period,
        required this.summary,
        required this.byType,
        required this.trend,
    });

    factory AlertsReport.fromJson(Map<String, dynamic> json) {
        return AlertsReport(
            period: ReportPeriod.fromJson(json["period"]),
            summary: AlertsSummary.fromJson(json["summary"]),
            byType: (json["by_type"] as List)
                .map((e) => AlertTypeBreakdown.fromJson(e))
                .toList(),
            trend: (json["trend"] as List)
                .map((e) => TrendPoint.fromJson(e))
                .toList(),
        );
    }
}

class AlertsSummary {
    final int totalAlerts;
    final int critical;
    final int medium;
    final int low;
    final int resolved;
    final int pending;
    final double resolutionRate;
    final double avgResolutionTimeHours;

    AlertsSummary({
        required this.totalAlerts,
        required this.critical,
        required this.medium,
        required this.low,
        required this.resolved,
        required this.pending,
        required this.resolutionRate,
        required this.avgResolutionTimeHours,
    });

    factory AlertsSummary.fromJson(Map<String, dynamic> json) {
        return AlertsSummary(
            totalAlerts: json["total_alerts"],
            critical: json["critical"],
            medium: json["medium"],
            low: json["low"],
            resolved: json["resolved"],
            pending: json["pending"],
            resolutionRate: (json["resolution_rate"] as num).toDouble(),
            avgResolutionTimeHours: (json["avg_resolution_time_hours"] as num).toDouble(),
        );
    }
}

class AlertTypeBreakdown {
    final String type;
    final int count;
    final int resolved;

    AlertTypeBreakdown({
        required this.type,
        required this.count,
        required this.resolved,
    });

    factory AlertTypeBreakdown.fromJson(Map<String, dynamic> json) {
        return AlertTypeBreakdown(
            type: json["type"],
            count: json["count"],
            resolved: json["resolved"],
        );
    }
}

class TrendPoint {
    final String date;
    final int alerts;

    TrendPoint({required this.date, required this.alerts});

    factory TrendPoint.fromJson(Map<String, dynamic> json) {
        return TrendPoint(
            date: json["date"],
            alerts: json["alerts"],
        );
    }
}'

create_file "$BASE_DIR/lib/reports/models/report_export_format.dart" 'enum ReportExportFormat {
    pdf,
    excel,
    csv,
    json;

    String get displayName {
        switch (this) {
            case pdf: return "PDF";
            case excel: return "Excel";
            case csv: return "CSV";
            case json: return "JSON";
        }
    }

    String get extension {
        switch (this) {
            case pdf: return "pdf";
            case excel: return "xlsx";
            case csv: return "csv";
            case json: return "json";
        }
    }

    String get mimeType {
        switch (this) {
            case pdf: return "application/pdf";
            case excel: return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
            case csv: return "text/csv";
            case json: return "application/json";
        }
    }
}'

# ============================================
# ملفات التكوين الأساسية
# ============================================

create_file "$BASE_DIR/pubspec.yaml" 'name: gateflow_app
description: نظام GateFlow لإدارة حركة المسافرين والسندات الزمنية
version: 1.0.0+1

environment:
  sdk: ">=3.0.0 <4.0.0"
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter
  
  flutter_bloc: ^8.1.3
  bloc_concurrency: ^0.2.2
  
  dio: ^5.4.0
  dio_http_cache: ^0.4.1
  connectivity_plus: ^5.0.2
  
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  shared_preferences: ^2.2.2
  
  mobile_scanner: ^3.5.0
  qr_flutter: ^4.1.0
  barcode_scan2: ^4.2.4
  
  camera: ^0.10.5
  video_player: ^2.8.2
  
  flutter_local_notifications: ^16.3.0
  awesome_notifications: ^0.9.2
  
  intl: ^0.18.1
  date_format: ^2.0.7
  
  uuid: ^4.2.1
  crypto: ^3.0.3
  password_strength: ^0.2.0
  permission_handler: ^11.2.0
  
  flutter_svg: ^2.0.9
  lucide_icons: ^0.3.0
  
  pdf: ^3.10.7
  excel: ^2.1.0
  share_plus: ^7.2.1
  
  logger: ^2.0.2+1
  
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.1
  build_runner: ^2.4.8
  bloc_test: ^9.1.5
  mockito: ^5.4.4
  integration_test:
    sdk: flutter

flutter:
  uses-material-design: true
  
  assets:
    - assets/images/
    - assets/icons/
    - assets/fonts/
    - assets/translations/
  
  fonts:
    - family: Cairo
      fonts:
        - asset: assets/fonts/Cairo/Cairo-Regular.ttf
        - asset: assets/fonts/Cairo/Cairo-Bold.ttf
          weight: 700
        - asset: assets/fonts/Cairo/Cairo-SemiBold.ttf
          weight: 600
    - family: Inter
      fonts:
        - asset: assets/fonts/Inter/Inter-Regular.ttf
        - asset: assets/fonts/Inter/Inter-Bold.ttf
          weight: 700
        - asset: assets/fonts/Inter/Inter-SemiBold.ttf
          weight: 600'

create_file "$BASE_DIR/analysis_options.yaml" 'include: package:flutter_lints/flutter.yaml

linter:
  rules:
    prefer_const_constructors: false
    prefer_const_literals_to_create_immutables: false
    avoid_print: false

analyzer:
  exclude:
    - "build/**"
    - ".dart_tool/**"
    - "**/*.g.dart"
    - "**/*.freezed.dart"'

create_file "$BASE_DIR/README.md" '# GateFlow System

نظام GateFlow لإدارة حركة المسافرين والسندات الزمنية عبر نقاط متعددة.

## الوصف

منصة إدارية رقمية متكاملة تهدف إلى إدارة حركة المسافرين عبر نقاط دخول متعددة، مع التركيز على:

- **إصدار السندات الزمنية الرقمية** - إنشاء وإدارة سندات الدخول والخروج
- **التحقق الآلي من قائمة المطلوبين** - مطابقة فورية مع قواعد البيانات
- **التكامل مع كاميرات المراقبة** - توثيق بصري للحركة
- **العمل دون اتصال بالإنترنت** - Offline-first architecture

## التقنيات

- **Frontend**: Flutter (Android, iOS, Web)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL / SQLite
- **Authentication**: JWT with RBAC

## الأدوار

| الدور | الوصف |
|-------|-------|
| System Admin | إدارة كاملة للنظام |
| Supervisor | مراقبة وتقارير وتنبيهات |
| Entry Officer | إدخال مسافرين وإصدار سندات |
| Exit Officer | تسجيل خروج المسافرين |
| Viewer | عرض فقط |

## هيكل المشروع

```
gateflow_app/
├── android/          # ملفات Android الأصلية
├── ios/              # ملفات iOS الأصلية
├── web/              # ملفات Web
├── lib/              # الكود المصدري Flutter
│   ├── core/         # المكونات الأساسية المشتركة
│   ├── auth/         # وحدة المصادقة
│   ├── travelers/    # وحدة المسافرين
│   ├── permits/      # وحدة السندات
│   ├── scanner/      # وحدة المسح الضوئي
│   ├── cameras/      # وحدة الكاميرات
│   ├── alerts/       # وحدة التنبيهات
│   ├── reports/      # وحدة التقارير
│   └── ...
├── assets/           # الملفات الثابتة
├── test/             # اختبارات الوحدة
└── pubspec.yaml      # تبعيات المشروع
```

## البدء

### المتطلبات

- Flutter SDK 3.0+
- Dart SDK 3.0+
- Android Studio / VS Code

### التثبيت

```bash
# استنساخ المستودع
git clone https://github.com/raedthawaba/gateflow_app.git

# الدخول للمجلد
cd gateflow_app

# تثبيت التبعيات
flutter pub get

# تشغيل التطبيق
flutter run
```

## الترخيص

MIT License

---

**GateFlow** - إدارة آمنة ومنظمة لحركة المسافرين
'

create_file "$BASE_DIR/.gitignore" '# Flutter
.DS_Store
.dart_tool/
.packages
build/
.pub/
.idea/
.vscode/
*.iml
*.lock
pubspec.lock

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.venv/
venv/
ENV/
*.egg-info/
dist/
build/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
Thumbs.db
.DS_Store

# Logs
*.log
logs/

# Temp files
tmp/
temp/'

# ============================================
# إنشاء ملفات placeholder فارغة للمجلدات المتبقية
# ============================================

echo ""
echo "جاري إنشاء الملفات المتبقية..."

# إنشاء ملفات placeholders للتأكد من وجود جميع المجلدات
find . -type d -empty -exec touch {}/.gitkeep \;

echo ""
echo "=========================================="
echo "  تم إنشاء هيكل المشروع بنجاح!"
echo "=========================================="
echo ""
echo "الهيكل الكامل جاهز للرفع إلى GitHub"
echo ""

# إنهاء السكريبت
exit 0
