import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:practica_estudiantes/cubit/estudiantes_cubit.dart';
import 'package:practica_estudiantes/cubit/estudiantes_state.dart';
import 'package:practica_estudiantes/models/estudiante.dart';
import 'package:practica_estudiantes/services/estudiante_service.dart';

class _ServicioFalso extends EstudianteService {
  final Future<List<Estudiante>> Function() respuesta;

  _ServicioFalso(this.respuesta) : super();

  @override
  Future<List<Estudiante>> obtenerEstudiantes() => respuesta();
}

Future<List<EstudiantesState>> estadosEmitidos(
  EstudiantesCubit cubit,
  Future<void> Function() accion,
) async {
  final estados = <EstudiantesState>[];
  final suscripcion = cubit.stream.listen(estados.add);
  await accion();
  await Future<void>.delayed(Duration.zero);
  await suscripcion.cancel();
  return estados;
}

void main() {
  const estudiante = Estudiante(
    id: 1,
    nombre: 'Leanne Graham',
    correo: 'sincere@april.biz',
    ciudad: 'Gwenborough',
  );

  test('emite Carga y luego Éxito cuando hay datos', () async {
    final cubit = EstudiantesCubit(_ServicioFalso(() async => [estudiante]));

    final estados = await estadosEmitidos(cubit, cubit.cargarEstudiantes);

    expect(estados, [isA<EstudiantesCarga>(), isA<EstudiantesExito>()]);
    expect((estados.last as EstudiantesExito).estudiantes.single.ciudad,
        'Gwenborough');
  });

  test('emite Carga y luego Vacío cuando la lista está vacía', () async {
    final cubit = EstudiantesCubit(_ServicioFalso(() async => []));

    final estados = await estadosEmitidos(cubit, cubit.cargarEstudiantes);

    expect(estados, [isA<EstudiantesCarga>(), isA<EstudiantesVacio>()]);
  });

  test('emite un mensaje distinto para cada causa del error', () async {
    final timeout = EstudiantesCubit(
      _ServicioFalso(() async => throw TimeoutException('tarde')),
    );
    final servidor = EstudiantesCubit(
      _ServicioFalso(() async => throw const ErrorServidorException(500)),
    );

    final estadosTimeout =
        await estadosEmitidos(timeout, timeout.cargarEstudiantes);
    final estadosServidor =
        await estadosEmitidos(servidor, servidor.cargarEstudiantes);

    expect((estadosTimeout.last as EstudiantesError).mensaje,
        contains('Tiempo de espera agotado'));
    expect((estadosServidor.last as EstudiantesError).mensaje,
        contains('Error del servidor (500)'));
  });

  test('reiniciar vuelve al estado Inicial', () async {
    final cubit = EstudiantesCubit(_ServicioFalso(() async => [estudiante]));
    await cubit.cargarEstudiantes();

    final estados = await estadosEmitidos(cubit, () async => cubit.reiniciar());

    expect(estados, [isA<EstudiantesInicial>()]);
  });
}
