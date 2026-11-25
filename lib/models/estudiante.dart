/// Datos de un estudiante obtenidos de la API.
class Estudiante {
  final int id;
  final String nombre;
  final String correo;
  final String ciudad;

  const Estudiante({
    required this.id,
    required this.nombre,
    required this.correo,
    required this.ciudad,
  });

  /// Convierte el JSON de la API en un objeto [Estudiante].
  ///
  /// Reto 1: la ciudad viene anidada en `json['address']['city']`.
  factory Estudiante.fromJson(Map<String, dynamic> json) {
    final address = json['address'] as Map<String, dynamic>?;

    return Estudiante(
      id: json['id'] as int,
      nombre: json['name'] as String,
      correo: json['email'] as String,
      ciudad: address?['city'] as String? ?? 'Ciudad desconocida',
    );
  }
}
