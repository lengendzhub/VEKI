class ProposalModel {
  const ProposalModel({
    required this.symbol,
    required this.direction,
    required this.entry,
    required this.stopLoss,
    required this.takeProfit,
    required this.confidence,
  });

  final String symbol;
  final String direction;
  final double entry;
  final double stopLoss;
  final double takeProfit;
  final double confidence;

  factory ProposalModel.fromJson(Map<String, dynamic> json) {
    return ProposalModel(
      symbol: (json['symbol'] as String?) ?? 'EURUSD',
      direction: (json['direction'] as String?) ?? 'long',
      entry: (json['entry'] as num?)?.toDouble() ?? 0,
      stopLoss: (json['stop_loss'] as num?)?.toDouble() ?? 0,
      takeProfit: (json['take_profit'] as num?)?.toDouble() ?? 0,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
    );
  }
}
