class TradeModel {
  const TradeModel({
    required this.symbol,
    required this.side,
    required this.entry,
    required this.stopLoss,
    required this.takeProfit,
    required this.size,
    required this.status,
    required this.openedAt,
  });

  final String symbol;
  final String side;
  final double entry;
  final double stopLoss;
  final double takeProfit;
  final double size;
  final String status;
  final DateTime openedAt;

  factory TradeModel.fromJson(Map<String, dynamic> json) {
    return TradeModel(
      symbol: (json['symbol'] as String?) ?? 'EURUSD',
      side: (json['side'] as String?) ?? 'long',
      entry: (json['entry'] as num?)?.toDouble() ?? 0,
      stopLoss: (json['stop_loss'] as num?)?.toDouble() ?? 0,
      takeProfit: (json['take_profit'] as num?)?.toDouble() ?? 0,
      size: (json['size'] as num?)?.toDouble() ?? 0,
      status: (json['status'] as String?) ?? 'open',
      openedAt: DateTime.tryParse((json['opened_at'] as String?) ?? '') ?? DateTime.now(),
    );
  }
}
