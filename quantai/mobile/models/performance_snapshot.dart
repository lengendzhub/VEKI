class PerformanceSnapshot {
  const PerformanceSnapshot({
    required this.winRate,
    required this.profitFactor,
    required this.maxDrawdown,
    required this.sharpe,
    required this.pnlToday,
  });

  final double winRate;
  final double profitFactor;
  final double maxDrawdown;
  final double sharpe;
  final double pnlToday;

  factory PerformanceSnapshot.fromJson(Map<String, dynamic> json) {
    return PerformanceSnapshot(
      winRate: (json['win_rate'] as num?)?.toDouble() ?? 0,
      profitFactor: (json['profit_factor'] as num?)?.toDouble() ?? 0,
      maxDrawdown: (json['max_drawdown'] as num?)?.toDouble() ?? 0,
      sharpe: (json['sharpe'] as num?)?.toDouble() ?? 0,
      pnlToday: (json['pnl_today'] as num?)?.toDouble() ?? 0,
    );
  }
}
