// mobile/features/dashboard/dashboard_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../shared/widgets/ambient_background.dart';
import '../../shared/widgets/glass_card.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                const GlassCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text('QuantAI Dashboard', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
                      SizedBox(height: 8),
                      Text('Live regime, news countdown, and execution control.'),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Expanded(
                  child: ListView(
                    children: <Widget>[
                      const GlassCard(child: Text('Regime: Trend')),
                      const SizedBox(height: 12),
                      const GlassCard(child: Text('News: CPI in 47m')),
                      const SizedBox(height: 12),
                      _navRow(context, 'Auth', '/auth', Icons.verified_user_outlined),
                      const SizedBox(height: 8),
                      _navRow(context, 'Proposals', '/proposals', Icons.tips_and_updates_outlined),
                      const SizedBox(height: 8),
                      _navRow(context, 'Trades', '/trades', Icons.swap_vert_circle_outlined),
                      const SizedBox(height: 8),
                      _navRow(context, 'Backtest', '/backtest', Icons.timeline_outlined),
                      const SizedBox(height: 8),
                      _navRow(context, 'Chart', '/chart', Icons.show_chart),
                      const SizedBox(height: 8),
                      _navRow(context, 'Performance', '/performance', Icons.query_stats),
                      const SizedBox(height: 8),
                      _navRow(context, 'Training Monitor', '/training', Icons.model_training_outlined),
                      const SizedBox(height: 8),
                      _navRow(context, 'Trading Control', '/trading', Icons.tune),
                      const SizedBox(height: 8),
                      _navRow(context, 'Settings', '/settings', Icons.settings_outlined),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _navRow(BuildContext context, String title, String route, IconData icon) {
    return GlassCard(
      child: ListTile(
        contentPadding: EdgeInsets.zero,
        leading: Icon(icon),
        title: Text(title),
        trailing: const Icon(Icons.arrow_forward_ios, size: 14),
        onTap: () => context.go(route),
      ),
    );
  }
}
