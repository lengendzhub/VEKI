import 'package:flutter/material.dart';

import '../../shared/layout/app_scaffold_shell.dart';
import '../../shared/widgets/liquid_glass_card.dart';

class TradingScreen extends StatelessWidget {
  const TradingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AppScaffoldShell(
      title: 'Trading Control',
      child: ListView(
        children: <Widget>[
          const LiquidGlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text('Execution Engine', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                SizedBox(height: 8),
                Text('Mode: Semi-auto'),
                Text('Kill Switch: OFF'),
                Text('Max Risk/Trade: 1.0%'),
                Text('Max Spread: 2.0 pips'),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: <Widget>[
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Enable Trading'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.stop_circle_outlined),
                  label: const Text('Kill Switch'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
