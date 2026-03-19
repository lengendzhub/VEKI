import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/auth_provider.dart';
import '../../shared/layout/app_scaffold_shell.dart';
import '../../shared/widgets/liquid_glass_card.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  bool _telegram = true;
  bool _trainingAlerts = true;
  bool _autoExecute = false;

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    return AppScaffoldShell(
      title: 'Settings',
      child: ListView(
        children: <Widget>[
          LiquidGlassCard(
            child: Column(
              children: <Widget>[
                SwitchListTile(
                  title: const Text('Telegram Alerts'),
                  value: _telegram,
                  onChanged: (v) => setState(() => _telegram = v),
                ),
                SwitchListTile(
                  title: const Text('Training Alerts'),
                  value: _trainingAlerts,
                  onChanged: (v) => setState(() => _trainingAlerts = v),
                ),
                SwitchListTile(
                  title: const Text('Auto Execute Approved Trades'),
                  value: _autoExecute,
                  onChanged: (v) => setState(() => _autoExecute = v),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          LiquidGlassCard(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Text(auth.isAuthenticated ? 'Session Active' : 'Session Not Active'),
                OutlinedButton(
                  onPressed: () => ref.read(authProvider.notifier).signOut(),
                  child: const Text('Sign out'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
