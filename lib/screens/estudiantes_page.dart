import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../cubit/estudiantes_cubit.dart';
import '../cubit/estudiantes_state.dart';

/// Una vista distinta para cada uno de los cinco estados.
class EstudiantesPage extends StatelessWidget {
  const EstudiantesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Reto 4: el título depende del estado (segundo BlocBuilder).
      appBar: AppBar(
        title: BlocBuilder<EstudiantesCubit, EstudiantesState>(
          builder: (context, state) {
            final cantidad = switch (state) {
              EstudiantesExito(:final estudiantes) => estudiantes.length,
              _ => 0,
            };

            return Text(
              cantidad > 0
                  ? 'Consulta de estudiantes ($cantidad)'
                  : 'Consulta de estudiantes',
            );
          },
        ),
        // Reto 3: botón de reinicio en la barra superior.
        actions: [
          IconButton(
            tooltip: 'Reiniciar',
            icon: const Icon(Icons.restart_alt),
            onPressed: () => context.read<EstudiantesCubit>().reiniciar(),
          ),
        ],
      ),
      body: BlocBuilder<EstudiantesCubit, EstudiantesState>(
        builder: (context, state) {
          return switch (state) {
            EstudiantesInicial() => const Center(
                child: Text('Presiona el botón para comenzar'),
              ),
            EstudiantesCarga() => const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 12),
                    Text('Cargando estudiantes...'),
                  ],
                ),
              ),
            EstudiantesVacio() => const Center(
                child: Text('No hay estudiantes registrados'),
              ),
            EstudiantesError(:final mensaje) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.error_outline, size: 48, color: Colors.red),
                      const SizedBox(height: 8),
                      Text(mensaje, textAlign: TextAlign.center),
                      const SizedBox(height: 12),
                      ElevatedButton(
                        onPressed: () => context
                            .read<EstudiantesCubit>()
                            .cargarEstudiantes(),
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                ),
              ),
            EstudiantesExito(:final estudiantes) => ListView.builder(
                itemCount: estudiantes.length,
                itemBuilder: (context, index) {
                  final e = estudiantes[index];
                  return ListTile(
                    leading: CircleAvatar(child: Text('${e.id}')),
                    title: Text(e.nombre),
                    // Reto 1: correo y ciudad en el subtítulo.
                    subtitle: Text('${e.correo}\n${e.ciudad}'),
                    isThreeLine: true,
                  );
                },
              ),
          };
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.read<EstudiantesCubit>().cargarEstudiantes(),
        icon: const Icon(Icons.download),
        label: const Text('Cargar estudiantes'),
      ),
    );
  }
}
