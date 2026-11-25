r"""Genera INFORME.docx con las tablas, reflexiones y capturas de la práctica.

Si USAR_PORTADA=1, omite el título y los datos de portada: se insertará
C:\Users\moral\Documents\Plantillas\PORTADA.docx como primera página.
"""
import os
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

root = Path(__file__).resolve().parents[1]
evidencias = root / "evidencias"
doc = Document()

# Estilo base en español.
estilo = doc.styles["Normal"]
estilo.font.name = "Calibri"
estilo.font.size = Pt(10.5)


def tabla(encabezados, filas, anchos=None):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    for i, texto in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.text = texto
        for run in celda.paragraphs[0].runs:
            run.bold = True
    for fila in filas:
        celdas = t.add_row().cells
        for i, texto in enumerate(fila):
            celdas[i].text = texto
    if anchos:
        for fila in t.rows:
            for i, ancho in enumerate(anchos):
                fila.cells[i].width = Inches(ancho)
    doc.add_paragraph()
    return t


def parrafo(texto, negrita=False):
    p = doc.add_paragraph()
    run = p.add_run(texto)
    run.bold = negrita
    return p


def pregunta(texto, respuesta):
    p = doc.add_paragraph()
    p.add_run(texto).bold = True
    p.add_run(f" {respuesta}")


def figura(archivo, titulo, descripcion):
    doc.add_heading(titulo, level=2)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(evidencias / archivo), width=Inches(6.0))
    p = doc.add_paragraph()
    p.add_run("Descripción: ").bold = True
    p.add_run(descripcion)


# ---------------------------------------------------------------- portada
# La portada oficial se inserta como primera página con Word (ver abajo).
if os.getenv("USAR_PORTADA") != "1":
    doc.add_heading("Práctica: Consulta de estudiantes con Cubit en Flutter", 0)
    parrafo("Desarrollo de Aplicaciones Móviles — Unidad 4: Estados en Flutter")
    tabla(
        ["Dato", "Valor"],
        [
            ["Integrante 1", "(completar)"],
            ["Integrante 2", "(completar)"],
            ["Grupo", "(completar)"],
            ["Asesor", "Josué Israel Vásquez Martínez"],
            ["Fecha", "24 de noviembre de 2026"],
        ],
        [1.5, 4.8],
    )
doc.add_heading("Objetivo", level=1)
parrafo(
    "Implementar la gestión de estados en Flutter con Cubit (flutter_bloc) para consultar "
    "una API y representar en pantalla los cinco estados de una consulta (inicial, carga, "
    "éxito, vacío y error), comprendiendo cómo el Cubit emite estados y cómo la interfaz "
    "se redibuja a partir de ellos."
)

doc.add_heading("1. Estructura del proyecto", level=1)
parrafo(
    "lib/ contiene main.dart y las carpetas models/, services/, cubit/ y screens/. "
    "Se añadieron las dependencias flutter_bloc, http y equatable; se eliminó "
    "test/widget_test.dart y se agregó el permiso INTERNET en AndroidManifest.xml."
)

doc.add_heading("2. Descripción de los cambios del reto", level=1)
tabla(
    ["N.º", "Actividad", "Archivos", "Estado / resultado"],
    [
        [
            "1",
            "Campo ciudad",
            "estudiante.dart, estudiantes_page.dart",
            "EstudiantesExito: el subtitle del ListTile muestra correo y ciudad (address.city). El Cubit no cambia.",
        ],
        [
            "2",
            "Mensajes de error distintos",
            "estudiantes_cubit.dart, estudiante_service.dart",
            "EstudiantesError: catch de TimeoutException, http.ClientException, ErrorServidorException y general.",
        ],
        [
            "3",
            "Botón de reinicio",
            "estudiantes_page.dart",
            "IconButton en AppBar.actions llama a reiniciar() y vuelve a EstudiantesInicial.",
        ],
        [
            "4",
            "Contador en el título",
            "estudiantes_page.dart",
            "Segundo BlocBuilder: «Consulta de estudiantes (10)» solo en EstudiantesExito.",
        ],
        [
            "5",
            "Probar los cinco estados",
            "main.dart, estudiante_service.dart",
            "Variables SIMULAR_VACIO, SIMULAR_CARGA_LENTA y URL_API; el Cubit permanece intacto.",
        ],
    ],
    [0.35, 1.25, 1.75, 3.0],
)
parrafo(
    "Comandos: flutter run; flutter run --dart-define=SIMULAR_CARGA_LENTA=true; "
    "flutter run --dart-define=SIMULAR_VACIO=true; "
    "flutter run --dart-define=URL_API=https://jsonplaceholder.typicode.com/no-existe."
)

doc.add_heading("3. Actividades conceptuales", level=1)
doc.add_heading("A. ¿Qué estado se emite?", level=2)
tabla(
    ["Situación", "Estado emitido", "Qué ve el usuario"],
    [
        ["Se abre la aplicación por primera vez", "EstudiantesInicial", "«Presiona el botón para comenzar»"],
        ["El usuario presiona Cargar estudiantes", "EstudiantesCarga", "Círculo girando y «Cargando estudiantes...»"],
        ["La API responde con los 10 usuarios", "EstudiantesExito", "Lista con nombre, correo y ciudad; título «... (10)»"],
        ["La API responde correctamente con lista vacía", "EstudiantesVacio", "«No hay estudiantes registrados»"],
        ["El teléfono no tiene internet", "EstudiantesError", "Icono rojo, mensaje de sin conexión y «Reintentar»"],
        ["La API responde con código 500", "EstudiantesError", "Icono rojo, «Error del servidor (500).» y «Reintentar»"],
        ["El usuario presiona el botón de reiniciar", "EstudiantesInicial", "Mensaje inicial; desaparece el contador"],
    ],
    [1.85, 1.5, 3.0],
)

doc.add_heading("B. ¿Qué capa es responsable?", level=2)
tabla(
    ["Elemento del código", "Capa", "Por qué"],
    [
        ["Estudiante.fromJson(...)", "Modelo", "Convierte el JSON (incluido address.city) en un Estudiante."],
        ["http.get(...).timeout(...)", "Servicio", "Encapsula la petición HTTP y el límite de tiempo."],
        ["emit(const EstudiantesCarga())", "Cubit", "Publica el estado que provoca el redibujado."],
        ["props en EstudiantesExito", "Cubit (estado)", "Igualdad por valor para evitar reconstrucciones."],
        ["BlocBuilder<EstudiantesCubit, ...>", "Pantalla", "Escucha el Cubit y elige el widget para cada estado."],
        ["context.read<...>().cargarEstudiantes()", "Pantalla", "Da acceso al Cubit desde el botón sin escuchar cambios."],
        ["BlocProvider(create: ...) en main.dart", "Pantalla", "Crea y comparte el Cubit con los widgets descendientes."],
        ["El parámetro simularVacio", "Servicio", "Simula una respuesta vacía para probar el estado Vacío."],
    ],
    [2.0, 1.0, 3.35],
)

doc.add_page_break()
doc.add_heading("4. Evidencias y capturas", level=1)
figura(
    "figura_1_inicial.png",
    "Figura 1. Estado Inicial",
    "Al abrir la app el Cubit está en EstudiantesInicial: mensaje inicial, sin contador en el título y botón «Cargar estudiantes» disponible.",
)
figura(
    "figura_2_carga.png",
    "Figura 2. Estado Carga",
    "Tras pulsar el botón con SIMULAR_CARGA_LENTA=true, el Cubit emite EstudiantesCarga: CircularProgressIndicator y texto «Cargando estudiantes...».",
)
figura(
    "figura_3_exito.png",
    "Figura 3. Estado Éxito",
    "La API devuelve 10 usuarios: el título muestra «Consulta de estudiantes (10)» y cada ListTile muestra id, nombre, correo y ciudad.",
)
figura(
    "figura_4_vacio.png",
    "Figura 4. Estado Vacío",
    "Con SIMULAR_VACIO=true (o una respuesta []), la consulta es correcta pero no hay datos: «No hay estudiantes registrados».",
)
figura(
    "figura_5_error.png",
    "Figura 5. Estado Error",
    "La API responde 500: icono rojo, mensaje «Error del servidor (500).» y botón «Reintentar» que vuelve a cargar.",
)
figura(
    "figura_6_codigo.png",
    "Figura 6. Código del Cubit y de la pantalla",
    "Código final con los catch específicos, reiniciar(), el AppBar con dos BlocBuilder y el subtitle con la ciudad.",
)

doc.add_page_break()
doc.add_heading("5. Preguntas de reflexión", level=1)
pregunta(
    "1. ¿Qué es un Cubit y en qué se diferencia de setState?",
    "Es una clase que guarda el estado y lo cambia con emit(). Vive fuera del widget, así que se puede probar, reutilizar y compartir. Con setState el estado queda dentro del widget, mezclado con la interfaz, y se reconstruye ese widget.",
)
pregunta(
    "2. ¿Qué hace emit() y qué ocurre en la pantalla?",
    "Publica un nuevo estado en el stream del Cubit. Los BlocBuilder que escuchan ejecutan su builder con el estado nuevo; si es igual por Equatable, no se reconstruyen.",
)
pregunta(
    "3. ¿Para qué sirve BlocBuilder y por qué no se redibuja toda la pantalla?",
    "Suscribe solo una parte del árbol al Cubit. Aquí hay dos: el cuerpo (cinco estados) y el título (contador). Al cargar no se recrea el Scaffold completo.",
)
pregunta(
    "4. ¿Por qué estados distintos y sealed?",
    "Cada clase representa una situación con sus datos (lista o mensaje). sealed obliga al compilador a verificar que el switch cubra todos los estados; uno nuevo sin dibujar daría error de compilación.",
)
pregunta(
    "5. ¿Qué función cumple Equatable?",
    "Compara estados por valor mediante props. Sin él, dos EstudiantesExito con la misma lista serían objetos distintos y provocarían una reconstrucción innecesaria.",
)
pregunta(
    "6. ¿Por qué el Cubit no llama directamente a http?",
    "Por separación de responsabilidades: el servicio concentra URL, decode, timeout y simulaciones; el Cubit solo decide qué estado emitir. Así se puede cambiar la API o hacer tests sin tocar la lógica de estados.",
)
pregunta(
    "7. ¿Qué hace BlocProvider y qué pasa sin él?",
    "Crea el Cubit y lo comparte con los widgets descendientes. Sin proveedor, context.read<EstudiantesCubit>() lanzaría ProviderNotFoundException.",
)
pregunta(
    "8. ¿Qué cambios realizaste y qué se vio afectado?",
    "Ciudad en el modelo y el ListTile, catch diferenciados en el Cubit, IconButton de reinicio, segundo BlocBuilder en el título y servicio parametrizado. Estados: Exito, Error e Inicial; widgets: ListTile, AppBar, IconButton, BlocBuilder y FAB.",
)

doc.add_heading("6. Conclusión", level=1)
parrafo(
    "Integrante 1: (escribe aquí un párrafo personal: qué aprendiste sobre el papel del Cubit "
    "al separar la lógica de la interfaz, qué dificultad tuviste y cómo ayudan los estados a "
    "representar cada situación de la consulta)."
)
parrafo(
    "Integrante 2: (escribe aquí tu propio párrafo con tu experiencia: qué te costó más, cómo "
    "resolviste el reto de la ciudad anidada en address o la simulación del estado vacío, y qué "
    "te llevas de la comparación entre setState y Cubit)."
)

doc.add_heading("7. Comprobación", level=1)
parrafo(
    "flutter analyze → No issues found. flutter test → 4 pruebas del Cubit superadas. "
    "flutter build web --release → correcto. "
    "Los cinco estados se verificaron en ejecución real: el texto accesible de las capturas "
    "confirma el mensaje inicial, «Cargando estudiantes...», «Consulta de estudiantes (10)» con "
    "las ciudades, «No hay estudiantes registrados» y «Error del servidor (500).»"
)

destino = root / os.getenv("NOMBRE_SALIDA", "INFORME.docx")
doc.save(destino)
print(destino)
