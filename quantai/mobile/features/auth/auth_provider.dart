import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/storage/local_storage.dart';
import '../../core/storage/secure_storage_service.dart';

class AuthState {
  const AuthState({required this.isAuthenticated, required this.loading, this.error});

  final bool isAuthenticated;
  final bool loading;
  final String? error;

  AuthState copyWith({bool? isAuthenticated, bool? loading, String? error}) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      loading: loading ?? this.loading,
      error: error,
    );
  }

  factory AuthState.initial() => const AuthState(isAuthenticated: false, loading: false);
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier(this._secureStorage, this._localStorage) : super(AuthState.initial()) {
    _bootstrap();
  }

  final SecureStorageService _secureStorage;
  final LocalStorage _localStorage;

  Future<void> _bootstrap() async {
    final token = await _secureStorage.readToken();
    state = state.copyWith(isAuthenticated: token != null && token.isNotEmpty);
  }

  Future<void> signIn({required String email, required String password}) async {
    state = state.copyWith(loading: true, error: null);
    if (email.trim().isEmpty || password.length < 6) {
      state = state.copyWith(loading: false, error: 'Invalid credentials format');
      return;
    }
    await _secureStorage.writeToken('demo-token-${DateTime.now().millisecondsSinceEpoch}');
    await _localStorage.setString('user_email', email.trim());
    state = state.copyWith(isAuthenticated: true, loading: false, error: null);
  }

  Future<void> signOut() async {
    await _secureStorage.clearToken();
    state = state.copyWith(isAuthenticated: false, loading: false, error: null);
  }
}

final secureStorageProvider = Provider<SecureStorageService>((ref) => SecureStorageService());
final localStorageProvider = Provider<LocalStorage>((ref) => LocalStorage());

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(secureStorageProvider), ref.watch(localStorageProvider));
});
