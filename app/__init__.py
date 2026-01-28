# Módulo principal do app
from .main import main, LimpezaDavidApp
from .utils import get_logger, format_size, COLORS

__all__ = ['main', 'LimpezaDavidApp', 'get_logger', 'format_size', 'COLORS']
__version__ = '1.0.0'
