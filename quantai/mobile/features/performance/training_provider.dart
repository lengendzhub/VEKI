import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/websocket_service.dart';

class TrainingPoint {
  const TrainingPoint({
    required this.epoch,
    required this.totalEpochs,
    required this.loss,
    required this.valLoss,
    required this.accuracy,
    required this.f1,
  });

  final int epoch;
  final int totalEpochs;
  final double loss;
  final double valLoss;
  final double accuracy;
  final double f1;
}

class TrainingStateModel {
  const TrainingStateModel({
    required this.stage,
    required this.status,
    required this.epoch,
    required this.totalEpochs,
    required this.loss,
    required this.valLoss,
    required this.accuracy,
    required this.f1,
    required this.health,
    required this.overfitting,
    required this.history,
  });

  final String stage;
  final String status;
  final int epoch;
  final int totalEpochs;
  final double loss;
  final double valLoss;
  final double accuracy;
  final double f1;
  final String health;
  final bool overfitting;
  final List<TrainingPoint> history;

  factory TrainingStateModel.initial() {
    return const TrainingStateModel(
      stage: 'idle',
      status: 'idle',
      epoch: 0,
      totalEpochs: 0,
      loss: 0,
      valLoss: 0,
      accuracy: 0,
      f1: 0,
      health: 'unknown',
      overfitting: false,
      history: <TrainingPoint>[],
    );
  }

  TrainingStateModel copyWith({
    String? stage,
    String? status,
    int? epoch,
    int? totalEpochs,
    double? loss,
    double? valLoss,
    double? accuracy,
    double? f1,
    String? health,
    bool? overfitting,
    List<TrainingPoint>? history,
  }) {
    return TrainingStateModel(
      stage: stage ?? this.stage,
      status: status ?? this.status,
      epoch: epoch ?? this.epoch,
      totalEpochs: totalEpochs ?? this.totalEpochs,
      loss: loss ?? this.loss,
      valLoss: valLoss ?? this.valLoss,
      accuracy: accuracy ?? this.accuracy,
      f1: f1 ?? this.f1,
      health: health ?? this.health,
      overfitting: overfitting ?? this.overfitting,
      history: history ?? this.history,
    );
  }
}

class TrainingNotifier extends StateNotifier<TrainingStateModel> {
  TrainingNotifier(this._ws) : super(TrainingStateModel.initial()) {
    _ws.connect();
    _sub = _ws.stream.listen(_onMessage);
  }

  final WebSocketService _ws;
  StreamSubscription<Map<String, dynamic>>? _sub;

  void _onMessage(Map<String, dynamic> message) {
    if (message['type'] != 'training_update') {
      return;
    }
    final dynamic dataRaw = message['data'];
    if (dataRaw is! Map<String, dynamic>) {
      return;
    }
    final data = dataRaw;

    final p = TrainingPoint(
      epoch: (data['epoch'] as num?)?.toInt() ?? 0,
      totalEpochs: (data['total_epochs'] as num?)?.toInt() ?? 0,
      loss: (data['loss'] as num?)?.toDouble() ?? 0,
      valLoss: (data['val_loss'] as num?)?.toDouble() ?? 0,
      accuracy: (data['accuracy'] as num?)?.toDouble() ?? 0,
      f1: (data['f1_score'] as num?)?.toDouble() ?? 0,
    );

    final List<TrainingPoint> history = <TrainingPoint>[...state.history];
    if ((data['status'] as String?) == 'training') {
      history.add(p);
      if (history.length > 200) {
        history.removeRange(0, history.length - 200);
      }
    }

    state = state.copyWith(
      stage: (data['stage'] as String?) ?? state.stage,
      status: (data['status'] as String?) ?? state.status,
      epoch: p.epoch,
      totalEpochs: p.totalEpochs,
      loss: p.loss,
      valLoss: p.valLoss,
      accuracy: p.accuracy,
      f1: p.f1,
      health: (data['health'] as String?) ?? state.health,
      overfitting: (data['overfitting'] as bool?) ?? state.overfitting,
      history: history,
    );
  }

  @override
  void dispose() {
    _sub?.cancel();
    _ws.dispose();
    super.dispose();
  }
}

final trainingWebSocketProvider = Provider<WebSocketService>((ref) {
  final ws = WebSocketService('ws://localhost:8000/ws?user_id=public');
  ref.onDispose(ws.dispose);
  return ws;
});

final trainingProvider = StateNotifierProvider<TrainingNotifier, TrainingStateModel>((ref) {
  final ws = ref.watch(trainingWebSocketProvider);
  return TrainingNotifier(ws);
});
