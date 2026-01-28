#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
limpeza_david - Módulo de Limpeza para Linux
Autor: David Fernandes
Descrição: Implementa a limpeza de arquivos temporários, cache e 
           arquivos desnecessários no Linux.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime, timedelta

# Importa utilitários
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils import get_logger, safe_remove_file, safe_remove_dir, get_file_size


class LinuxCleaner:
    """
    Classe para limpeza de sistema no Linux.
    Remove arquivos temporários, cache e arquivos desnecessários.
    """
    
    def __init__(self):
        self.logger = get_logger("LinuxCleaner")
        self.user_home = Path.home()
        self.uid = os.getuid()
        
        # Diretórios protegidos - NUNCA apagar
        self.protected_dirs = {
            Path("/"),
            Path("/bin"),
            Path("/boot"),
            Path("/dev"),
            Path("/etc"),
            Path("/lib"),
            Path("/lib64"),
            Path("/opt"),
            Path("/proc"),
            Path("/root"),
            Path("/sbin"),
            Path("/sys"),
            Path("/usr"),
            self.user_home / "Documents",
            self.user_home / "Documentos",
            self.user_home / "Desktop",
            self.user_home / "Área de trabalho",
            self.user_home / "Pictures",
            self.user_home / "Imagens",
            self.user_home / "Downloads",
            self.user_home / ".ssh",
            self.user_home / ".gnupg",
            self.user_home / ".config",
        }
        
        # Arquivos/diretórios críticos - NUNCA apagar
        self.protected_files = {
            '.bashrc', '.bash_profile', '.profile', '.zshrc',
            '.gitconfig', '.ssh', '.gnupg', 'passwd', 'shadow',
            'fstab', 'hostname', 'hosts'
        }
        
    def get_categories(self) -> Dict[str, Dict]:
        """
        Retorna as categorias de limpeza disponíveis.
        """
        return {
            'tmp': {
                'name': 'Arquivos Temporários (/tmp)',
                'icon': '📁',
                'description': 'Arquivos temporários do sistema'
            },
            'var_tmp': {
                'name': 'Arquivos Temporários (/var/tmp)',
                'icon': '📂',
                'description': 'Arquivos temporários persistentes'
            },
            'user_cache': {
                'name': 'Cache do Usuário',
                'icon': '💾',
                'description': 'Cache em ~/.cache'
            },
            'browser_cache': {
                'name': 'Cache de Navegadores',
                'icon': '🌐',
                'description': 'Cache do Chrome, Firefox, etc.'
            },
            'thumbnails': {
                'name': 'Thumbnails',
                'icon': '🖼️',
                'description': 'Cache de miniaturas de imagens'
            },
            'old_logs': {
                'name': 'Logs Antigos',
                'icon': '📝',
                'description': 'Arquivos de log antigos'
            },
            'trash': {
                'name': 'Lixeira',
                'icon': '🗑️',
                'description': 'Arquivos na lixeira do usuário'
            },
            'old_files': {
                'name': 'Arquivos Antigos/Backup',
                'icon': '📦',
                'description': 'Arquivos .old, .bak, ~backup'
            },
            'package_cache': {
                'name': 'Cache de Pacotes',
                'icon': '📦',
                'description': 'Cache do apt/dnf/pacman'
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
            'tmp': self._scan_tmp,
            'var_tmp': self._scan_var_tmp,
            'user_cache': self._scan_user_cache,
            'browser_cache': self._scan_browser_cache,
            'thumbnails': self._scan_thumbnails,
            'old_logs': self._scan_old_logs,
            'trash': self._scan_trash,
            'old_files': self._scan_old_files,
            'package_cache': self._scan_package_cache,
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
            path = Path(path).resolve()
            
            # Não deletar diretórios protegidos ou seus pais
            for protected in self.protected_dirs:
                try:
                    protected = protected.resolve()
                    if path == protected:
                        return False
                    # Verifica se o path é pai de um diretório protegido
                    if protected.is_relative_to(path):
                        return False
                except:
                    pass
                    
            # Não deletar arquivos protegidos
            if path.name in self.protected_files:
                return False
                
            # Não deletar links simbólicos que apontam para lugares críticos
            if path.is_symlink():
                target = path.resolve()
                for protected in self.protected_dirs:
                    try:
                        if target == protected.resolve():
                            return False
                    except:
                        pass
                        
            # Não deletar arquivos que não pertencem ao usuário (exceto /tmp)
            if '/tmp' not in str(path) and '/var/tmp' not in str(path):
                try:
                    if path.exists() and path.stat().st_uid != self.uid:
                        return False
                except:
                    pass
                    
            return True
            
        except Exception:
            return False
            
    def _scan_directory(self, directory: Path, patterns: List[str] = None, 
                       max_age_days: int = None) -> Tuple[List[str], int]:
        """
        Escaneia um diretório e retorna arquivos encontrados.
        
        Args:
            directory: Diretório a escanear
            patterns: Padrões de arquivo (glob)
            max_age_days: Idade máxima em dias (arquivos mais antigos)
        """
        files = []
        total_size = 0
        
        if not directory.exists():
            return files, total_size
            
        try:
            if patterns:
                for pattern in patterns:
                    for file_path in directory.rglob(pattern):
                        if self._check_file(file_path, max_age_days):
                            size = get_file_size(file_path)
                            files.append(str(file_path))
                            total_size += size
            else:
                for file_path in directory.rglob('*'):
                    if self._check_file(file_path, max_age_days):
                        size = get_file_size(file_path)
                        files.append(str(file_path))
                        total_size += size
                        
        except PermissionError:
            self.logger.warning(f"Sem permissão para acessar: {directory}")
        except Exception as e:
            self.logger.error(f"Erro ao escanear {directory}: {e}")
            
        return files, total_size
        
    def _check_file(self, file_path: Path, max_age_days: int = None) -> bool:
        """Verifica se um arquivo deve ser incluído na lista."""
        if not file_path.is_file():
            return False
            
        if not self._is_safe_to_delete(file_path):
            return False
            
        if max_age_days:
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                age = datetime.now() - mtime
                if age.days < max_age_days:
                    return False
            except:
                pass
                
        return True
        
    def _scan_tmp(self) -> Tuple[List[str], int]:
        """Escaneia /tmp (arquivos com mais de 1 dia)."""
        files = []
        total_size = 0
        
        tmp_dir = Path("/tmp")
        
        if tmp_dir.exists():
            for item in tmp_dir.iterdir():
                try:
                    # Pula arquivos muito recentes (menos de 1 hora)
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    age = datetime.now() - mtime
                    
                    if age < timedelta(hours=1):
                        continue
                        
                    if self._is_safe_to_delete(item):
                        if item.is_file():
                            size = get_file_size(item)
                            files.append(str(item))
                            total_size += size
                        elif item.is_dir():
                            f, s = self._scan_directory(item)
                            files.extend(f)
                            total_size += s
                except PermissionError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Erro ao verificar {item}: {e}")
                    
        return files, total_size
        
    def _scan_var_tmp(self) -> Tuple[List[str], int]:
        """Escaneia /var/tmp (arquivos com mais de 7 dias)."""
        var_tmp = Path("/var/tmp")
        return self._scan_directory(var_tmp, max_age_days=7)
        
    def _scan_user_cache(self) -> Tuple[List[str], int]:
        """Escaneia cache do usuário ~/.cache."""
        cache_dir = self.user_home / ".cache"
        
        # Exclui caches importantes
        exclude_dirs = {
            'pip', 'npm', 'yarn', 'go-build', 'cargo', 'rustup',
            'mesa_shader_cache', 'fontconfig'
        }
        
        files = []
        total_size = 0
        
        if cache_dir.exists():
            for item in cache_dir.iterdir():
                if item.name in exclude_dirs:
                    continue
                    
                if item.is_dir():
                    f, s = self._scan_directory(item)
                    files.extend(f)
                    total_size += s
                elif item.is_file() and self._is_safe_to_delete(item):
                    size = get_file_size(item)
                    files.append(str(item))
                    total_size += size
                    
        return files, total_size
        
    def _scan_browser_cache(self) -> Tuple[List[str], int]:
        """Escaneia cache de navegadores."""
        files = []
        total_size = 0
        
        # Chrome/Chromium
        chrome_paths = [
            self.user_home / ".config/google-chrome/Default/Cache",
            self.user_home / ".config/google-chrome/Default/Code Cache",
            self.user_home / ".config/chromium/Default/Cache",
            self.user_home / ".config/chromium/Default/Code Cache",
        ]
        
        # Firefox
        firefox_profiles = self.user_home / ".mozilla/firefox"
        
        # Brave
        brave_paths = [
            self.user_home / ".config/BraveSoftware/Brave-Browser/Default/Cache",
        ]
        
        # Opera
        opera_paths = [
            self.user_home / ".config/opera/Cache",
        ]
        
        all_paths = chrome_paths + brave_paths + opera_paths
        
        for cache_path in all_paths:
            if cache_path.exists():
                f, s = self._scan_directory(cache_path)
                files.extend(f)
                total_size += s
                
        # Firefox - precisa buscar perfis
        if firefox_profiles.exists():
            for profile in firefox_profiles.iterdir():
                if profile.is_dir() and '.default' in profile.name:
                    cache_path = profile / "cache2"
                    if cache_path.exists():
                        f, s = self._scan_directory(cache_path)
                        files.extend(f)
                        total_size += s
                        
        return files, total_size
        
    def _scan_thumbnails(self) -> Tuple[List[str], int]:
        """Escaneia cache de thumbnails."""
        thumbnails_dir = self.user_home / ".cache/thumbnails"
        return self._scan_directory(thumbnails_dir)
        
    def _scan_old_logs(self) -> Tuple[List[str], int]:
        """Escaneia logs antigos (arquivos com mais de 7 dias)."""
        files = []
        total_size = 0
        
        log_dirs = [
            Path("/var/log"),
            self.user_home / ".local/share/xorg",
        ]
        
        patterns = ['*.log', '*.log.*', '*.old', '*.gz']
        
        for log_dir in log_dirs:
            if log_dir.exists():
                f, s = self._scan_directory(log_dir, patterns=patterns, max_age_days=7)
                files.extend(f)
                total_size += s
                
        return files, total_size
        
    def _scan_trash(self) -> Tuple[List[str], int]:
        """Escaneia a lixeira do usuário."""
        files = []
        total_size = 0
        
        trash_paths = [
            self.user_home / ".local/share/Trash/files",
            self.user_home / ".local/share/Trash/info",
        ]
        
        for trash_path in trash_paths:
            if trash_path.exists():
                f, s = self._scan_directory(trash_path)
                files.extend(f)
                total_size += s
                
        return files, total_size
        
    def _scan_old_files(self) -> Tuple[List[str], int]:
        """Escaneia arquivos de backup antigos."""
        patterns = ['*.old', '*.bak', '*.backup', '*~', '*.swp', '*.swo']
        
        scan_dirs = [
            self.user_home,
            self.user_home / ".config",
        ]
        
        files = []
        total_size = 0
        
        for scan_dir in scan_dirs:
            # Limita a profundidade para evitar escanear muitos arquivos
            if scan_dir.exists():
                for pattern in patterns:
                    for file_path in scan_dir.glob(pattern):
                        if file_path.is_file() and self._is_safe_to_delete(file_path):
                            size = get_file_size(file_path)
                            files.append(str(file_path))
                            total_size += size
                            
        return files, total_size
        
    def _scan_package_cache(self) -> Tuple[List[str], int]:
        """Escaneia cache de gerenciadores de pacotes."""
        files = []
        total_size = 0
        
        # APT (Debian/Ubuntu)
        apt_cache = Path("/var/cache/apt/archives")
        if apt_cache.exists():
            f, s = self._scan_directory(apt_cache, patterns=['*.deb'])
            files.extend(f)
            total_size += s
            
        # DNF/YUM (Fedora/RHEL)
        dnf_cache = Path("/var/cache/dnf")
        if dnf_cache.exists():
            f, s = self._scan_directory(dnf_cache)
            files.extend(f)
            total_size += s
            
        # Pacman (Arch)
        pacman_cache = Path("/var/cache/pacman/pkg")
        if pacman_cache.exists():
            f, s = self._scan_directory(pacman_cache, patterns=['*.pkg.tar.*'])
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
                
                if path.is_file() or path.is_symlink():
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
        
    def clean_apt_cache(self) -> bool:
        """
        Executa apt clean para limpar cache de pacotes.
        Requer permissões de root.
        """
        try:
            result = subprocess.run(
                ['sudo', 'apt', 'clean'],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache apt: {e}")
            return False


# Para testes diretos
if __name__ == "__main__":
    cleaner = LinuxCleaner()
    
    print("Categorias disponíveis:")
    for cat_id, info in cleaner.get_categories().items():
        print(f"  {info['icon']} {info['name']}")
        
    print("\nEscaneando cache do usuário...")
    files, size = cleaner.scan_category('user_cache')
    print(f"Encontrados: {len(files)} arquivos ({size} bytes)")
