# Módulo de limpeza - limpeza_david
# Suporta Windows e Linux

import platform

# Importa apenas o cleaner apropriado para o sistema operacional
if platform.system() == 'Windows':
    from .windows import WindowsCleaner
    __all__ = ['WindowsCleaner']
else:
    from .linux import LinuxCleaner
    __all__ = ['LinuxCleaner']
