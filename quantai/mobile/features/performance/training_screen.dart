import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/widgets/ambient_background.dart';
import '../../shared/widgets/liquid_glass_card.dart';
import 'training_provider.dart';

class TrainingScreen extends ConsumerWidget {
  const TrainingScreen({super.key});

  Color _statusColor(String status) {
    switch (status) {
      case 'training':
        return const Color(0xFF60A5FA);
      case 'completed':
        return const Color(0xFF22C55E);
      case 'failed':
        return const Color(0xFFEF4444);
      default:
        return const Color(0xFF94A3B8);
    }
  }

  Color _healthColor(String health) {
    switch (health) {
      case 'good':
        return const Color(0xFF22C55E);
      case 'warning':
        return const Color(0xFFF59E0B);
      case 'bad':
        return const Color(0xFFEF4444);
      default:
        return const Color(0xFF94A3B8);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(trainingProvider);
    final progress = state.totalEpochs > 0 ? state.epoch / state.totalEpochs : 0.0;

    final List<FlSpot> lossSpots = <FlSpot>[];
    final List<FlSpot> valLossSpots = <FlSpot>[];
    for (final p in state.history) {
      lossSpots.add(FlSpot(p.epoch.toDouble(), p.loss));
      valLossSpots.add(FlSpot(p.epoch.toDouble(), p.valLoss));
    }

    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: <Widget>[
              const SizedBox(height: 8),
              const Text(
                'Training Monitor',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 12),
              LiquidGlassCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: <Widget>[
                        Text('Stage: ${state.stage.toUpperCase()}'),
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 280),
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                          decoration: BoxDecoration(
                            color: _statusColor(state.status).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: Text(
                            state.status.toUpperCase(),
                            style: TextStyle(color: _statusColor(state.status), fontWeight: FontWeight.w700),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Center(
                      child: SizedBox(
                        height: 110,
                        width: 110,
                        child: Stack(
                          fit: StackFit.expand,
                          children: <Widget>[
                            CircularProgressIndicator(
                              value: progress.clamp(0, 1),
                              strokeWidth: 10,
                              backgroundColor: const Color(0x33FFFFFF),
                            ),
                            Center(
                              child: Text('${(progress * 100).toStringAsFixed(0)}%'),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text('Epoch ${state.epoch}/${state.totalEpochs}'),
                    const SizedBox(height: 8),
                    Text('Loss: ${state.loss.toStringAsFixed(5)} | Val: ${state.valLoss.toStringAsFixed(5)}'),
                    Text('Accuracy: ${(state.accuracy * 100).toStringAsFixed(2)}% | F1: ${state.f1.toStringAsFixed(4)}'),
                    const SizedBox(height: 8),
                    Row(
                      children: <Widget>[
                        Text('Health: ', style: TextStyle(color: Colors.white.withOpacity(0.75))),
                        Text(
                          state.health.toUpperCase(),
                          style: TextStyle(color: _healthColor(state.health), fontWeight: FontWeight.w700),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          state.overfitting ? 'OVERFITTING' : 'STABLE',
                          style: TextStyle(
                            color: state.overfitting ? const Color(0xFFF59E0B) : const Color(0xFF22C55E),
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              LiquidGlassCard(
                child: SizedBox(
                  height: 220,
                  child: LineChart(
                    LineChartData(
                      gridData: const FlGridData(show: true),
                      titlesData: const FlTitlesData(show: true),
                      borderData: FlBorderData(show: false),
                      lineBarsData: <LineChartBarData>[
                        LineChartBarData(
                          spots: lossSpots,
                          isCurved: true,
                          barWidth: 2.5,
                          color: const Color(0xFFA78BFA),
                          dotData: const FlDotData(show: false),
                        ),
                        LineChartBarData(
                          spots: valLossSpots,
                          isCurved: true,
                          barWidth: 2.5,
                          color: const Color(0xFF60A5FA),
                          dotData: const FlDotData(show: false),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
