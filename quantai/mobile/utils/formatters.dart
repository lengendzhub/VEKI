import 'package:intl/intl.dart';

final NumberFormat _moneyFmt = NumberFormat.currency(symbol: r'$', decimalDigits: 2);
final NumberFormat _pctFmt = NumberFormat('0.00%');

String money(double value) => _moneyFmt.format(value);

String pct(double value) => _pctFmt.format(value);

String pipDelta(double value) {
  final sign = value >= 0 ? '+' : '';
  return '$sign${value.toStringAsFixed(1)} pips';
}
