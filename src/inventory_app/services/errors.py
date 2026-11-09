"""Excepciones de negocio. Su mensaje ya es apto para mostrar al usuario."""


class AppError(Exception):
    """Error base de la aplicación (mensaje en español para el usuario)."""


class ValidationError(AppError):
    pass


class NotFoundError(AppError):
    pass


class DuplicateSkuError(ValidationError):
    pass


class InsufficientStockError(AppError):
    pass


class BackupError(AppError):
    pass
