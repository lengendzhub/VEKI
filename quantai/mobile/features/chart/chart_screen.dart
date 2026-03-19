import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../../shared/layout/app_scaffold_shell.dart';
import '../../shared/widgets/liquid_glass_card.dart';

class ChartScreen extends StatelessWidget {
  const ChartScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<FlSpot> series = <FlSpot>[
      const FlSpot(0, 1.0820),
      const FlSpot(1, 1.0840),
      const FlSpot(2, 1.0830),
      const FlSpot(3, 1.0875),
      const FlSpot(4, 1.0860),
      const FlSpot(5, 1.0890),
    ];

    return AppScaffoldShell(
      title: 'Chart',
      child: ListView(
        children: <Widget>[
          const Text('EURUSD 15m', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
          const SizedBox(height: 12),
          LiquidGlassCard(
            child: SizedBox(
              height: 260,
              child: LineChart(
                LineChartData(
                  borderData: FlBorderData(show: false),
                  gridData: const FlGridData(show: true),
                  titlesData: const FlTitlesData(show: true),
                  lineBarsData: <LineChartBarData>[
                    LineChartBarData(
                      spots: series,
                      isCurved: true,
                      barWidth: 3,
                      color: const Color(0xFF22C55E),
                      dotData: const FlDotData(show: false),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
