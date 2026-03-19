// mobile/lib/app.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../core/theme/app_theme.dart';
import '../features/auth/auth_screen.dart';
import '../features/backtest/backtest_screen.dart';
import '../features/chart/chart_screen.dart';
import '../features/dashboard/dashboard_screen.dart';
import '../features/performance/performance_screen.dart';
import '../features/proposals/proposals_screen.dart';
import '../features/performance/training_screen.dart';
import '../features/settings/settings_screen.dart';
import '../features/trading/trading_screen.dart';
import '../features/trades/trades_screen.dart';

class QuantAIApp extends StatelessWidget {
  const QuantAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    final router = GoRouter(
      initialLocation: '/',
      routes: <RouteBase>[
        GoRoute(path: '/', builder: (context, state) => const DashboardScreen()),
        GoRoute(path: '/auth', builder: (context, state) => const AuthScreen()),
        GoRoute(path: '/proposals', builder: (context, state) => const ProposalsScreen()),
        GoRoute(path: '/trades', builder: (context, state) => const TradesScreen()),
        GoRoute(path: '/backtest', builder: (context, state) => const BacktestScreen()),
        GoRoute(path: '/chart', builder: (context, state) => const ChartScreen()),
        GoRoute(path: '/performance', builder: (context, state) => const PerformanceScreen()),
        GoRoute(path: '/training', builder: (context, state) => const TrainingScreen()),
        GoRoute(path: '/trading', builder: (context, state) => const TradingScreen()),
        GoRoute(path: '/settings', builder: (context, state) => const SettingsScreen()),
      ],
    );

    return MaterialApp.router(
      title: 'QuantAI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      routerConfig: router,
    );
  }
}
