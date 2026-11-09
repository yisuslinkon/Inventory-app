"""Todos los textos de la aplicación (español) en un único archivo.

Los servicios usan los mensajes de la sección ERRORES; la interfaz usa el resto.
"""

# ---------------------------------------------------------------- ERRORES
ERR_NAME_REQUIRED = "El nombre es obligatorio."
ERR_SKU_REQUIRED = "El SKU es obligatorio."
ERR_SKU_DUPLICATE = "Ya existe un producto activo con el SKU «{sku}»."
ERR_INVALID_INT = "{field}: debe ser un número entero."
ERR_NEGATIVE = "{field}: no puede ser negativo."
ERR_MUST_BE_POSITIVE = "{field}: debe ser mayor que cero."
ERR_INVALID_MONEY = "{field}: monto no válido."
ERR_PRODUCT_NOT_FOUND = "El producto no existe o fue eliminado."
ERR_PRODUCT_INACTIVE = "El producto «{name}» está archivado y no se puede usar."
ERR_INSUFFICIENT_STOCK = (
    "Stock insuficiente para «{name}»: disponible {available}, solicitado {requested}."
)
ERR_NO_ITEMS = "Agrega al menos un producto a la venta."
ERR_SALE_NOT_FOUND = "La venta no existe."
ERR_SALE_ALREADY_VOIDED = "La venta #{id} ya estaba anulada."
ERR_CORRECTION_NO_CHANGE = "El conteo indicado es igual al stock actual; no hay nada que corregir."
ERR_INVALID_ADJUST_KIND = "Tipo de ajuste no válido."
ERR_DATE_RANGE = "La fecha inicial no puede ser posterior a la fecha final."
ERR_BACKUP_INVALID = "El archivo seleccionado no es una copia de seguridad válida."
ERR_BACKUP_NEWER = (
    "La copia fue creada con una versión más nueva de la aplicación y no se puede importar."
)
ERR_UNEXPECTED = "Ocurrió un error inesperado: {detail}"

# Etiquetas de campos usadas en los mensajes de validación
FIELD_COST = "Precio de costo"
FIELD_PRICE = "Precio de venta"
FIELD_STOCK = "Stock"
FIELD_MIN_STOCK = "Stock mínimo"
FIELD_QUANTITY = "Cantidad"
FIELD_COUNT = "Conteo"

# Tipos de movimiento (historial)
MOVEMENT_LABELS = {
    "initial": "Stock inicial",
    "restock": "Reposición",
    "loss": "Pérdida",
    "correction": "Corrección",
    "sale": "Venta",
    "void": "Anulación de venta",
}
SALE_STATUS_LABELS = {"completed": "Completada", "voided": "Anulada"}

# ---------------------------------------------------------- ERRORES DE UI
ERR_PICK_PRODUCT = "Selecciona un producto de la lista."
ERR_DB_OPEN = (
    "No se pudo abrir la base de datos:\n{path}\n\n{detail}\n\n"
    "Si el problema continúa, restaura una copia de seguridad."
)

# ------------------------------------------------------------- NAVEGACIÓN
NAV_DASHBOARD = "Panel"
NAV_PRODUCTS = "Productos"
NAV_INVENTORY = "Inventario"
NAV_SALES = "Ventas"
NAV_REPORTS = "Reportes"
NAV_SETTINGS = "Respaldo y ajustes"

# ---------------------------------------------------------------- BOTONES
BTN_OK = "Aceptar"
BTN_CANCEL = "Cancelar"
BTN_SAVE = "Guardar"
BTN_EDIT = "Editar"
BTN_DELETE = "Eliminar"
BTN_NEW_PRODUCT = "Nuevo producto"
BTN_APPLY_ADJUSTMENT = "Aplicar ajuste"
BTN_ADD_TO_SALE = "Agregar"
BTN_REMOVE = "Quitar"
BTN_CLEAR_SALE = "Vaciar"
BTN_REGISTER_SALE = "Registrar venta"
BTN_VOID_SALE = "Anular venta"
BTN_QUERY = "Consultar"
BTN_EXPORT_CSV = "Exportar CSV"
BTN_EXPORT_DB = "Exportar base de datos"
BTN_IMPORT_DB = "Importar base de datos"
BTN_IMPORT_CONFIRM = "Reemplazar datos"

# ------------------------------------------------------- DIÁLOGOS GENERALES
DLG_ERROR_TITLE = "No se pudo completar la acción"
DLG_INFO_TITLE = "Listo"
DLG_CONFIRM_TITLE = "Confirmar"
DLG_VOID_REASON_TITLE = "Motivo de la anulación"
DLG_VOID_REASON_LABEL = "Motivo (opcional):"
DLG_EXPORT_CSV = "Exportar ventas a CSV"
DLG_EXPORT_DB = "Exportar copia de seguridad"
DLG_IMPORT_DB = "Importar copia de seguridad"
FILTER_CSV = "Archivos CSV (*.csv)"
FILTER_DB = "Base de datos (*.db);;Todos los archivos (*)"

# -------------------------------------------------------------- ETIQUETAS
LBL_NAME = "Nombre"
LBL_SKU = "SKU"
LBL_CATEGORY = "Categoría"
LBL_COST = "Precio de costo"
LBL_PRICE = "Precio de venta"
LBL_STOCK_INITIAL = "Stock inicial"
LBL_STOCK_CURRENT = "Stock actual"
LBL_MIN_STOCK = "Alerta de stock mínimo"
LBL_PRODUCT = "Producto"
LBL_ADJ_TYPE = "Tipo de ajuste"
LBL_QUANTITY = "Cantidad"
LBL_REAL_COUNT = "Conteo real"
LBL_NOTE = "Nota"
LBL_NOTE_OPTIONAL = "Nota (opcional)"
LBL_HISTORY = "Historial de movimientos"
LBL_TOTAL = "Total"
LBL_LAST_SALES = "Últimas ventas"
LBL_FROM = "Desde"
LBL_TO = "Hasta"
LBL_CURRENCY_CODE = "Código de moneda"
LBL_CURRENCY_SYMBOL = "Símbolo"
LBL_CURRENCY_DECIMALS = "Decimales"

CHK_HISTORY_ALL = "Ver todos los productos"
CHK_INCLUDE_VOIDED = "Incluir ventas anuladas"

PICKER_PLACEHOLDER = "Escribe para buscar por nombre o SKU…"
PICKER_STOCK = "stock"
PRODUCTS_SEARCH = "Buscar por nombre, SKU o categoría…"
PRODUCT_NEW_TITLE = "Nuevo producto"
PRODUCT_EDIT_TITLE = "Editar producto"
PRODUCT_STOCK_HINT = "El stock se modifica desde la sección Inventario (ajustes)."

ADJ_RESTOCK = "Reposición (suma)"
ADJ_LOSS = "Pérdida (resta)"
ADJ_CORRECTION = "Corrección (conteo real)"

TAB_NEW_SALE = "Nueva venta"
TAB_SALES_HISTORY = "Historial"

# ---------------------------------------------------------------- COLUMNAS
COL_NAME = "Nombre"
COL_SKU = "SKU"
COL_CATEGORY = "Categoría"
COL_COST = "Costo"
COL_PRICE = "Precio"
COL_STOCK = "Stock"
COL_MIN_STOCK = "Mínimo"
COL_DATE = "Fecha"
COL_PRODUCT = "Producto"
COL_TYPE = "Tipo"
COL_CHANGE = "Cambio"
COL_STOCK_AFTER = "Stock resultante"
COL_NOTE = "Nota"
COL_QUANTITY = "Cantidad"
COL_SUBTOTAL = "Subtotal"
COL_SALE_NO = "N.º"
COL_DETAIL = "Detalle"
COL_UNITS = "Unidades"
COL_TOTAL = "Total"
COL_PROFIT = "Utilidad"
COL_STATUS = "Estado"
COL_REVENUE = "Ingresos"

# ---------------------------------------------------------------- PANEL
DASH_SUBTITLE = "Resumen de {month} de {year}"
KPI_REVENUE = "Total vendido"
KPI_UNITS = "Unidades vendidas"
KPI_PROFIT = "Utilidad"
CHART_TITLE = "Ventas por mes (últimos 12 meses)"
CHART_SERIES = "Ventas"
TOP_TITLE = "Top 5 productos del mes"
TOP_EMPTY = "Aún no hay ventas este mes."
LOW_TITLE = "Alertas de stock bajo"
LOW_EMPTY = "Todo el inventario está por encima del mínimo."

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]
MONTHS_SHORT = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

# --------------------------------------------------------------- MENSAJES
MSG_SELECT_PRODUCT = "Primero selecciona un producto de la tabla."
MSG_SELECT_SALE = "Primero selecciona una venta de la tabla."
CONFIRM_DELETE_PRODUCT = "¿Eliminar el producto «{name}»?"
MSG_PRODUCT_ARCHIVED = (
    "«{name}» tiene ventas o movimientos registrados, por eso se archivó en lugar de "
    "borrarse. Ya no aparece en las listas y su historial se conserva."
)
MSG_ADJUSTMENT_OK = "Ajuste registrado. Stock actual: {stock}."
MSG_SALE_OK = "Venta #{id} registrada por {total}."
CONFIRM_VOID_SALE = "¿Anular la venta #{id}? El stock de sus productos se restablecerá."
MSG_SALE_VOIDED = "Venta #{id} anulada y stock restablecido."
MSG_NO_SALES_TO_EXPORT = "No hay ventas en el rango seleccionado para exportar."
MSG_CSV_OK = "Se exportaron {n} líneas a:\n{path}"
REPORT_SUMMARY = (
    "Ventas completadas: {n}   ·   Unidades: {units}   ·   Total: {total}   ·   Utilidad: {profit}"
)

# ------------------------------------------------------ RESPALDO Y AJUSTES
BACKUP_TITLE = "Copias de seguridad"
BACKUP_HINT = (
    "Exporta una copia de tu base de datos para guardarla en un lugar seguro o llevarla a "
    "otro computador. Al importar, los datos actuales se reemplazan (se guarda antes una "
    "copia automática)."
)
DATA_FILE_LOCATION = "Archivo de datos actual: {path}"
CONFIRM_IMPORT_DB = (
    "Se reemplazarán TODOS los datos actuales por los de la copia seleccionada. "
    "Antes se guardará una copia automática de lo que tienes ahora.\n\n¿Continuar?"
)
MSG_BACKUP_OK = "Copia de seguridad guardada en:\n{path}"
MSG_IMPORT_OK = "Copia importada correctamente."
MSG_IMPORT_SAFETY = "\n\nTus datos anteriores se guardaron en:\n{path}"
CURRENCY_TITLE = "Moneda"
CURRENCY_DECIMALS_LOCKED = (
    "Los decimales no se pueden cambiar cuando ya hay productos o ventas, porque los "
    "montos guardados se interpretarían distinto."
)
CURRENCY_PREVIEW = "Vista previa: {example}"
MSG_CURRENCY_SAVED = "Configuración de moneda guardada."

# ------------------------------------------------------------ DESARROLLO
WINDOW_TITLE_DEV = "{app} — MODO DESARROLLO (datos de prueba)"
