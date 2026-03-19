import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  SecureStorageService() : _storage = const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  Future<void> writeToken(String token) {
    return _storage.write(key: 'auth_token', value: token);
  }

  Future<String?> readToken() {
    return _storage.read(key: 'auth_token');
  }

  Future<void> clearToken() {
    return _storage.delete(key: 'auth_token');
  }
}
