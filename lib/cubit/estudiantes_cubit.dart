import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;

import '../services/estudiante_service.dart';
import 'estudiantes_state.dart';

/// Guarda el estado actual y decide qué estado emitir en cada consulta.
class EstudiantesCubit extends Cubit<EstudiantesState> {
  final EstudianteService _servicio;

  EstudiantesCubit(this._servicio) : super(const EstudiantesInicial());

  Future<void> cargarEstudiantes() async {
    emit(const EstudiantesCarga());

    try {
      final datos = await _servicio.obtenerEstudiantes();

      if (datos.isEmpty) {
        emit(const EstudiantesVacio());
      } else {
        emit(EstudiantesExito(datos));
      }
    } on TimeoutException catch (_) {
      // Reto 2: el servidor tardó más del tiempo permitido.
      emit(const EstudiantesError(
        'Tiempo de espera agotado. Inténtalo de nuevo más tarde.',
      ));
    } on http.ClientException catch (_) {
      // Reto 2: normalmente significa que no hay conexión a internet.
      emit(const EstudiantesError(
        'Sin conexión a internet. Revisa tu red e inténtalo de nuevo.',
      ));
    } on ErrorServidorException catch (e) {
      // Reto 2: la API respondió, pero con un código de error (500, 404...).
      emit(EstudiantesError('Error del servidor (${e.codigo}).'));
    } catch (_) {
      // Reto 2: cualquier otra causa (JSON inválido, etc.).
      emit(const EstudiantesError(
        'No se pudieron cargar los datos. Inténtalo de nuevo.',
      ));
    }
  }

  /// Reto 3: vuelve al estado inicial.
  void reiniciar() => emit(const EstudiantesInicial());
}
