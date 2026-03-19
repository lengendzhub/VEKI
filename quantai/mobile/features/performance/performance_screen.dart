import 'package:flutter/material.dart';

import '../../models/performance_snapshot.dart';
import '../../shared/layout/app_scaffold_shell.dart';
import '../../shared/widgets/liquid_glass_card.dart';
import '../../utils/formatters.dart';

class PerformanceScreen extends StatelessWidget {
  const PerformanceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const snapshot = PerformanceSnapshot(
      winRate: 0.58,
      profitFactor: 1.71,
      maxDrawdown: 0.067,
      sharpe: 1.43,
      pnlToday: 324.61,
    );

    return AppScaffoldShell(
      title: 'Performance',
      child: ListView(
        children: <Widget>[
          LiquidGlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                const Text('Performance Snapshot', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                const SizedBox(height: 12),
                Text('Win Rate: ${pct(snapshot.winRate)}'),
                Text('Profit Factor: ${snapshot.profitFactor.toStringAsFixed(2)}'),
                Text('Max Drawdown: ${pct(snapshot.maxDrawdown)}'),
                Text('Sharpe: ${snapshot.sharpe.toStringAsFixed(2)}'),
                Text('PnL Today: ${money(snapshot.pnlToday)}'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
