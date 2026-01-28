#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
limpeza_david - Módulo de Utilitários
Autor: David Fernandes
Descrição: Funções utilitárias compartilhadas para o projeto.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# === Cores para Terminal ===
class Colors:
    """Códigos de cores ANSI para terminal."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Cores
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Cores de fundo
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


# === Cores para GUI ===
COLORS = {
    'bg': '#f5f5f5',
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'text': '#1f2937',
    'text_secondary': '#6b7280',
}


# === Configuração de Logging ===
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_log_path() -> Path:
    """Retorna o caminho para o arquivo de log."""
    if sys.platform == 'win32':
        log_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'limpeza_david' / 'logs'
    else:
        log_dir = Path.home() / '.local' / 'share' / 'limpeza_david' / 'logs'
        
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"limpeza_{datetime.now().strftime('%Y%m%d')}.log"


def get_logger(name: str) -> logging.Logger:
    """
    Cria e configura um logger.
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Handler para arquivo
        try:
            file_handler = logging.FileHandler(get_log_path(), encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
            logger.addHandler(file_handler)
        except Exception:
            pass
            
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        logger.addHandler(console_handler)
        
    return logger


# === Formatação de Tamanho ===
def format_size(size_bytes: int) -> str:
    """
    Formata um tamanho em bytes para uma string legível.
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        String formatada (ex: "1.5 GB")
    """
    if size_bytes < 0:
        return "0 B"
        
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
        
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"


def parse_size(size_str: str) -> int:
    """
    Converte uma string de tamanho para bytes.
    
    Args:
        size_str: String como "1.5 GB" ou "500 MB"
        
    Returns:
        Tamanho em bytes
    """
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }
    
    size_str = size_str.strip().upper()
    
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                value = float(size_str[:-len(unit)].strip())
                return int(value * multiplier)
            except ValueError:
                return 0
                
    return 0


# === Operações de Arquivo ===
def get_file_size(path: Path) -> int:
    """
    Retorna o tamanho de um arquivo em bytes.
    
    Args:
        path: Caminho do arquivo
        
    Returns:
        Tamanho em bytes ou 0 em caso de erro
    """
    try:
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    except (OSError, PermissionError):
        pass
    return 0


def safe_remove_file(path: Path) -> bool:
    """
    Remove um arquivo de forma segura.
    
    Args:
        path: Caminho do arquivo
        
    Returns:
        True se removido com sucesso
    """
    try:
        if path.exists():
            path.unlink()
            return True
    except (OSError, PermissionError) as e:
        logger = get_logger("utils")
        logger.debug(f"Não foi possível remover {path}: {e}")
    return False


def safe_remove_dir(path: Path) -> bool:
    """
    Remove um diretório de forma segura.
    
    Args:
        path: Caminho do diretório
        
    Returns:
        True se removido com sucesso
    """
    try:
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
            return not path.exists()
    except (OSError, PermissionError) as e:
        logger = get_logger("utils")
        logger.debug(f"Não foi possível remover {path}: {e}")
    return False


# === Utilidades de Interface ===
def CENTER_WINDOW(window):
    """
    Centraliza uma janela Tkinter na tela.
    
    Args:
        window: Instância da janela Tk
    """
    window.update_idletasks()
    
    width = window.winfo_width()
    height = window.winfo_height()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"+{x}+{y}")


def print_banner():
    """Imprime o banner do aplicativo no terminal."""
    banner = f"""
{Colors.PURPLE}{Colors.BOLD}
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🧹  LIMPEZA DAVID - Limpador de Sistema  🧹        ║
║                                                       ║
║   Versão 1.0.0 | Open Source                         ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)


def print_colored(message: str, color: str = Colors.WHITE):
    """
    Imprime uma mensagem colorida no terminal.
    
    Args:
        message: Mensagem a imprimir
        color: Código de cor ANSI
    """
    print(f"{color}{message}{Colors.RESET}")


def confirm_action(message: str) -> bool:
    """
    Solicita confirmação do usuário no terminal.
    
    Args:
        message: Mensagem de confirmação
        
    Returns:
        True se confirmado
    """
    print(f"\n{Colors.YELLOW}⚠️  {message} (s/n): {Colors.RESET}", end="")
    response = input().strip().lower()
    return response in ['s', 'sim', 'y', 'yes']


# === Detecção de Sistema ===
def get_system_info() -> dict:
    """
    Retorna informações sobre o sistema.
    
    Returns:
        Dicionário com informações do sistema
    """
    import platform
    
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }


def is_admin() -> bool:
    """
    Verifica se o script está rodando com privilégios de admin.
    
    Returns:
        True se tiver privilégios de admin
    """
    try:
        if sys.platform == 'win32':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


# === Conversão de Ícone ===
def convert_png_to_ico(png_path: Path, ico_path: Path) -> bool:
    """
    Converte um arquivo PNG para ICO (Windows).
    
    Args:
        png_path: Caminho do arquivo PNG
        ico_path: Caminho de destino do arquivo ICO
        
    Returns:
        True se convertido com sucesso
    """
    try:
        from PIL import Image
        
        img = Image.open(png_path)
        
        # Redimensiona para tamanhos de ícone comuns
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        img.save(ico_path, format='ICO', sizes=sizes)
        return True
        
    except ImportError:
        logger = get_logger("utils")
        logger.warning("Pillow não instalado - conversão de ícone não disponível")
        return False
    except Exception as e:
        logger = get_logger("utils")
        logger.error(f"Erro ao converter ícone: {e}")
        return False


# Para testes
if __name__ == "__main__":
    print_banner()
    
    print(f"\n{Colors.CYAN}Informações do Sistema:{Colors.RESET}")
    info = get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
        
    print(f"\n{Colors.CYAN}Teste de formatação de tamanho:{Colors.RESET}")
    test_sizes = [0, 1023, 1024, 1536, 1048576, 1073741824, 1099511627776]
    for size in test_sizes:
        print(f"  {size} bytes = {format_size(size)}")
        
    print(f"\n{Colors.CYAN}Privilégios de admin:{Colors.RESET} {'Sim' if is_admin() else 'Não'}")
