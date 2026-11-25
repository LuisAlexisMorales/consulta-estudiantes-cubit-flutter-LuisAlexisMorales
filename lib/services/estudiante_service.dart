import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/estudiante.dart';

/// Error lanzado cuando la API responde con un código distinto de 200.
class ErrorServidorException implements Exception {
  final int codigo;

  const ErrorServidorException(this.codigo);

  @override
  String toString() => 'Error del servidor: $codigo';
}

/// Acceso a la API de estudiantes.
class EstudianteService {
  static const String urlApi = 'https://jsonplaceholder.typicode.com/users';

  /// Si es true, simula una consulta correcta que devuelve una lista vacía
  /// (para demostrar el estado Vacío).
  final bool simularVacio;

  /// URL base. Permite apuntar a una URL incorrecta y provocar el estado Error.
  final String urlBase;

  /// Retardo opcional para poder observar el estado Carga.
  final Duration retardo;

  const EstudianteService({
    this.simularVacio = false,
    this.urlBase = urlApi,
    this.retardo = Duration.zero,
  });

  Future<List<Estudiante>> obtenerEstudiantes() async {
    if (retardo > Duration.zero) {
      await Future<void>.delayed(retardo);
    }

    if (simularVacio) {
      await Future<void>.delayed(const Duration(seconds: 1));
      return <Estudiante>[];
    }

    final respuesta = await http
        .get(Uri.parse(urlBase))
        .timeout(const Duration(seconds: 10));

    if (respuesta.statusCode != 200) {
      throw ErrorServidorException(respuesta.statusCode);
    }

    final List<dynamic> datos = jsonDecode(respuesta.body) as List<dynamic>;
    return datos
        .map((json) => Estudiante.fromJson(json as Map<String, dynamic>))
        .toList();
  }
}
