import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../widgets/ambient_background.dart';

class AppScaffoldShell extends StatelessWidget {
  const AppScaffoldShell({
    super.key,
    required this.title,
    required this.child,
    this.actions,
  });

  final String title;
  final Widget child;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        actions: actions,
      ),
      drawer: Drawer(
        child: ListView(
          children: <Widget>[
            const DrawerHeader(child: Text('QuantAI Navigation')),
            _item(context, 'Dashboard', '/'),
            _item(context, 'Auth', '/auth'),
            _item(context, 'Proposals', '/proposals'),
            _item(context, 'Trades', '/trades'),
            _item(context, 'Backtest', '/backtest'),
            _item(context, 'Chart', '/chart'),
            _item(context, 'Performance', '/performance'),
            _item(context, 'Training', '/training'),
            _item(context, 'Trading', '/trading'),
            _item(context, 'Settings', '/settings'),
          ],
        ),
      ),
      body: AmbientBackground(
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: child,
          ),
        ),
      ),
    );
  }

  Widget _item(BuildContext context, String label, String route) {
    return ListTile(
      title: Text(label),
      onTap: () {
        Navigator.of(context).pop();
        context.go(route);
      },
    );
  }
}
