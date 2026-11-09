#!/usr/bin/env bash
# Compila Kikario.app en tu Mac.   Uso:  ./build_mac.sh [--skip-tests]
set -euo pipefail
cd "$(dirname "$0")"

SKIP_TESTS=0
[[ "${1:-}" == "--skip-tests" ]] && SKIP_TESTS=1

# 1) Buscar Python 3.12 (o 3.13). Se puede forzar con PYTHON=/ruta/a/python ./build_mac.sh
PY="${PYTHON:-}"
if [[ -z "$PY" ]]; then
  for c in python3.12 python3.13; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
fi
if [[ -z "$PY" ]]; then
  echo "ERROR: no encontré Python 3.12. Instálalo desde https://www.python.org/downloads/macos/" >&2
  echo "       (o ejecuta con PYTHON=/ruta/a/python ./build_mac.sh)" >&2
  exit 1
fi
echo "==> Python: $($PY --version) ($(command -v "$PY"))  |  arquitectura: $(uname -m)"

# 2) Entorno virtual
if [[ ! -d .venv ]]; then
  echo "==> Creando entorno virtual en .venv"
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
echo "==> Instalando dependencias (requirements-dev.txt)"
pip install -r requirements-dev.txt

# 3) Pruebas
if [[ $SKIP_TESTS -eq 0 ]]; then
  echo "==> Ejecutando pruebas"
  QT_QPA_PLATFORM=offscreen python -m pytest -q
fi

# 4) Compilar
echo "==> Compilando con PyInstaller"
rm -rf build dist
pyinstaller --noconfirm --clean inventory.spec

# 5) Firma ad-hoc (sin cuenta de desarrollador): evita que macOS marque el bundle como dañado
codesign --force --deep --sign - dist/Kikario.app || echo "(aviso) no se pudo firmar ad-hoc"

# 6) Prueba de humo de la app empaquetada (BD temporal, sin ventana visible)
echo "==> Prueba de humo de la app empaquetada"
QT_QPA_PLATFORM=offscreen dist/Kikario.app/Contents/MacOS/Kikario --selftest

# 7) Zip para distribuir
ditto -c -k --keepParent dist/Kikario.app dist/Kikario-macOS.zip

echo
echo "Listo:"
echo "  App:  $(pwd)/dist/Kikario.app"
echo "  Zip:  $(pwd)/dist/Kikario-macOS.zip"
echo "Primera vez en este Mac: clic derecho > Abrir (o: xattr -cr dist/Kikario.app)"
