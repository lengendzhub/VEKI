import 'package:flutter/material.dart';

import 'glass_card.dart';

class LiquidGlassCard extends StatelessWidget {
  const LiquidGlassCard({super.key, required this.child, this.padding = const EdgeInsets.all(14)});

  final Widget child;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: <Color>[Color(0x774C1D95), Color(0x445B21B6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
      ),
      child: GlassCard(padding: padding, child: child),
    );
  }
}
