// mobile/shared/widgets/ambient_background.dart
import 'package:flutter/material.dart';

class AmbientBackground extends StatelessWidget {
  const AmbientBackground({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: <Color>[Color(0xFF0F172A), Color(0xFF1E293B)],
        ),
      ),
      child: Stack(
        children: <Widget>[
          Positioned(top: -100, right: -50, child: _orb(const Color(0x3322D3EE), 280)),
          Positioned(bottom: -120, left: -80, child: _orb(const Color(0x333B82F6), 320)),
          child,
        ],
      ),
    );
  }

  Widget _orb(Color color, double size) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );
  }
}
