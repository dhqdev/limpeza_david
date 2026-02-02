#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
limpeza_david - Ferramenta de Limpeza de Sistema
Autor: David Fernandes
Descrição: Ferramenta cross-platform para limpeza de arquivos temporários,
           cache e arquivos desnecessários do sistema.
"""

import os
import sys
import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# Adiciona o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import (
    format_size, 
    get_logger, 
    CENTER_WINDOW,
    COLORS
)

# Importa o cleaner apropriado baseado no SO
if platform.system() == 'Windows':
    from app.cleaner.windows import WindowsCleaner as SystemCleaner
else:
    from app.cleaner.linux import LinuxCleaner as SystemCleaner


class LimpezaDavidApp:
    """
    Aplicação principal com interface gráfica Tkinter.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Limpeza David - Limpador de Sistema")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Configurar ícone se existir (desabilitado por padrão - pode causar erro com ícones grandes)
        # self._set_icon()
        
        # Inicializa o cleaner
        self.cleaner = SystemCleaner()
        self.logger = get_logger("LimpezaDavid")
        
        # Variáveis de controle
        self.scan_results = {}
        self.is_scanning = False
        self.is_cleaning = False
        
        # Checkboxes para categorias
        self.category_vars = {}
        
        # Configura o estilo
        self._setup_style()
        
        # Constrói a interface
        self._build_ui()
        
        # Centraliza a janela
        CENTER_WINDOW(self.root)
        
    def _set_icon(self):
        """Define o ícone da aplicação."""
        try:
            # Tenta encontrar o ícone
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_paths = [
                os.path.join(base_path, 'assets', 'icon.png'),
                os.path.join(base_path, 'assets', 'icon.ico'),
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    if icon_path.endswith('.png'):
                        icon = tk.PhotoImage(file=icon_path)
                        self.root.iconphoto(True, icon)
                    elif icon_path.endswith('.ico') and platform.system() == 'Windows':
                        self.root.iconbitmap(icon_path)
                    break
        except Exception as e:
            self.logger.warning(f"Não foi possível carregar o ícone: {e}")
    
    def _setup_style(self):
        """Configura o estilo visual da aplicação."""
        style = ttk.Style()
        
        # Tema base
        if platform.system() == 'Windows':
            style.theme_use('vista')
        else:
            try:
                style.theme_use('clam')
            except:
                pass
        
        # Cores personalizadas
        self.root.configure(bg=COLORS['bg'])
        
        # Configurar estilos
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 18, 'bold'),
                       foreground=COLORS['primary'])
        
        style.configure('Header.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=COLORS['text'])
        
        style.configure('Info.TLabel',
                       font=('Segoe UI', 10),
                       foreground=COLORS['text_secondary'])
        
        style.configure('Success.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=COLORS['success'])
        
        style.configure('Action.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       padding=(20, 10))
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       padding=(15, 8))
                       
    def _build_ui(self):
        """Constrói a interface gráfica."""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === Cabeçalho ===
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame, 
            text="🧹 Limpeza David",
            style='Title.TLabel'
        )
        title_label.pack(side=tk.LEFT)
        
        # Info do sistema
        system_info = f"Sistema: {platform.system()} {platform.release()}"
        system_label = ttk.Label(
            header_frame,
            text=system_info,
            style='Info.TLabel'
        )
        system_label.pack(side=tk.RIGHT)
        
        # === Frame de Categorias ===
        categories_frame = ttk.LabelFrame(
            main_frame, 
            text="📂 Categorias de Limpeza",
            padding="15"
        )
        categories_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid de checkboxes
        categories = self.cleaner.get_categories()
        
        for i, (cat_id, cat_info) in enumerate(categories.items()):
            var = tk.BooleanVar(value=True)
            self.category_vars[cat_id] = var
            
            cb = ttk.Checkbutton(
                categories_frame,
                text=f"{cat_info['icon']} {cat_info['name']}",
                variable=var
            )
            cb.grid(row=i // 3, column=i % 3, sticky=tk.W, padx=10, pady=5)
        
        # === Botões de Ação ===
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.scan_btn = ttk.Button(
            buttons_frame,
            text="🔍 Analisar Sistema",
            style='Action.TButton',
            command=self._start_scan
        )
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clean_btn = ttk.Button(
            buttons_frame,
            text="🗑️ Limpar Selecionados",
            style='Action.TButton',
            command=self._start_clean,
            state=tk.DISABLED
        )
        self.clean_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.select_all_btn = ttk.Button(
            buttons_frame,
            text="✅ Selecionar Todos",
            style='Secondary.TButton',
            command=self._select_all
        )
        self.select_all_btn.pack(side=tk.RIGHT)
        
        self.deselect_all_btn = ttk.Button(
            buttons_frame,
            text="❌ Desmarcar Todos",
            style='Secondary.TButton',
            command=self._deselect_all
        )
        self.deselect_all_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # === Barra de Progresso ===
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            progress_frame,
            text="Pronto para análise",
            style='Info.TLabel'
        )
        self.status_label.pack(pady=(5, 0))
        
        # === Área de Resultados/Log ===
        results_frame = ttk.LabelFrame(
            main_frame,
            text="📋 Log de Operações",
            padding="10"
        )
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.log_text = scrolledtext.ScrolledText(
            results_frame,
            height=12,
            font=('Consolas', 9),
            wrap=tk.WORD,
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Tags para colorir o log
        self.log_text.tag_configure('info', foreground='#569cd6')
        self.log_text.tag_configure('success', foreground='#4ec9b0')
        self.log_text.tag_configure('warning', foreground='#dcdcaa')
        self.log_text.tag_configure('error', foreground='#f14c4c')
        self.log_text.tag_configure('header', foreground='#c586c0', font=('Consolas', 9, 'bold'))
        
        # === Resumo ===
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X)
        
        self.summary_label = ttk.Label(
            summary_frame,
            text="Espaço a liberar: 0 B",
            style='Success.TLabel'
        )
        self.summary_label.pack(side=tk.LEFT)
        
        # Versão
        version_label = ttk.Label(
            summary_frame,
            text="v1.0.0",
            style='Info.TLabel'
        )
        version_label.pack(side=tk.RIGHT)
        
        # Log inicial
        self._log("═" * 50, 'header')
        self._log("🧹 Limpeza David - Limpador de Sistema", 'header')
        self._log(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 'info')
        self._log(f"💻 Sistema: {platform.system()} {platform.release()}", 'info')
        self._log("═" * 50, 'header')
        self._log("")
        self._log("Clique em 'Analisar Sistema' para iniciar.", 'info')
        
    def _log(self, message, tag=None):
        """Adiciona mensagem ao log."""
        self.log_text.configure(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
    def _update_status(self, message):
        """Atualiza o status."""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
        
    def _update_progress(self, value):
        """Atualiza a barra de progresso."""
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def _select_all(self):
        """Seleciona todas as categorias."""
        for var in self.category_vars.values():
            var.set(True)
            
    def _deselect_all(self):
        """Desmarca todas as categorias."""
        for var in self.category_vars.values():
            var.set(False)
            
    def _get_selected_categories(self):
        """Retorna as categorias selecionadas."""
        return [cat_id for cat_id, var in self.category_vars.items() if var.get()]
        
    def _start_scan(self):
        """Inicia a análise em uma thread separada."""
        if self.is_scanning:
            return
            
        selected = self._get_selected_categories()
        if not selected:
            messagebox.showwarning(
                "Aviso",
                "Selecione pelo menos uma categoria para analisar."
            )
            return
            
        self.is_scanning = True
        self.scan_btn.configure(state=tk.DISABLED)
        self.clean_btn.configure(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._scan_thread, args=(selected,))
        thread.daemon = True
        thread.start()
        
    def _scan_thread(self, categories):
        """Thread de análise."""
        try:
            self._log("")
            self._log("🔍 Iniciando análise do sistema...", 'header')
            self._update_status("Analisando...")
            
            total_size = 0
            total_files = 0
            self.scan_results = {}
            
            for i, cat_id in enumerate(categories):
                progress = ((i + 1) / len(categories)) * 100
                self._update_progress(progress)
                
                cat_info = self.cleaner.get_categories()[cat_id]
                self._log(f"  📂 Analisando: {cat_info['name']}...", 'info')
                self._update_status(f"Analisando: {cat_info['name']}...")
                
                # Escaneia a categoria
                files, size = self.cleaner.scan_category(cat_id)
                
                self.scan_results[cat_id] = {
                    'files': files,
                    'size': size
                }
                
                total_size += size
                total_files += len(files)
                
                self._log(f"    └─ {len(files)} arquivos ({format_size(size)})", 'success')
                
            self._log("")
            self._log("═" * 50, 'header')
            self._log(f"📊 RESUMO DA ANÁLISE:", 'header')
            self._log(f"   Total de arquivos: {total_files}", 'success')
            self._log(f"   Espaço a liberar: {format_size(total_size)}", 'success')
            self._log("═" * 50, 'header')
            
            self.summary_label.configure(
                text=f"Espaço a liberar: {format_size(total_size)} ({total_files} arquivos)"
            )
            
            self._update_status("Análise concluída!")
            self._update_progress(100)
            
            if total_files > 0:
                self.clean_btn.configure(state=tk.NORMAL)
                self._log("")
                self._log("✅ Clique em 'Limpar Selecionados' para remover os arquivos.", 'info')
            else:
                self._log("")
                self._log("✨ Sistema já está limpo! Nenhum arquivo para remover.", 'success')
                
        except Exception as e:
            self._log(f"❌ Erro durante análise: {str(e)}", 'error')
            self.logger.error(f"Erro na análise: {e}")
        finally:
            self.is_scanning = False
            self.scan_btn.configure(state=tk.NORMAL)
            
    def _start_clean(self):
        """Inicia a limpeza em uma thread separada."""
        if self.is_cleaning or not self.scan_results:
            return
            
        # Confirmação
        total_files = sum(len(r['files']) for r in self.scan_results.values())
        total_size = sum(r['size'] for r in self.scan_results.values())
        
        confirm = messagebox.askyesno(
            "Confirmar Limpeza",
            f"Deseja remover {total_files} arquivos?\n"
            f"Espaço a ser liberado: {format_size(total_size)}\n\n"
            f"⚠️ Esta ação não pode ser desfeita!"
        )
        
        if not confirm:
            return
            
        self.is_cleaning = True
        self.scan_btn.configure(state=tk.DISABLED)
        self.clean_btn.configure(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._clean_thread)
        thread.daemon = True
        thread.start()
        
    def _clean_thread(self):
        """Thread de limpeza."""
        try:
            self._log("")
            self._log("🗑️ Iniciando limpeza...", 'header')
            self._update_status("Limpando...")
            
            total_removed = 0
            total_size_freed = 0
            total_errors = 0
            
            categories = list(self.scan_results.keys())
            
            for i, cat_id in enumerate(categories):
                progress = ((i + 1) / len(categories)) * 100
                self._update_progress(progress)
                
                cat_info = self.cleaner.get_categories()[cat_id]
                files = self.scan_results[cat_id]['files']
                
                if not files:
                    continue
                    
                self._log(f"  🧹 Limpando: {cat_info['name']}...", 'info')
                self._update_status(f"Limpando: {cat_info['name']}...")
                
                # Remove os arquivos
                removed, size_freed, errors = self.cleaner.clean_files(files)
                
                total_removed += removed
                total_size_freed += size_freed
                total_errors += errors
                
                self._log(f"    └─ {removed} removidos ({format_size(size_freed)})", 'success')
                if errors > 0:
                    self._log(f"    └─ {errors} erros (arquivos em uso ou protegidos)", 'warning')
                    
            self._log("")
            self._log("═" * 50, 'header')
            self._log(f"✅ LIMPEZA CONCLUÍDA!", 'header')
            self._log(f"   Arquivos removidos: {total_removed}", 'success')
            self._log(f"   Espaço liberado: {format_size(total_size_freed)}", 'success')
            if total_errors > 0:
                self._log(f"   Erros: {total_errors}", 'warning')
            self._log("═" * 50, 'header')
            
            self.summary_label.configure(
                text=f"✅ Liberado: {format_size(total_size_freed)}"
            )
            
            self._update_status("Limpeza concluída!")
            self._update_progress(100)
            
            # Limpa os resultados
            self.scan_results = {}
            
            messagebox.showinfo(
                "Limpeza Concluída",
                f"✅ Limpeza realizada com sucesso!\n\n"
                f"Arquivos removidos: {total_removed}\n"
                f"Espaço liberado: {format_size(total_size_freed)}"
            )
            
        except Exception as e:
            self._log(f"❌ Erro durante limpeza: {str(e)}", 'error')
            self.logger.error(f"Erro na limpeza: {e}")
        finally:
            self.is_cleaning = False
            self.scan_btn.configure(state=tk.NORMAL)
            
    def run(self):
        """Inicia a aplicação."""
        self.logger.info("Aplicação iniciada")
        self.root.mainloop()
        self.logger.info("Aplicação encerrada")


def main():
    """Ponto de entrada principal."""
    app = LimpezaDavidApp()
    app.run()


if __name__ == "__main__":
    main()
