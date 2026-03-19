// mobile/core/theme/app_theme.dart
import 'package:flutter/material.dart';

import 'colors.dart';

class AppTheme {
  static ThemeData get light => ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: AppColors.bgA,
        colorScheme: const ColorScheme.dark(
          primary: AppColors.trend,
          secondary: AppColors.range,
          error: AppColors.volatile,
        ),
        cardTheme: const CardTheme(
          color: AppColors.glass,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(18)),
          ),
        ),
      );
}
