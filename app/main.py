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
import math
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


class SplashScreen:
    """
    Tela de splash animada com vassourinha e barra de carregamento.
    """
    
    def __init__(self, on_complete_callback):
        self.root = tk.Tk()
        self.root.title("Limpeza David")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # Remove bordas da janela
        
        # Centraliza a janela
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 400) // 2
        self.root.geometry(f"500x400+{x}+{y}")
        
        self.on_complete = on_complete_callback
        self.angle = 0
        self.progress = 0
        self.loading_text = "Iniciando..."
        
        self._build_ui()
        self._animate()
        
    def _build_ui(self):
        """Constrói a interface da splash screen."""
        # Frame principal com gradiente simulado
        self.main_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Borda decorativa
        border_frame = tk.Frame(self.main_frame, bg='#6366f1', padx=3, pady=3)
        border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        inner_frame = tk.Frame(border_frame, bg='#1a1a2e')
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para animação
        self.canvas = tk.Canvas(
            inner_frame, 
            width=480, 
            height=250,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.canvas.pack(pady=(30, 10))
        
        # Título
        title_label = tk.Label(
            inner_frame,
            text="🧹 Limpeza David",
            font=('Segoe UI', 28, 'bold'),
            fg='#6366f1',
            bg='#1a1a2e'
        )
        title_label.pack(pady=(0, 5))
        
        # Subtítulo
        subtitle_label = tk.Label(
            inner_frame,
            text="Limpador de Sistema Inteligente",
            font=('Segoe UI', 12),
            fg='#8b8b9e',
            bg='#1a1a2e'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Frame da barra de progresso
        progress_frame = tk.Frame(inner_frame, bg='#1a1a2e')
        progress_frame.pack(fill=tk.X, padx=50, pady=(10, 5))
        
        # Barra de progresso personalizada
        self.progress_canvas = tk.Canvas(
            progress_frame,
            width=380,
            height=8,
            bg='#2d2d44',
            highlightthickness=0
        )
        self.progress_canvas.pack()
        
        # Label de status
        self.status_label = tk.Label(
            inner_frame,
            text="Iniciando...",
            font=('Segoe UI', 10),
            fg='#6b7280',
            bg='#1a1a2e'
        )
        self.status_label.pack(pady=(10, 0))
        
    def _draw_broom(self, angle):
        """Desenha a vassourinha animada."""
        self.canvas.delete("all")
        
        cx, cy = 240, 125  # Centro
        
        # Partículas de poeira animadas
        for i in range(8):
            particle_angle = (angle * 2 + i * 45) * math.pi / 180
            distance = 80 + math.sin(angle * 0.1 + i) * 20
            px = cx + math.cos(particle_angle) * distance
            py = cy + math.sin(particle_angle) * distance
            size = 3 + math.sin(angle * 0.05 + i) * 2
            alpha = int(100 + math.sin(angle * 0.1 + i) * 50)
            alpha = max(0, min(255, alpha))
            color = f'#{alpha:02x}{alpha:02x}{min(255, alpha + 50):02x}'
            self.canvas.create_oval(
                px - size, py - size, px + size, py + size,
                fill=color, outline=''
            )
        
        # Círculo de fundo brilhante
        glow_size = 90 + math.sin(angle * 0.05) * 10
        self.canvas.create_oval(
            cx - glow_size, cy - glow_size,
            cx + glow_size, cy + glow_size,
            fill='#252540', outline=''
        )
        
        # Vassourinha principal
        broom_angle = math.sin(angle * 0.08) * 15  # Balanço
        rad = math.radians(broom_angle - 45)
        
        # Cabo da vassoura
        handle_length = 60
        hx = cx - math.cos(rad) * handle_length
        hy = cy - math.sin(rad) * handle_length
        self.canvas.create_line(
            cx, cy, hx, hy,
            fill='#8B4513', width=8, capstyle=tk.ROUND
        )
        
        # Cabeça da vassoura (cerdas)
        bristle_rad = math.radians(broom_angle + 45)
        for i in range(-3, 4):
            bristle_angle = bristle_rad + math.radians(i * 8)
            bx = cx + math.cos(bristle_angle) * 45
            by = cy + math.sin(bristle_angle) * 45
            # Movimento das cerdas
            wave = math.sin(angle * 0.1 + i * 0.5) * 3
            self.canvas.create_line(
                cx + math.cos(bristle_angle) * 15,
                cy + math.sin(bristle_angle) * 15,
                bx + wave, by + wave,
                fill='#DAA520', width=4, capstyle=tk.ROUND
            )
        
        # Base da cabeça
        self.canvas.create_oval(
            cx - 18, cy - 18, cx + 18, cy + 18,
            fill='#6366f1', outline='#818cf8', width=2
        )
        
        # Brilho na cabeça
        self.canvas.create_oval(
            cx - 8, cy - 12, cx + 2, cy - 6,
            fill='#a5b4fc', outline=''
        )
        
        # Estrelinhas decorativas
        for i in range(5):
            star_angle = (angle + i * 72) * math.pi / 180
            star_dist = 100 + i * 10
            sx = cx + math.cos(star_angle) * star_dist
            sy = cy + math.sin(star_angle) * star_dist
            star_size = 2 + math.sin(angle * 0.1 + i) * 1
            self.canvas.create_text(
                sx, sy,
                text="✨",
                font=('Segoe UI', int(8 + star_size)),
                fill='#fbbf24'
            )
        
    def _update_progress_bar(self):
        """Atualiza a barra de progresso."""
        self.progress_canvas.delete("all")
        
        # Fundo
        self.progress_canvas.create_rectangle(
            0, 0, 380, 8,
            fill='#2d2d44', outline=''
        )
        
        # Progresso com gradiente
        if self.progress > 0:
            width = int(380 * self.progress / 100)
            # Efeito de brilho
            self.progress_canvas.create_rectangle(
                0, 0, width, 8,
                fill='#6366f1', outline=''
            )
            # Brilho no topo
            self.progress_canvas.create_rectangle(
                0, 0, width, 3,
                fill='#818cf8', outline=''
            )
        
    def _animate(self):
        """Loop de animação."""
        self.angle += 3
        self._draw_broom(self.angle)
        
        # Simula progresso de carregamento
        if self.progress < 100:
            self.progress += 2
            
            # Atualiza texto de status
            if self.progress < 20:
                self.loading_text = "Iniciando sistema..."
            elif self.progress < 40:
                self.loading_text = "Carregando módulos..."
            elif self.progress < 60:
                self.loading_text = "Verificando permissões..."
            elif self.progress < 80:
                self.loading_text = "Preparando interface..."
            else:
                self.loading_text = "Quase pronto..."
            
            self.status_label.config(text=self.loading_text)
            self._update_progress_bar()
            
            self.root.after(50, self._animate)
        else:
            # Carregamento completo
            self.status_label.config(text="✅ Pronto!")
            self._update_progress_bar()
            self.root.after(500, self._finish)
    
    def _finish(self):
        """Finaliza a splash e abre a aplicação principal."""
        self.root.destroy()
        self.on_complete()
        
    def run(self):
        """Inicia a splash screen."""
        self.root.mainloop()


class LimpezaDavidApp:
    """
    Aplicação principal com interface gráfica Tkinter moderna.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Limpeza David - Limpador de Sistema")
        self.root.geometry("850x650")
        self.root.minsize(750, 550)
        
        # Cores do tema
        self.theme = {
            'bg': '#1a1a2e',
            'bg_secondary': '#16213e',
            'bg_card': '#1f2940',
            'primary': '#6366f1',
            'primary_hover': '#818cf8',
            'success': '#22c55e',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'text': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'border': '#334155'
        }
        
        # Configurar cor de fundo
        self.root.configure(bg=self.theme['bg'])
        
        # Configurar ícone se existir
        self._set_icon()
        
        # Inicializa o cleaner
        self.cleaner = SystemCleaner()
        self.logger = get_logger("LimpezaDavid")
        
        # Variáveis de controle
        self.scan_results = {}
        self.is_scanning = False
        self.is_cleaning = False
        self.scan_complete = False
        
        # Checkboxes para categorias
        self.category_vars = {}
        
        # Configura o estilo
        self._setup_style()
        
        # Constrói a interface
        self._build_ui()
        
        # Centraliza a janela
        CENTER_WINDOW(self.root)
        
        # Inicia análise automática após a interface carregar
        self.root.after(500, self._start_scan)
        
    def _set_icon(self):
        """Define o ícone da aplicação."""
        try:
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
        
        # Configurar estilos personalizados
        style.configure('Dark.TFrame', background=self.theme['bg'])
        style.configure('Card.TFrame', background=self.theme['bg_card'])
        
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'),
                       foreground=self.theme['primary'],
                       background=self.theme['bg'])
        
        style.configure('Header.TLabel',
                       font=('Segoe UI', 14, 'bold'),
                       foreground=self.theme['text'],
                       background=self.theme['bg'])
        
        style.configure('Info.TLabel',
                       font=('Segoe UI', 11),
                       foreground=self.theme['text_secondary'],
                       background=self.theme['bg'])
        
        style.configure('Success.TLabel',
                       font=('Segoe UI', 13, 'bold'),
                       foreground=self.theme['success'],
                       background=self.theme['bg'])
                       
        style.configure('Card.TLabel',
                       font=('Segoe UI', 11),
                       foreground=self.theme['text'],
                       background=self.theme['bg_card'])
                       
        style.configure('Dark.TCheckbutton',
                       font=('Segoe UI', 11),
                       foreground=self.theme['text'],
                       background=self.theme['bg_card'])
        
        # Estilo para LabelFrame
        style.configure('Card.TLabelframe',
                       background=self.theme['bg_card'],
                       foreground=self.theme['text'])
        style.configure('Card.TLabelframe.Label',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.theme['primary'],
                       background=self.theme['bg_card'])
                       
    def _build_ui(self):
        """Constrói a interface gráfica moderna."""
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.theme['bg'], padx=25, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === Cabeçalho ===
        header_frame = tk.Frame(main_frame, bg=self.theme['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Logo e título
        title_frame = tk.Frame(header_frame, bg=self.theme['bg'])
        title_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            title_frame, 
            text="🧹 Limpeza David",
            font=('Segoe UI', 26, 'bold'),
            fg=self.theme['primary'],
            bg=self.theme['bg']
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_frame,
            text="Libere espaço e otimize seu sistema",
            font=('Segoe UI', 11),
            fg=self.theme['text_secondary'],
            bg=self.theme['bg']
        )
        subtitle_label.pack(anchor='w')
        
        # Info do sistema
        system_frame = tk.Frame(header_frame, bg=self.theme['bg_card'], padx=15, pady=10)
        system_frame.pack(side=tk.RIGHT)
        
        system_info = f"💻 {platform.system()} {platform.release()}"
        system_label = tk.Label(
            system_frame,
            text=system_info,
            font=('Segoe UI', 10),
            fg=self.theme['text_secondary'],
            bg=self.theme['bg_card']
        )
        system_label.pack()
        
        # === Frame de Categorias ===
        categories_outer = tk.Frame(main_frame, bg=self.theme['bg_card'], padx=2, pady=2)
        categories_outer.pack(fill=tk.X, pady=(0, 20))
        
        categories_frame = tk.Frame(categories_outer, bg=self.theme['bg_card'], padx=20, pady=15)
        categories_frame.pack(fill=tk.X)
        
        cat_title = tk.Label(
            categories_frame,
            text="📂 Categorias de Limpeza",
            font=('Segoe UI', 13, 'bold'),
            fg=self.theme['primary'],
            bg=self.theme['bg_card']
        )
        cat_title.pack(anchor='w', pady=(0, 15))
        
        # Grid de checkboxes
        checkbox_frame = tk.Frame(categories_frame, bg=self.theme['bg_card'])
        checkbox_frame.pack(fill=tk.X)
        
        categories = self.cleaner.get_categories()
        
        for i, (cat_id, cat_info) in enumerate(categories.items()):
            var = tk.BooleanVar(value=True)
            self.category_vars[cat_id] = var
            
            cb = tk.Checkbutton(
                checkbox_frame,
                text=f"{cat_info['icon']} {cat_info['name']}",
                variable=var,
                font=('Segoe UI', 11),
                fg=self.theme['text'],
                bg=self.theme['bg_card'],
                selectcolor=self.theme['bg_secondary'],
                activebackground=self.theme['bg_card'],
                activeforeground=self.theme['text'],
                highlightthickness=0,
                bd=0
            )
            cb.grid(row=i // 3, column=i % 3, sticky=tk.W, padx=15, pady=8)
        
        # Botão re-analisar (discreto, no canto direito)
        rescan_frame = tk.Frame(categories_frame, bg=self.theme['bg_card'])
        rescan_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.rescan_btn = tk.Button(
            rescan_frame,
            text="🔄 Re-analisar",
            command=self._start_scan,
            font=('Segoe UI', 10),
            fg=self.theme['text_secondary'],
            bg=self.theme['bg_secondary'],
            activebackground=self.theme['primary'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.rescan_btn.pack(side=tk.RIGHT)
        
        # === Barra de Progresso e Status ===
        progress_frame = tk.Frame(main_frame, bg=self.theme['bg'])
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Canvas para barra de progresso personalizada
        self.progress_canvas = tk.Canvas(
            progress_frame,
            width=800,
            height=12,
            bg=self.theme['bg_secondary'],
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X)
        
        self.progress_var = 0
        
        # Status
        self.status_label = tk.Label(
            progress_frame,
            text="🔍 Analisando sistema automaticamente...",
            font=('Segoe UI', 11),
            fg=self.theme['text_secondary'],
            bg=self.theme['bg']
        )
        self.status_label.pack(pady=(10, 0))
        
        # === RODAPÉ COM BOTÃO (PRIMEIRO para garantir visibilidade) ===
        footer_frame = tk.Frame(main_frame, bg=self.theme['bg'], pady=15)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Resumo (lado esquerdo)
        left_footer = tk.Frame(footer_frame, bg=self.theme['bg'])
        left_footer.pack(side=tk.LEFT, fill=tk.Y)
        
        self.summary_label = tk.Label(
            left_footer,
            text="⏳ Analisando...",
            font=('Segoe UI', 14, 'bold'),
            fg=self.theme['success'],
            bg=self.theme['bg']
        )
        self.summary_label.pack(anchor='w')
        
        # Versão
        version_label = tk.Label(
            left_footer,
            text="v1.0.0",
            font=('Segoe UI', 9),
            fg=self.theme['text_secondary'],
            bg=self.theme['bg']
        )
        version_label.pack(anchor='w')
        
        # Botão de limpar (GRANDE e bem visível)
        self.clean_btn = tk.Button(
            footer_frame,
            text="🗑️ LIMPAR SISTEMA",
            command=self._start_clean,
            font=('Segoe UI', 16, 'bold'),
            fg='white',
            bg=self.theme['primary'],
            activebackground=self.theme['primary_hover'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=40,
            pady=15,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.clean_btn.pack(side=tk.RIGHT)
        
        # === Área de Status Simplificada (sem logs detalhados) ===
        status_outer = tk.Frame(main_frame, bg=self.theme['border'], padx=1, pady=1)
        status_outer.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        status_frame = tk.Frame(status_outer, bg=self.theme['bg_card'], padx=20, pady=20)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título da área de status
        status_title = tk.Label(
            status_frame,
            text="📊 Resumo da Análise",
            font=('Segoe UI', 13, 'bold'),
            fg=self.theme['primary'],
            bg=self.theme['bg_card']
        )
        status_title.pack(anchor='w', pady=(0, 15))
        
        # Frame para cards de categorias
        self.categories_result_frame = tk.Frame(status_frame, bg=self.theme['bg_card'])
        self.categories_result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inicializa com mensagem de espera
        self.waiting_label = tk.Label(
            self.categories_result_frame,
            text="🔍 Analisando seu sistema...\n\nAguarde enquanto verificamos os arquivos temporários.",
            font=('Segoe UI', 12),
            fg=self.theme['text_secondary'],
            bg=self.theme['bg_card'],
            justify=tk.CENTER
        )
        self.waiting_label.pack(expand=True, pady=50)
        
        # Log oculto (para manter compatibilidade, mas não visível)
        self.log_text = tk.Text(main_frame, height=1, width=1)
        self.log_text.pack_forget()  # Esconde completamente
        
    def _update_progress_bar(self, value):
        """Atualiza a barra de progresso personalizada."""
        self.progress_canvas.delete("all")
        
        # Obtém a largura atual do canvas
        self.progress_canvas.update_idletasks()
        width = self.progress_canvas.winfo_width()
        
        if width <= 1:
            width = 800
        
        # Fundo
        self.progress_canvas.create_rectangle(
            0, 0, width, 12,
            fill=self.theme['bg_secondary'], outline=''
        )
        
        # Progresso
        if value > 0:
            prog_width = int(width * value / 100)
            # Cor baseada no progresso
            color = self.theme['primary']
            self.progress_canvas.create_rectangle(
                0, 0, prog_width, 12,
                fill=color, outline=''
            )
            # Brilho
            self.progress_canvas.create_rectangle(
                0, 0, prog_width, 4,
                fill=self.theme['primary_hover'], outline=''
            )
        
    def _log(self, message, tag=None):
        """Adiciona mensagem ao log (apenas para debug interno)."""
        # Log silencioso - não mostra na interface
        self.logger.debug(message)
        
    def _update_status(self, message):
        """Atualiza o status."""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
        
    def _update_progress(self, value):
        """Atualiza a barra de progresso."""
        self.progress_var = value
        self._update_progress_bar(value)
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
        self.clean_btn.configure(state=tk.DISABLED)
        self.rescan_btn.configure(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._scan_thread, args=(selected,))
        thread.daemon = True
        thread.start()
        
    def _scan_thread(self, categories):
        """Thread de análise."""
        try:
            self._update_status("🔍 Analisando...")
            
            total_size = 0
            total_files = 0
            self.scan_results = {}
            
            for i, cat_id in enumerate(categories):
                progress = ((i + 1) / len(categories)) * 100
                self._update_progress(progress)
                
                cat_info = self.cleaner.get_categories()[cat_id]
                self._update_status(f"🔍 Analisando: {cat_info['name']}...")
                
                # Escaneia a categoria
                files, size = self.cleaner.scan_category(cat_id)
                
                self.scan_results[cat_id] = {
                    'files': files,
                    'size': size
                }
                
                total_size += size
                total_files += len(files)
            
            # Atualiza a interface com os resultados visuais
            self._update_results_display()
            
            self.summary_label.configure(
                text=f"💾 Espaço a liberar: {format_size(total_size)} ({total_files} arquivos)"
            )
            
            self._update_status("✅ Análise concluída!")
            self._update_progress(100)
            
            self.scan_complete = True
            
            if total_files > 0:
                self.clean_btn.configure(state=tk.NORMAL)
            else:
                self.summary_label.configure(text="✨ Sistema limpo!")
                
        except Exception as e:
            self.logger.error(f"Erro na análise: {e}")
        finally:
            self.is_scanning = False
            self.rescan_btn.configure(state=tk.NORMAL)
    
    def _update_results_display(self):
        """Atualiza a exibição visual dos resultados."""
        # Limpa o frame de resultados
        for widget in self.categories_result_frame.winfo_children():
            widget.destroy()
        
        if not self.scan_results:
            return
        
        # Cria cards para cada categoria com resultados
        categories = self.cleaner.get_categories()
        
        row = 0
        col = 0
        
        for cat_id, result in self.scan_results.items():
            if cat_id not in categories:
                continue
                
            cat_info = categories[cat_id]
            files_count = len(result['files'])
            size = result['size']
            
            # Card da categoria
            card = tk.Frame(
                self.categories_result_frame,
                bg=self.theme['bg_secondary'],
                padx=15,
                pady=12
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            
            # Ícone e nome
            header = tk.Label(
                card,
                text=f"{cat_info['icon']} {cat_info['name']}",
                font=('Segoe UI', 11, 'bold'),
                fg=self.theme['text'],
                bg=self.theme['bg_secondary']
            )
            header.pack(anchor='w')
            
            # Quantidade e tamanho
            if files_count > 0:
                info_text = f"{files_count} arquivos • {format_size(size)}"
                info_color = self.theme['warning'] if size > 100*1024*1024 else self.theme['text_secondary']
            else:
                info_text = "✓ Limpo"
                info_color = self.theme['success']
            
            info = tk.Label(
                card,
                text=info_text,
                font=('Segoe UI', 10),
                fg=info_color,
                bg=self.theme['bg_secondary']
            )
            info.pack(anchor='w', pady=(5, 0))
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Configura o grid para expandir
        for i in range(3):
            self.categories_result_frame.columnconfigure(i, weight=1)
            
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
        self.clean_btn.configure(state=tk.DISABLED)
        self.rescan_btn.configure(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._clean_thread)
        thread.daemon = True
        thread.start()
        
    def _clean_thread(self):
        """Thread de limpeza."""
        try:
            self._update_status("🧹 Limpando...")
            
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
                    
                self._update_status(f"🧹 Limpando: {cat_info['name']}...")
                
                # Remove os arquivos
                removed, size_freed, errors = self.cleaner.clean_files(files)
                
                total_removed += removed
                total_size_freed += size_freed
                total_errors += errors
            
            self.summary_label.configure(
                text=f"✅ Liberado: {format_size(total_size_freed)}"
            )
            
            self._update_status("✅ Limpeza concluída!")
            self._update_progress(100)
            
            # Limpa os resultados
            self.scan_results = {}
            self.scan_complete = False
            
            # Mensagem de sucesso
            error_msg = ""
            if total_errors > 0:
                error_msg = f"\n\n⚠️ {total_errors} arquivo(s) não puderam ser removidos\n(em uso ou protegidos)"
            
            messagebox.showinfo(
                "Limpeza Concluída",
                f"✅ Limpeza realizada com sucesso!\n\n"
                f"📁 Arquivos removidos: {total_removed}\n"
                f"💾 Espaço liberado: {format_size(total_size_freed)}{error_msg}"
            )
            
            # Reinicia análise automática após limpeza
            self.root.after(1000, self._start_scan)
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a limpeza:\n{str(e)}")
        finally:
            self.is_cleaning = False
            self.rescan_btn.configure(state=tk.NORMAL)
            
    def run(self):
        """Inicia a aplicação."""
        self.logger.info("Aplicação iniciada")
        self.root.mainloop()
        self.logger.info("Aplicação encerrada")


def main():
    """Ponto de entrada principal com splash screen."""
    def start_main_app():
        app = LimpezaDavidApp()
        app.run()
    
    # Mostra splash screen antes da aplicação principal
    splash = SplashScreen(start_main_app)
    splash.run()


if __name__ == "__main__":
    main()
