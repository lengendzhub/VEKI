import 'package:flutter/material.dart';

import '../../shared/layout/app_scaffold_shell.dart';
import '../../shared/widgets/liquid_glass_card.dart';

class BacktestScreen extends StatelessWidget {
  const BacktestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AppScaffoldShell(
      title: 'Backtest',
      child: ListView(
        children: const <Widget>[
          LiquidGlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text('Strategy Replay', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                SizedBox(height: 8),
                Text('Period: 2024-01-01 to 2025-01-01'),
                SizedBox(height: 8),
                Text('Trades: 482 | Win Rate: 58.3% | PF: 1.72'),
                SizedBox(height: 8),
                Text('Max DD: 6.8% | Net PnL: +12.4%'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
