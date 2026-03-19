import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/layout/app_scaffold_shell.dart';
import '../../shared/widgets/glass_card.dart';
import 'auth_provider.dart';

class AuthScreen extends ConsumerStatefulWidget {
  const AuthScreen({super.key});

  @override
  ConsumerState<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends ConsumerState<AuthScreen> {
  final TextEditingController _email = TextEditingController(text: 'trader@quantai.dev');
  final TextEditingController _password = TextEditingController();

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    return AppScaffoldShell(
      title: 'Auth',
      child: ListView(
        children: <Widget>[
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                const Text('Authentication', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                const SizedBox(height: 12),
                TextField(controller: _email, decoration: const InputDecoration(labelText: 'Email')),
                const SizedBox(height: 10),
                TextField(
                  controller: _password,
                  obscureText: true,
                  decoration: const InputDecoration(labelText: 'Password'),
                ),
                const SizedBox(height: 12),
                Row(
                  children: <Widget>[
                    ElevatedButton(
                      onPressed: auth.loading
                          ? null
                          : () => ref
                              .read(authProvider.notifier)
                              .signIn(email: _email.text, password: _password.text),
                      child: Text(auth.loading ? 'Signing In...' : 'Sign In'),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: () => ref.read(authProvider.notifier).signOut(),
                      child: const Text('Sign Out'),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text('Status: ${auth.isAuthenticated ? 'Authenticated' : 'Signed out'}'),
                if (auth.error != null) ...<Widget>[
                  const SizedBox(height: 8),
                  Text(auth.error!, style: const TextStyle(color: Color(0xFFEF4444))),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
