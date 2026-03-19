import 'package:flutter/material.dart';

import '../../models/trade_model.dart';
import '../../shared/layout/app_scaffold_shell.dart';
import '../../shared/widgets/liquid_glass_card.dart';
import '../../utils/formatters.dart';

class TradesScreen extends StatelessWidget {
  const TradesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final trades = <TradeModel>[
      TradeModel(
        symbol: 'EURUSD',
        side: 'long',
        entry: 1.0842,
        stopLoss: 1.0820,
        takeProfit: 1.0898,
        size: 0.5,
        status: 'open',
        openedAt: DateTime.now().subtract(const Duration(minutes: 42)),
      ),
      TradeModel(
        symbol: 'XAUUSD',
        side: 'short',
        entry: 3208.0,
        stopLoss: 3221.0,
        takeProfit: 3182.0,
        size: 0.2,
        status: 'open',
        openedAt: DateTime.now().subtract(const Duration(hours: 2, minutes: 16)),
      ),
    ];

    return AppScaffoldShell(
      title: 'Trades',
      child: ListView.separated(
        itemCount: trades.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (_, i) {
          final t = trades[i];
          final pips = (t.takeProfit - t.entry) * 10000;
          return LiquidGlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text('${t.symbol} ${t.side.toUpperCase()} · ${t.status.toUpperCase()}', style: const TextStyle(fontWeight: FontWeight.w700)),
                const SizedBox(height: 6),
                Text('Entry ${t.entry} | SL ${t.stopLoss} | TP ${t.takeProfit}'),
                Text('Target ${pipDelta(pips)} | Size ${t.size.toStringAsFixed(2)} lots'),
              ],
            ),
          );
        },
      ),
    );
  }
}
