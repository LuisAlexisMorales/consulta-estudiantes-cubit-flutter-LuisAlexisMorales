"""Genera un HTML con el código del Cubit y de la pantalla para la Figura 6."""
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parents[1]
archivos = [
    ("lib/cubit/estudiantes_cubit.dart", "estudiantes_cubit.dart"),
    ("lib/screens/estudiantes_page.dart", "estudiantes_page.dart"),
]
columnas = []
for ruta, titulo in archivos:
    codigo = escape((root / ruta).read_text(encoding="utf-8"))
    columnas.append(
        f'<section><h2>{titulo}</h2><pre>{codigo}</pre></section>'
    )

html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Código del reto</title>
<style>
  body {{ margin: 0; padding: 18px; background: #fafafa; color: #17202a;
         font-family: Consolas, "Courier New", monospace; }}
  h1 {{ font-size: 18px; margin: 0 0 12px; font-family: Segoe UI, sans-serif; }}
  .cols {{ display: flex; gap: 18px; }}
  section {{ flex: 1; min-width: 0; background: white; border: 1px solid #d5d8dc;
             border-radius: 6px; padding: 10px; }}
  h2 {{ font-size: 13px; margin: 0 0 8px; font-family: Segoe UI, sans-serif;
        color: #283593; }}
  pre {{ margin: 0; font-size: 10.5px; line-height: 13px; white-space: pre-wrap;
         word-break: break-word; }}
</style>
</head>
<body>
<h1>Práctica Cubit — código del reto (Cubit y pantalla)</h1>
<div class="cols">{''.join(columnas)}</div>
</body>
</html>
"""

destino = root / "evidencias" / "codigo.html"
destino.write_text(html, encoding="utf-8")
print(destino)
