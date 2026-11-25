import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'cubit/estudiantes_cubit.dart';
import 'screens/estudiantes_page.dart';
import 'services/estudiante_service.dart';

// Reto 5: variables de entorno para provocar los cinco estados sin editar
// el código. Ejemplos:
//   flutter run --dart-define=SIMULAR_CARGA_LENTA=true
//   flutter run --dart-define=SIMULAR_VACIO=true
//   flutter run --dart-define=URL_API=https://jsonplaceholder.typicode.com/no-existe
const bool simularVacio = bool.fromEnvironment('SIMULAR_VACIO');
const bool simularCargaLenta = bool.fromEnvironment('SIMULAR_CARGA_LENTA');
const String urlApi = String.fromEnvironment(
  'URL_API',
  defaultValue: EstudianteService.urlApi,
);

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Práctica Cubit',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: BlocProvider(
        create: (_) => EstudiantesCubit(
          EstudianteService(
            simularVacio: simularVacio,
            retardo: simularCargaLenta ? const Duration(seconds: 3) : Duration.zero,
            urlBase: urlApi,
          ),
        ),
        child: const EstudiantesPage(),
      ),
    );
  }
}
