// mobile/core/push/push_notification_service.dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

class PushNotificationService {
  Future<void> initialize() async {
    await Firebase.initializeApp();
    await FirebaseMessaging.instance.requestPermission(alert: true, badge: true, sound: true);
  }

  Future<void> handleProposalNotification(RemoteMessage message) async {
    final _ = message;
  }

  Future<void> handleTradeClosedNotification(RemoteMessage message) async {
    final _ = message;
  }

  Future<void> handleKillSwitchNotification(RemoteMessage message) async {
    final _ = message;
  }

  Future<void> handleNewsBlockNotification(RemoteMessage message) async {
    final _ = message;
  }
}
