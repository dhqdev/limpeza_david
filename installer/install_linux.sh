#!/bin/bash
#
# Script de instalação do Limpeza David para Linux
#
# Este script automatiza a instalação do Limpeza David:
# - Verifica e instala Git (se necessário)
# - Verifica e instala Python (se necessário)
# - Clona o repositório
# - Instala dependências
# - Cria atalho na Área de Trabalho
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/SEU_USUARIO/limpeza_david/main/installer/install_linux.sh | bash
#
# Autor: David Fernandes
# Versão: 1.0.0

set -e

# === CONFIGURAÇÕES ===
REPO_URL="https://github.com/SEU_USUARIO/limpeza_david.git"
APP_NAME="Limpeza David"
INSTALL_DIR="$HOME/.local/share/limpeza_david"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/Desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# === FUNÇÕES UTILITÁRIAS ===

print_banner() {
    echo ""
    echo -e "${PURPLE}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║                                                       ║"
    echo "║   🧹  LIMPEZA DAVID - Instalador Linux  🧹            ║"
    echo "║                                                       ║"
    echo "║   Versão 1.0.0 | Open Source                          ║"
    echo "║                                                       ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_step() {
    echo -e "${BLUE}${BOLD}➤ $1${NC}"
}

# Detecta o gerenciador de pacotes
detect_package_manager() {
    if command -v apt &> /dev/null; then
        PKG_MANAGER="apt"
        PKG_INSTALL="sudo apt install -y"
        PKG_UPDATE="sudo apt update"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        PKG_INSTALL="sudo dnf install -y"
        PKG_UPDATE="sudo dnf check-update || true"
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
        PKG_INSTALL="sudo yum install -y"
        PKG_UPDATE="sudo yum check-update || true"
    elif command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
        PKG_INSTALL="sudo pacman -S --noconfirm"
        PKG_UPDATE="sudo pacman -Sy"
    elif command -v zypper &> /dev/null; then
        PKG_MANAGER="zypper"
        PKG_INSTALL="sudo zypper install -y"
        PKG_UPDATE="sudo zypper refresh"
    else
        print_error "Gerenciador de pacotes não suportado!"
        exit 1
    fi
    
    print_info "Gerenciador de pacotes detectado: $PKG_MANAGER"
}

# Instala Git
install_git() {
    print_step "Verificando Git..."
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git já está instalado: $GIT_VERSION"
        return 0
    fi
    
    print_info "Instalando Git..."
    
    case $PKG_MANAGER in
        apt)
            $PKG_UPDATE
            $PKG_INSTALL git
            ;;
        dnf|yum)
            $PKG_INSTALL git
            ;;
        pacman)
            $PKG_INSTALL git
            ;;
        zypper)
            $PKG_INSTALL git
            ;;
    esac
    
    if command -v git &> /dev/null; then
        print_success "Git instalado com sucesso"
        return 0
    else
        print_error "Falha ao instalar Git"
        return 1
    fi
}

# Instala Python
install_python() {
    print_step "Verificando Python..."
    
    # Verifica python3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python já está instalado: $PYTHON_VERSION"
        PYTHON_CMD="python3"
        return 0
    fi
    
    # Verifica python
    if command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
            print_success "Python já está instalado: $PYTHON_VERSION"
            PYTHON_CMD="python"
            return 0
        fi
    fi
    
    print_info "Instalando Python 3..."
    
    case $PKG_MANAGER in
        apt)
            $PKG_UPDATE
            $PKG_INSTALL python3 python3-pip python3-venv python3-tk
            ;;
        dnf|yum)
            $PKG_INSTALL python3 python3-pip python3-tkinter
            ;;
        pacman)
            $PKG_INSTALL python python-pip tk
            ;;
        zypper)
            $PKG_INSTALL python3 python3-pip python3-tk
            ;;
    esac
    
    if command -v python3 &> /dev/null; then
        print_success "Python instalado com sucesso"
        PYTHON_CMD="python3"
        return 0
    else
        print_error "Falha ao instalar Python"
        return 1
    fi
}

# Instala dependências do sistema para Tkinter
install_tkinter() {
    print_step "Verificando Tkinter..."
    
    # Testa se tkinter está disponível
    if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
        print_success "Tkinter já está instalado"
        return 0
    fi
    
    print_info "Instalando Tkinter..."
    
    case $PKG_MANAGER in
        apt)
            $PKG_INSTALL python3-tk
            ;;
        dnf|yum)
            $PKG_INSTALL python3-tkinter
            ;;
        pacman)
            $PKG_INSTALL tk
            ;;
        zypper)
            $PKG_INSTALL python3-tk
            ;;
    esac
    
    if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
        print_success "Tkinter instalado com sucesso"
        return 0
    else
        print_warning "Tkinter pode não estar disponível - a GUI pode não funcionar"
        return 0
    fi
}

# Clona o repositório
clone_repository() {
    print_step "Preparando diretório de instalação..."
    
    # Remove instalação anterior se existir
    if [ -d "$INSTALL_DIR" ]; then
        print_info "Removendo instalação anterior..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Cria diretório pai
    mkdir -p "$(dirname "$INSTALL_DIR")"
    
    print_info "Baixando Limpeza David..."
    
    if git clone "$REPO_URL" "$INSTALL_DIR"; then
        print_success "Repositório clonado com sucesso"
        return 0
    else
        print_error "Falha ao clonar repositório"
        return 1
    fi
}

# Instala dependências Python
install_dependencies() {
    print_step "Instalando dependências Python..."
    
    cd "$INSTALL_DIR"
    
    # Atualiza pip
    $PYTHON_CMD -m pip install --user --upgrade pip
    
    # Instala dependências
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install --user -r requirements.txt
    fi
    
    print_success "Dependências instaladas"
    return 0
}

# Cria script de lançamento
create_launcher() {
    print_step "Criando script de lançamento..."
    
    # Cria diretório bin se não existir
    mkdir -p "$BIN_DIR"
    
    # Cria o script
    cat > "$BIN_DIR/limpeza-david" << EOF
#!/bin/bash
# Lançador do Limpeza David
cd "$INSTALL_DIR"
$PYTHON_CMD app/main.py "\$@"
EOF
    
    chmod +x "$BIN_DIR/limpeza-david"
    
    # Adiciona ao PATH se necessário
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo "" >> "$HOME/.bashrc"
        echo "# Limpeza David" >> "$HOME/.bashrc"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        
        # Também para zsh se existir
        if [ -f "$HOME/.zshrc" ]; then
            echo "" >> "$HOME/.zshrc"
            echo "# Limpeza David" >> "$HOME/.zshrc"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        fi
    fi
    
    print_success "Script de lançamento criado: $BIN_DIR/limpeza-david"
    return 0
}

# Cria atalho .desktop
create_desktop_entry() {
    print_step "Criando atalho na Área de Trabalho..."
    
    # Encontra o caminho do ícone
    ICON_PATH="$INSTALL_DIR/assets/icon.png"
    if [ ! -f "$ICON_PATH" ]; then
        ICON_PATH="utilities-system-monitor"  # Ícone padrão do sistema
    fi
    
    # Cria diretório de aplicações
    mkdir -p "$APPLICATIONS_DIR"
    
    # Cria arquivo .desktop para o menu de aplicações
    cat > "$APPLICATIONS_DIR/limpeza_david.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=limpeza_david
GenericName=Limpador de Sistema
Comment=Ferramenta de limpeza de sistema - Remove arquivos temporários, cache e lixo
Exec=$PYTHON_CMD $INSTALL_DIR/app/main.py
Icon=$ICON_PATH
Terminal=false
Categories=Utility;System;
Keywords=cleaner;cleanup;temp;cache;limpeza;
StartupNotify=true
StartupWMClass=limpeza_david
EOF
    
    chmod +x "$APPLICATIONS_DIR/limpeza_david.desktop"
    
    # Cria também na Área de Trabalho
    # Tenta encontrar a pasta Desktop (pode variar por idioma)
    DESKTOP_PATHS=(
        "$HOME/Desktop"
        "$HOME/Área de trabalho"
        "$HOME/Área de Trabalho"
        "$HOME/Escritorio"
        "$HOME/Bureau"
    )
    
    for DESKTOP_PATH in "${DESKTOP_PATHS[@]}"; do
        if [ -d "$DESKTOP_PATH" ]; then
            cp "$APPLICATIONS_DIR/limpeza_david.desktop" "$DESKTOP_PATH/limpeza_david.desktop"
            chmod +x "$DESKTOP_PATH/limpeza_david.desktop"
            
            # Marca como confiável (para GNOME) - permite executar sem perguntar
            if command -v gio &> /dev/null; then
                gio set "$DESKTOP_PATH/limpeza_david.desktop" metadata::trusted true 2>/dev/null || true
            fi
            
            # Para KDE/outros DEs
            chmod a+x "$DESKTOP_PATH/limpeza_david.desktop"
            
            print_success "Atalho criado em: $DESKTOP_PATH/limpeza_david.desktop"
            break
        fi
    done
    
    # Atualiza o cache de aplicações
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
    fi
    
    return 0
}

# Constrói executável (opcional)
build_executable() {
    print_step "Construindo executável (opcional)..."
    
    # Verifica se PyInstaller está disponível
    if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
        print_info "Instalando PyInstaller..."
        $PYTHON_CMD -m pip install --user pyinstaller
    fi
    
    cd "$INSTALL_DIR"
    
    # Constrói o executável
    ICON_ARG=""
    if [ -f "$INSTALL_DIR/assets/icon.png" ]; then
        ICON_ARG="--icon=assets/icon.png"
    fi
    
    $PYTHON_CMD -m PyInstaller --noconfirm --onefile \
        --name "limpeza-david" \
        --add-data "assets:assets" \
        $ICON_ARG \
        app/main.py
    
    if [ -f "$INSTALL_DIR/dist/limpeza-david" ]; then
        mv "$INSTALL_DIR/dist/limpeza-david" "$BIN_DIR/"
        chmod +x "$BIN_DIR/limpeza-david"
        print_success "Executável criado: $BIN_DIR/limpeza-david"
        return 0
    else
        print_warning "Não foi possível criar o executável"
        return 1
    fi
}

# === MAIN ===

main() {
    clear
    print_banner
    
    # Detecta gerenciador de pacotes
    detect_package_manager
    echo ""
    
    # Define comando Python padrão
    PYTHON_CMD="python3"
    
    print_info "🚀 Iniciando instalação do Limpeza David..."
    echo ""
    
    # Etapa 1: Instalar Git
    if ! install_git; then
        print_error "Falha ao instalar Git. Abortando."
        exit 1
    fi
    echo ""
    
    # Etapa 2: Instalar Python
    if ! install_python; then
        print_error "Falha ao instalar Python. Abortando."
        exit 1
    fi
    echo ""
    
    # Etapa 3: Instalar Tkinter
    install_tkinter
    echo ""
    
    # Etapa 4: Clonar repositório
    if ! clone_repository; then
        print_error "Falha ao baixar o projeto. Abortando."
        exit 1
    fi
    echo ""
    
    # Etapa 5: Instalar dependências
    if ! install_dependencies; then
        print_error "Falha ao instalar dependências. Abortando."
        exit 1
    fi
    echo ""
    
    # Etapa 6: Criar launcher
    create_launcher
    echo ""
    
    # Etapa 7: Criar atalho
    create_desktop_entry
    echo ""
    
    # Etapa 8 (Opcional): Criar executável
    echo -e "${YELLOW}❓ Deseja criar um executável? (pode demorar alguns minutos)${NC}"
    read -p "   Digite 's' para sim ou 'n' para não: " CREATE_EXE
    
    if [[ "$CREATE_EXE" == "s" || "$CREATE_EXE" == "S" ]]; then
        build_executable || true
    fi
    
    # Conclusão
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    print_success "INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    print_info "📂 Instalado em: $INSTALL_DIR"
    print_info "🖥️  Atalho criado na Área de Trabalho e menu de aplicações"
    echo ""
    echo -e "${YELLOW}🚀 Para iniciar o Limpeza David:${NC}"
    echo "   - Clique no atalho na Área de Trabalho"
    echo "   - Ou execute: limpeza-david"
    echo "   - Ou execute: $PYTHON_CMD $INSTALL_DIR/app/main.py"
    echo ""
    
    # Pergunta se quer iniciar agora
    echo -e "${YELLOW}❓ Deseja iniciar o Limpeza David agora? (s/n)${NC}"
    read -p "   " START_NOW
    
    if [[ "$START_NOW" == "s" || "$START_NOW" == "S" ]]; then
        print_success "🚀 Iniciando Limpeza David..."
        cd "$INSTALL_DIR"
        $PYTHON_CMD app/main.py &
    fi
}

# Executa
main
