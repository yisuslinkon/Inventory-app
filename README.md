# Kikario

**Kikario** — pensada para llevar el negocio de Kika.

Aplicación de escritorio **100 % offline** para controlar inventario y ventas. Funciona en macOS y Windows.
Python 3.12 · PySide6 (Qt) · SQLite · QtCharts · PyInstaller.

Funciones: productos con alertas de stock mínimo, ajustes de inventario con historial, ventas con varios
productos (bloquea si falta stock y se pueden anular), panel con ventas del mes, gráfico de los últimos
12 meses, top 5 y stock bajo, reportes por rango de fechas con exportación a CSV, y copias de seguridad
(exportar/importar la base de datos). No usa internet ni envía telemetría.

---

## 1. Entorno virtual (venv) y dependencias

Un *entorno virtual* es una carpeta (`.venv`) con su propio Python y sus propias librerías, para no mezclar
nada con el resto de tu Mac. Se crea una vez por proyecto.

Desde la carpeta del proyecto, en la Terminal:

```bash
python3.12 -m venv .venv            # crear (solo la primera vez)
source .venv/bin/activate           # activar (cada vez que abras una Terminal nueva)
pip install -r requirements-dev.txt # instalar dependencias (solo la primera vez o si cambian)
```

Sabrás que está activo porque el prompt empieza con `(.venv)`. Para salir: `deactivate`.

En Windows (PowerShell): `py -3.12 -m venv .venv`, luego `.venv\Scripts\Activate.ps1`.

`requirements.txt` tiene lo necesario para **ejecutar** la app; `requirements-dev.txt` añade pytest y
PyInstaller (para pruebas y compilar).

## 2. Ejecutar en desarrollo

```bash
source .venv/bin/activate
python run.py
```

## 3. Pruebas

```bash
source .venv/bin/activate
pytest
```

La lógica (productos, stock, ventas, anulaciones, dashboard, reportes, backup, migraciones) está en
`services/` y `db/`, sin dependencia de la interfaz, y se prueba sin abrir ninguna ventana. Las pruebas de
interfaz usan Qt en modo `offscreen`.

## 4. Compilar en tu Mac

```bash
./build_mac.sh                 # instala dependencias, corre pruebas, compila y empaqueta
./build_mac.sh --skip-tests    # igual, pero sin pruebas
```

(Si dice "permission denied": `chmod +x build_mac.sh` o ejecútalo con `bash build_mac.sh`.)

Resultado en `dist/`:

- `Kikario.app` — la aplicación
- `Kikario-macOS.zip` — la misma app comprimida para compartirla

El script usa `python3.12` (o `PYTHON=/ruta/a/python ./build_mac.sh`), compila para la arquitectura de tu
Mac, firma "ad-hoc" y ejecuta una prueba de humo de la app ya empaquetada (`Kikario --selftest`, con una
base de datos temporal).

## 5. Obtener la versión de Windows (GitHub Actions)

No necesitas una máquina Windows: GitHub la compila por ti.

1. Sube el proyecto a un repositorio de GitHub (puede ser privado):
   ```bash
   git init && git add . && git commit -m "Kikario"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
   git push -u origin main
   ```
2. **Opción A — manual:** en GitHub, pestaña **Actions** → workflow **Build** → **Run workflow**.
3. **Opción B — con tag (crea además un Release con los archivos):**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. Cuando termine (unos minutos), entra a la ejecución y descarga en **Artifacts**:
   - `Kikario-Windows` → contiene `Kikario-Windows.zip` (carpeta con `Kikario.exe`)
   - `Kikario-macOS-Intel` y `Kikario-macOS-AppleSilicon` → `.app` comprimida
   Con el tag, los mismos zip quedan en la sección **Releases**.
5. En Windows: descomprime la carpeta completa y ejecuta `Kikario.exe` (no muevas el `.exe` solo).

El workflow instala dependencias, corre las pruebas, compila con PyInstaller, hace la prueba de humo del
programa empaquetado y sube los artefactos. Nota: en repositorios privados los minutos de macOS cuentan más
que los de Windows/Linux; si no necesitas alguna variante de Mac, borra su bloque en `matrix` de
`.github/workflows/build.yml`.

## 6. Dónde se guardan los datos

| Sistema | Archivo de la base de datos |
|---|---|
| macOS | `~/Library/Application Support/Kikario/kikario.db` |
| Windows | `%APPDATA%\Kikario\kikario.db` |

**Desarrollo vs. producción:** `python run.py` (código fuente) guarda en `./datos-dev/` y la ventana dice
"MODO DESARROLLO", así tus datos de prueba nunca se mezclan con los de la app instalada. La app compilada
(`Kikario.app` / `Kikario.exe`) siempre usa la carpeta del sistema de la tabla. Para forzar otra
carpeta: `KIKARIO_DATA_DIR=/ruta python run.py`. Para empezar de cero en desarrollo, borra `datos-dev/`.

En la misma carpeta se guarda `kikario.log` (errores inesperados). La ruta exacta se muestra en la
pantalla **Respaldo y ajustes**. Para respaldar: **Exportar base de datos**; para restaurar o pasar los
datos a otro equipo: **Importar base de datos** (antes de reemplazar se guarda una copia automática).

## 7. Aplicaciones sin firmar: avisos del sistema

Las apps no están firmadas con un certificado de pago, así que el sistema muestra una advertencia la
primera vez:

- **macOS:** clic derecho sobre `Kikario.app` → **Abrir** → **Abrir**. Si dice que está "dañada" o no
  la deja abrir, quita la marca de cuarentena con `xattr -cr /ruta/a/Kikario.app` y vuelve a abrirla.
  En macOS recientes también puedes ir a **Ajustes del Sistema → Privacidad y seguridad → Abrir de todos
  modos**.
- **Windows:** en la pantalla azul de SmartScreen pulsa **Más información → Ejecutar de todas formas**.

## 8. Estructura

```
src/inventory_app/
  db/        conexión SQLite, migrador y migrations/*.sql
  services/  lógica de negocio (sin Qt): products, inventory, sales, dashboard, reports, backup, money…
  ui/        ventana principal, páginas y widgets (PySide6)
  strings.py todos los textos en español
tests/       pytest
inventory.spec  configuración de PyInstaller (Mac y Windows)
```

Decisiones de diseño: precios como enteros en la unidad mínima de la moneda (COP sin decimales por
defecto, configurable); cada venta, anulación o ajuste de stock es una transacción SQLite; cada venta
guarda el precio y el costo del momento, así la utilidad histórica no cambia si luego editas precios;
borrar un producto con historial lo archiva en vez de eliminarlo.
