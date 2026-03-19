// mobile/core/network/websocket_service.dart
import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService {
  WebSocketService(this.url);

  final String url;
  WebSocketChannel? _channel;
  final StreamController<Map<String, dynamic>> _controller = StreamController.broadcast();

  Stream<Map<String, dynamic>> get stream => _controller.stream;

  void connect() {
    _channel = WebSocketChannel.connect(Uri.parse(url));
    _channel!.stream.listen((dynamic event) {
      if (event is String) {
        _controller.add(jsonDecode(event) as Map<String, dynamic>);
      }
    }, onError: (_) => reconnect(), onDone: reconnect);
  }

  void send(Map<String, dynamic> payload) {
    _channel?.sink.add(jsonEncode(payload));
  }

  void reconnect() {
    Future<void>.delayed(const Duration(seconds: 2), connect);
  }

  void dispose() {
    _channel?.sink.close();
    _controller.close();
  }
}
