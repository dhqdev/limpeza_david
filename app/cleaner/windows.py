#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
limpeza_david - Módulo de Limpeza para Windows
Autor: David Fernandes
Descrição: Implementa a limpeza de arquivos temporários, cache e 
           arquivos desnecessários no Windows.
"""

import os
import shutil
import glob
import platform
from pathlib import Path
from typing import List, Tuple, Dict

# Imports específicos do Windows (só carrega se estiver no Windows)
if platform.system() == 'Windows':
    import winreg
    import ctypes

# Importa utilitários
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils import get_logger, safe_remove_file, safe_remove_dir, get_file_size


class WindowsCleaner:
    """
    Classe para limpeza de sistema no Windows.
    Remove arquivos temporários, cache e arquivos desnecessários.
    """
    
    def __init__(self):
        self.logger = get_logger("WindowsCleaner")
        self.user_home = Path.home()
        self.temp_dir = Path(os.environ.get('TEMP', ''))
        self.local_app_data = Path(os.environ.get('LOCALAPPDATA', ''))
        self.app_data = Path(os.environ.get('APPDATA', ''))
        
        # Diretórios protegidos - NUNCA apagar
        self.protected_dirs = {
            Path("C:/Windows/System32"),
            Path("C:/Windows/SysWOW64"),
            Path("C:/Program Files"),
            Path("C:/Program Files (x86)"),
            self.user_home / "Documents",
            self.user_home / "Desktop",
            self.user_home / "Pictures",
            self.user_home / "Downloads",
        }
        
        # Extensões perigosas - arquivos que NÃO devem ser apagados
        self.protected_extensions = {
            '.exe', '.dll', '.sys', '.msi', '.bat', '.cmd', '.ps1',
            '.doc', '.docx', '.xls', '.xlsx', '.pdf', '.ppt', '.pptx'
        }
        
    def get_categories(self) -> Dict[str, Dict]:
        """
        Retorna as categorias de limpeza disponíveis.
        """
        return {
            'temp_user': {
                'name': 'Arquivos Temporários do Usuário',
                'icon': '📁',
                'description': 'Pasta TEMP do usuário atual'
            },
            'temp_windows': {
                'name': 'Arquivos Temporários do Windows',
                'icon': '🪟',
                'description': 'Pasta C:\\Windows\\Temp'
            },
            'prefetch': {
                'name': 'Prefetch',
                'icon': '⚡',
                'description': 'Arquivos de pré-carregamento do Windows'
            },
            'browser_cache': {
                'name': 'Cache de Navegadores',
                'icon': '🌐',
                'description': 'Cache do Chrome, Firefox, Edge'
            },
            'windows_cache': {
                'name': 'Cache do Windows',
                'icon': '💾',
                'description': 'Cache de thumbnails e ícones'
            },
            'recent_files': {
                'name': 'Arquivos Recentes',
                'icon': '📋',
                'description': 'Lista de arquivos recentes'
            },
            'log_files': {
                'name': 'Arquivos de Log',
                'icon': '📝',
                'description': 'Arquivos .log antigos'
            },
            'old_files': {
                'name': 'Arquivos Antigos/Backup',
                'icon': '📦',
                'description': 'Arquivos .old, .bak, .tmp'
            }
        }
        
    def scan_category(self, category: str) -> Tuple[List[str], int]:
        """
        Escaneia uma categoria e retorna os arquivos encontrados.
        
        Args:
            category: ID da categoria
            
        Returns:
            Tupla com lista de arquivos e tamanho total
        """
        scan_methods = {
            'temp_user': self._scan_temp_user,
            'temp_windows': self._scan_temp_windows,
            'prefetch': self._scan_prefetch,
            'browser_cache': self._scan_browser_cache,
            'windows_cache': self._scan_windows_cache,
            'recent_files': self._scan_recent_files,
            'log_files': self._scan_log_files,
            'old_files': self._scan_old_files,
        }
        
        method = scan_methods.get(category)
        if method:
            return method()
        return [], 0
        
    def _is_safe_to_delete(self, path: Path) -> bool:
        """
        Verifica se é seguro deletar um arquivo/diretório.
        """
        try:
            # Não deletar diretórios protegidos
            for protected in self.protected_dirs:
                if path == protected or protected in path.parents:
                    return False
                    
            # Não deletar arquivos com extensões protegidas
            if path.suffix.lower() in self.protected_extensions:
                return False
                
            # Não deletar arquivos do sistema
            if 'Windows\\System32' in str(path) or 'Windows\\SysWOW64' in str(path):
                return False
                
            return True
            
        except Exception:
            return False
            
    def _scan_directory(self, directory: Path, patterns: List[str] = None) -> Tuple[List[str], int]:
        """
        Escaneia um diretório e retorna arquivos encontrados.
        """
        files = []
        total_size = 0
        
        if not directory.exists():
            return files, total_size
            
        try:
            if patterns:
                for pattern in patterns:
                    for file_path in directory.rglob(pattern):
                        if file_path.is_file() and self._is_safe_to_delete(file_path):
                            size = get_file_size(file_path)
                            files.append(str(file_path))
                            total_size += size
            else:
                for file_path in directory.rglob('*'):
                    if file_path.is_file() and self._is_safe_to_delete(file_path):
                        size = get_file_size(file_path)
                        files.append(str(file_path))
                        total_size += size
                        
        except PermissionError:
            self.logger.warning(f"Sem permissão para acessar: {directory}")
        except Exception as e:
            self.logger.error(f"Erro ao escanear {directory}: {e}")
            
        return files, total_size
        
    def _scan_temp_user(self) -> Tuple[List[str], int]:
        """Escaneia a pasta TEMP do usuário."""
        return self._scan_directory(self.temp_dir)
        
    def _scan_temp_windows(self) -> Tuple[List[str], int]:
        """Escaneia a pasta C:\\Windows\\Temp."""
        windows_temp = Path("C:/Windows/Temp")
        return self._scan_directory(windows_temp)
        
    def _scan_prefetch(self) -> Tuple[List[str], int]:
        """Escaneia a pasta Prefetch."""
        prefetch_dir = Path("C:/Windows/Prefetch")
        return self._scan_directory(prefetch_dir, ['*.pf'])
        
    def _scan_browser_cache(self) -> Tuple[List[str], int]:
        """Escaneia cache de navegadores."""
        files = []
        total_size = 0
        
        # Chrome
        chrome_cache = self.local_app_data / "Google/Chrome/User Data/Default/Cache"
        chrome_code_cache = self.local_app_data / "Google/Chrome/User Data/Default/Code Cache"
        
        # Edge
        edge_cache = self.local_app_data / "Microsoft/Edge/User Data/Default/Cache"
        edge_code_cache = self.local_app_data / "Microsoft/Edge/User Data/Default/Code Cache"
        
        # Firefox
        firefox_profiles = self.local_app_data / "Mozilla/Firefox/Profiles"
        
        cache_dirs = [
            chrome_cache, chrome_code_cache,
            edge_cache, edge_code_cache
        ]
        
        for cache_dir in cache_dirs:
            f, s = self._scan_directory(cache_dir)
            files.extend(f)
            total_size += s
            
        # Firefox cache
        if firefox_profiles.exists():
            for profile in firefox_profiles.iterdir():
                if profile.is_dir():
                    ff_cache = profile / "cache2"
                    f, s = self._scan_directory(ff_cache)
                    files.extend(f)
                    total_size += s
                    
        return files, total_size
        
    def _scan_windows_cache(self) -> Tuple[List[str], int]:
        """Escaneia cache do Windows (thumbnails, ícones)."""
        files = []
        total_size = 0
        
        # Thumbnail cache
        thumbnail_cache = self.local_app_data / "Microsoft/Windows/Explorer"
        
        for file_path in thumbnail_cache.glob("thumbcache_*.db"):
            if self._is_safe_to_delete(file_path):
                size = get_file_size(file_path)
                files.append(str(file_path))
                total_size += size
                
        # Icon cache
        icon_cache = self.local_app_data / "IconCache.db"
        if icon_cache.exists() and self._is_safe_to_delete(icon_cache):
            size = get_file_size(icon_cache)
            files.append(str(icon_cache))
            total_size += size
            
        return files, total_size
        
    def _scan_recent_files(self) -> Tuple[List[str], int]:
        """Escaneia arquivos recentes (atalhos)."""
        recent_dir = self.app_data / "Microsoft/Windows/Recent"
        return self._scan_directory(recent_dir, ['*.lnk'])
        
    def _scan_log_files(self) -> Tuple[List[str], int]:
        """Escaneia arquivos de log."""
        files = []
        total_size = 0
        
        # Logs em várias localizações
        log_locations = [
            self.temp_dir,
            self.local_app_data,
            Path("C:/Windows/Logs"),
        ]
        
        for location in log_locations:
            f, s = self._scan_directory(location, ['*.log'])
            files.extend(f)
            total_size += s
            
        return files, total_size
        
    def _scan_old_files(self) -> Tuple[List[str], int]:
        """Escaneia arquivos antigos/backup."""
        files = []
        total_size = 0
        
        patterns = ['*.old', '*.bak', '*.tmp', '*.temp', '~*']
        
        scan_locations = [
            self.temp_dir,
            self.user_home,
            self.local_app_data,
        ]
        
        for location in scan_locations:
            f, s = self._scan_directory(location, patterns)
            files.extend(f)
            total_size += s
            
        return files, total_size
        
    def clean_files(self, files: List[str]) -> Tuple[int, int, int]:
        """
        Remove os arquivos da lista.
        
        Args:
            files: Lista de caminhos de arquivos
            
        Returns:
            Tupla com (arquivos removidos, tamanho liberado, erros)
        """
        removed = 0
        size_freed = 0
        errors = 0
        
        for file_path in files:
            try:
                path = Path(file_path)
                
                if not path.exists():
                    continue
                    
                if not self._is_safe_to_delete(path):
                    self.logger.warning(f"Arquivo protegido ignorado: {file_path}")
                    errors += 1
                    continue
                    
                size = get_file_size(path)
                
                if path.is_file():
                    success = safe_remove_file(path)
                else:
                    success = safe_remove_dir(path)
                    
                if success:
                    removed += 1
                    size_freed += size
                    self.logger.debug(f"Removido: {file_path}")
                else:
                    errors += 1
                    
            except Exception as e:
                self.logger.error(f"Erro ao remover {file_path}: {e}")
                errors += 1
                
        return removed, size_freed, errors
        
    def empty_recycle_bin(self) -> bool:
        """
        Esvazia a Lixeira do Windows.
        
        Returns:
            True se bem-sucedido
        """
        try:
            # Usa a API do Windows
            SHERB_NOCONFIRMATION = 0x00000001
            SHERB_NOPROGRESSUI = 0x00000002
            SHERB_NOSOUND = 0x00000004
            
            flags = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
            
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
            self.logger.info("Lixeira esvaziada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao esvaziar lixeira: {e}")
            return False


# Para testes diretos
if __name__ == "__main__":
    cleaner = WindowsCleaner()
    
    print("Categorias disponíveis:")
    for cat_id, info in cleaner.get_categories().items():
        print(f"  {info['icon']} {info['name']}")
        
    print("\nEscaneando arquivos temporários do usuário...")
    files, size = cleaner.scan_category('temp_user')
    print(f"Encontrados: {len(files)} arquivos ({size} bytes)")
