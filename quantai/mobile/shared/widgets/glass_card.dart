// mobile/shared/widgets/glass_card.dart
import 'dart:ui';

import 'package:flutter/material.dart';

class GlassCard extends StatelessWidget {
  const GlassCard({super.key, required this.child, this.padding = const EdgeInsets.all(14)});

  final Widget child;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(18),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 14, sigmaY: 14),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: <Color>[Color(0x5539495A), Color(0x3339495A)],
            ),
            border: Border.all(color: const Color(0x55FFFFFF)),
            borderRadius: BorderRadius.circular(18),
          ),
          child: child,
        ),
      ),
    );
  }
}
