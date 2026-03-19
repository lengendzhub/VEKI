import 'package:flutter/material.dart';

import '../../models/proposal_model.dart';
import '../../shared/layout/app_scaffold_shell.dart';
import '../../shared/widgets/liquid_glass_card.dart';

class ProposalsScreen extends StatelessWidget {
  const ProposalsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const proposals = <ProposalModel>[
      ProposalModel(symbol: 'EURUSD', direction: 'long', entry: 1.0840, stopLoss: 1.0810, takeProfit: 1.0900, confidence: 0.74),
      ProposalModel(symbol: 'XAUUSD', direction: 'short', entry: 3205.0, stopLoss: 3220.0, takeProfit: 3175.0, confidence: 0.68),
    ];

    return AppScaffoldShell(
      title: 'Proposals',
      child: ListView.separated(
        itemCount: proposals.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (context, i) {
          final p = proposals[i];
          return LiquidGlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text('${p.symbol} ${p.direction.toUpperCase()}', style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                Text('Entry ${p.entry} | SL ${p.stopLoss} | TP ${p.takeProfit}'),
                Text('Confidence ${(p.confidence * 100).toStringAsFixed(1)}%'),
              ],
            ),
          );
        },
      ),
    );
  }
}
