// mobile/core/network/api_client.dart
import 'package:dio/dio.dart';

class ApiClient {
  ApiClient({required String baseUrl})
      : _dio = Dio(BaseOptions(baseUrl: baseUrl, connectTimeout: const Duration(seconds: 15)));

  final Dio _dio;

  Future<Response<dynamic>> get(String path, {Map<String, dynamic>? query}) {
    return _dio.get(path, queryParameters: query);
  }

  Future<Response<dynamic>> post(String path, {Object? data}) {
    return _dio.post(path, data: data);
  }
}
