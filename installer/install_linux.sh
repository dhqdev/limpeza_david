#!/bin/bash
# ============================================================================
# LIMPEZA DAVID - Instalador Universal para Linux
# ============================================================================
# Autor: David Fernandes
# Versão: 2.0.0
# 
# Este script automatiza a instalação completa do Limpeza David:
# - Detecta o gerenciador de pacotes (apt, dnf, pacman, zypper)
# - Verifica e instala todas as dependências (Git, Python, pip, Tkinter)
# - Clona o repositório
# - Instala dependências Python
# - Cria atalho funcional na Área de Trabalho
#
# USO:
# curl -fsSL https://raw.githubusercontent.com/dhqdev/limpeza_david/main/installer/install_linux.sh | bash
# ============================================================================

set -e

# === CONFIGURAÇÕES ===
REPO_URL="https://github.com/dhqdev/limpeza_david.git"
APP_NAME="limpeza_david"
INSTALL_DIR="$HOME/.local/share/limpeza_david"
BIN_DIR="$HOME/.local/bin"
SCRIPT_PATH="$BIN_DIR/limpeza-david"

# Detectar Área de Trabalho (suporte a vários idiomas)
detect_desktop_dir() {
    # Tenta usar xdg-user-dir primeiro
    if command -v xdg-user-dir &> /dev/null; then
        DESKTOP_DIR=$(xdg-user-dir DESKTOP 2>/dev/null)
        if [[ -n "$DESKTOP_DIR" && -d "$DESKTOP_DIR" ]]; then
            echo "$DESKTOP_DIR"
            return
        fi
    fi
    
    # Lista de possíveis nomes para a área de trabalho
    local desktop_names=("Desktop" "Área de trabalho" "Área de Trabalho" "Escritorio" "Bureau")
    
    for name in "${desktop_names[@]}"; do
        if [[ -d "$HOME/$name" ]]; then
            echo "$HOME/$name"
            return
        fi
    done
    
    # Fallback: cria Desktop
    mkdir -p "$HOME/Desktop"
    echo "$HOME/Desktop"
}

DESKTOP_DIR=$(detect_desktop_dir)
DESKTOP_FILE="$DESKTOP_DIR/${APP_NAME}.desktop"

# === CORES ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# === FUNÇÕES AUXILIARES ===
print_banner() {
    echo ""
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                                                       ║${NC}"
    echo -e "${MAGENTA}║   🧹  LIMPEZA DAVID - Instalador Linux  🧹            ║${NC}"
    echo -e "${MAGENTA}║                                                       ║${NC}"
    echo -e "${MAGENTA}║   Versão 2.0.0 | Open Source                          ║${NC}"
    echo -e "${MAGENTA}║                                                       ║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "\n${BLUE}➤ $1${NC}"
}

# === DETECÇÃO DO GERENCIADOR DE PACOTES ===
detect_package_manager() {
    if command -v apt &> /dev/null; then
        PKG_MANAGER="apt"
        PKG_UPDATE="sudo apt update"
        PKG_INSTALL="sudo apt install -y"
        PYTHON_PKG="python3"
        PYTHON_PIP_PKG="python3-pip"
        PYTHON_VENV_PKG="python3-venv"
        TKINTER_PKG="python3-tk"
        GIT_PKG="git"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        PKG_UPDATE="sudo dnf check-update || true"
        PKG_INSTALL="sudo dnf install -y"
        PYTHON_PKG="python3"
        PYTHON_PIP_PKG="python3-pip"
        PYTHON_VENV_PKG="python3-virtualenv"
        TKINTER_PKG="python3-tkinter"
        GIT_PKG="git"
    elif command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
        PKG_UPDATE="sudo pacman -Sy"
        PKG_INSTALL="sudo pacman -S --noconfirm"
        PYTHON_PKG="python"
        PYTHON_PIP_PKG="python-pip"
        PYTHON_VENV_PKG="python-virtualenv"
        TKINTER_PKG="tk"
        GIT_PKG="git"
    elif command -v zypper &> /dev/null; then
        PKG_MANAGER="zypper"
        PKG_UPDATE="sudo zypper refresh"
        PKG_INSTALL="sudo zypper install -y"
        PYTHON_PKG="python3"
        PYTHON_PIP_PKG="python3-pip"
        PYTHON_VENV_PKG="python3-virtualenv"
        TKINTER_PKG="python3-tk"
        GIT_PKG="git"
    elif command -v apk &> /dev/null; then
        PKG_MANAGER="apk"
        PKG_UPDATE="sudo apk update"
        PKG_INSTALL="sudo apk add"
        PYTHON_PKG="python3"
        PYTHON_PIP_PKG="py3-pip"
        PYTHON_VENV_PKG="python3-dev"
        TKINTER_PKG="py3-tkinter"
        GIT_PKG="git"
    else
        log_error "Gerenciador de pacotes não suportado!"
        log_info "Suportados: apt (Debian/Ubuntu), dnf (Fedora), pacman (Arch), zypper (openSUSE), apk (Alpine)"
        exit 1
    fi
    
    log_info "Gerenciador de pacotes detectado: ${BOLD}$PKG_MANAGER${NC}"
}

# === VERIFICAÇÃO E INSTALAÇÃO DE DEPENDÊNCIAS ===
check_and_install_git() {
    log_step "Verificando Git..."
    
    if command -v git &> /dev/null; then
        log_success "Git já está instalado: $(git --version)"
    else
        log_warning "Git não encontrado. Instalando..."
        $PKG_UPDATE
        $PKG_INSTALL $GIT_PKG
        
        if command -v git &> /dev/null; then
            log_success "Git instalado com sucesso: $(git --version)"
        else
            log_error "Falha ao instalar Git"
            exit 1
        fi
    fi
}

check_and_install_python() {
    log_step "Verificando Python..."
    
    # Procura por python3 primeiro, depois python
    PYTHON_CMD=""
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        # Verifica se é Python 3
        if python --version 2>&1 | grep -q "Python 3"; then
            PYTHON_CMD="python"
        fi
    fi
    
    if [[ -n "$PYTHON_CMD" ]]; then
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
        log_success "Python já está instalado: $PYTHON_VERSION"
    else
        log_warning "Python 3 não encontrado. Instalando..."
        $PKG_UPDATE
        $PKG_INSTALL $PYTHON_PKG
        
        if command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
            log_success "Python instalado com sucesso: $(python3 --version)"
        else
            log_error "Falha ao instalar Python"
            exit 1
        fi
    fi
}

check_and_install_pip() {
    log_step "Verificando pip..."
    
    # Tenta diferentes formas de verificar o pip
    PIP_INSTALLED=false
    
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        PIP_INSTALLED=true
        PIP_VERSION=$($PYTHON_CMD -m pip --version 2>&1)
        log_success "pip já está instalado: $PIP_VERSION"
    elif command -v pip3 &> /dev/null; then
        PIP_INSTALLED=true
        log_success "pip3 já está instalado: $(pip3 --version)"
    elif command -v pip &> /dev/null; then
        PIP_INSTALLED=true
        log_success "pip já está instalado: $(pip --version)"
    fi
    
    if [[ "$PIP_INSTALLED" == "false" ]]; then
        log_warning "pip não encontrado. Instalando..."
        
        # Tenta instalar via pacote do sistema primeiro
        $PKG_INSTALL $PYTHON_PIP_PKG 2>/dev/null || true
        
        # Se ainda não funcionar, tenta ensurepip
        if ! $PYTHON_CMD -m pip --version &> /dev/null; then
            log_info "Tentando instalar pip via ensurepip..."
            $PYTHON_CMD -m ensurepip --upgrade 2>/dev/null || true
        fi
        
        # Se ainda não funcionar, tenta get-pip.py
        if ! $PYTHON_CMD -m pip --version &> /dev/null; then
            log_info "Tentando instalar pip via get-pip.py..."
            curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
            $PYTHON_CMD /tmp/get-pip.py --user
            rm -f /tmp/get-pip.py
            
            # Adiciona o diretório local ao PATH
            export PATH="$HOME/.local/bin:$PATH"
        fi
        
        # Verifica se funcionou
        if $PYTHON_CMD -m pip --version &> /dev/null; then
            log_success "pip instalado com sucesso: $($PYTHON_CMD -m pip --version)"
        else
            log_warning "pip não pôde ser instalado automaticamente"
            log_info "Você pode precisar instalar manualmente: $PKG_INSTALL $PYTHON_PIP_PKG"
        fi
    fi
}

check_and_install_tkinter() {
    log_step "Verificando Tkinter..."
    
    if $PYTHON_CMD -c "import tkinter" &> /dev/null; then
        log_success "Tkinter já está instalado"
    else
        log_warning "Tkinter não encontrado. Instalando..."
        $PKG_INSTALL $TKINTER_PKG
        
        if $PYTHON_CMD -c "import tkinter" &> /dev/null; then
            log_success "Tkinter instalado com sucesso"
        else
            log_error "Falha ao instalar Tkinter"
            log_info "Tente manualmente: $PKG_INSTALL $TKINTER_PKG"
            exit 1
        fi
    fi
}

# === CLONAGEM DO REPOSITÓRIO ===
clone_repository() {
    log_step "Preparando diretório de instalação..."
    
    # Remove instalação anterior se existir
    if [[ -d "$INSTALL_DIR" ]]; then
        log_info "Removendo instalação anterior..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Cria diretório pai
    mkdir -p "$(dirname "$INSTALL_DIR")"
    
    log_info "Baixando Limpeza David..."
    
    if git clone "$REPO_URL" "$INSTALL_DIR"; then
        log_success "Repositório clonado com sucesso"
    else
        log_error "Falha ao clonar repositório"
        exit 1
    fi
}

# === INSTALAÇÃO DE DEPENDÊNCIAS PYTHON ===
install_python_dependencies() {
    log_step "Instalando dependências Python..."
    
    cd "$INSTALL_DIR"
    
    # Verifica se requirements.txt existe
    if [[ -f "requirements.txt" ]]; then
        # Tenta instalar via pip
        if $PYTHON_CMD -m pip --version &> /dev/null; then
            $PYTHON_CMD -m pip install --user -r requirements.txt 2>/dev/null || true
        elif command -v pip3 &> /dev/null; then
            pip3 install --user -r requirements.txt 2>/dev/null || true
        fi
    fi
    
    log_success "Dependências instaladas"
}

# === CRIAÇÃO DO SCRIPT DE LANÇAMENTO ===
create_launcher_script() {
    log_step "Criando script de lançamento..."
    
    # Cria diretório bin se não existir
    mkdir -p "$BIN_DIR"
    
    # Cria o script de lançamento
    cat > "$SCRIPT_PATH" << EOF
#!/bin/bash
# Lançador do Limpeza David
cd "$INSTALL_DIR"
exec $PYTHON_CMD "$INSTALL_DIR/run.py" "\$@"
EOF
    
    chmod +x "$SCRIPT_PATH"
    
    log_success "Script de lançamento criado: $SCRIPT_PATH"
    
    # Adiciona ao PATH se necessário
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        log_info "Adicionando $BIN_DIR ao PATH..."
        
        # Detecta o shell e adiciona ao arquivo de configuração apropriado
        SHELL_RC=""
        if [[ -n "$BASH_VERSION" ]]; then
            SHELL_RC="$HOME/.bashrc"
        elif [[ -n "$ZSH_VERSION" ]]; then
            SHELL_RC="$HOME/.zshrc"
        fi
        
        if [[ -n "$SHELL_RC" && -f "$SHELL_RC" ]]; then
            if ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" "$SHELL_RC"; then
                echo "" >> "$SHELL_RC"
                echo "# Adicionado pelo instalador do Limpeza David" >> "$SHELL_RC"
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
                log_info "PATH atualizado em $SHELL_RC"
            fi
        fi
    fi
}

# === CRIAÇÃO DO ATALHO NA ÁREA DE TRABALHO ===
create_desktop_shortcut() {
    log_step "Criando atalho na Área de Trabalho..."
    
    # Define o caminho do ícone
    ICON_PATH="$INSTALL_DIR/assets/icon.png"
    
    # Usa um ícone padrão se o custom não existir
    if [[ ! -f "$ICON_PATH" ]]; then
        ICON_PATH="utilities-system-monitor"
    fi
    
    # Obtém o caminho absoluto do Python
    PYTHON_FULL_PATH=$(which $PYTHON_CMD)
    
    # Cria o arquivo .desktop com Path e Exec corretos
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Limpeza David
GenericName=Limpador de Sistema
Comment=Ferramenta de limpeza de sistema - Remove arquivos temporários, cache e lixo
Exec=bash -c 'cd "$INSTALL_DIR" && "$PYTHON_FULL_PATH" "$INSTALL_DIR/run.py"'
Path=$INSTALL_DIR
Icon=$ICON_PATH
Terminal=false
Categories=Utility;System;
Keywords=cleaner;cleanup;temp;cache;limpeza;
StartupNotify=true
StartupWMClass=limpeza_david
EOF
    
    # IMPORTANTE: Torna o arquivo .desktop executável
    chmod +x "$DESKTOP_FILE"
    
    # Marca como confiável no GNOME/KDE (necessário para executar)
    if command -v gio &> /dev/null; then
        gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
    fi
    
    # Para KDE Plasma
    if command -v kwriteconfig5 &> /dev/null; then
        kwriteconfig5 --file "$DESKTOP_FILE" --group "Desktop Entry" --key "X-KDE-SubstituteUID" "false" 2>/dev/null || true
    fi
    
    # Remove atributo de quarentena (se existir)
    if command -v xattr &> /dev/null; then
        xattr -d user.xdg.origin.url "$DESKTOP_FILE" 2>/dev/null || true
        xattr -d com.apple.quarantine "$DESKTOP_FILE" 2>/dev/null || true
    fi
    
    # Também copia para applications (menu do sistema)
    APPLICATIONS_DIR="$HOME/.local/share/applications"
    mkdir -p "$APPLICATIONS_DIR"
    cp "$DESKTOP_FILE" "$APPLICATIONS_DIR/${APP_NAME}.desktop"
    chmod +x "$APPLICATIONS_DIR/${APP_NAME}.desktop"
    
    # Marca como confiável também no menu
    if command -v gio &> /dev/null; then
        gio set "$APPLICATIONS_DIR/${APP_NAME}.desktop" metadata::trusted true 2>/dev/null || true
    fi
    
    # Atualiza o cache do desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
    fi
    
    log_success "Atalho criado em: $DESKTOP_FILE"
    log_success "Também disponível no menu de aplicativos"
    
    # Instruções para o usuário caso não funcione
    log_info "Se o atalho não abrir ao clicar:"
    log_info "  1. Clique com botão direito no ícone"
    log_info "  2. Selecione 'Permitir execução' ou 'Confiar neste aplicativo'"
}

# === VERIFICAÇÃO FINAL ===
verify_installation() {
    log_step "Verificando instalação..."
    
    ERRORS=0
    
    # Verifica se o diretório de instalação existe
    if [[ ! -d "$INSTALL_DIR" ]]; then
        log_error "Diretório de instalação não encontrado"
        ((ERRORS++))
    fi
    
    # Verifica se o arquivo principal existe
    if [[ ! -f "$INSTALL_DIR/run.py" ]]; then
        log_error "Arquivo principal (run.py) não encontrado"
        ((ERRORS++))
    fi
    
    # Verifica se o script de lançamento existe
    if [[ ! -f "$SCRIPT_PATH" ]]; then
        log_error "Script de lançamento não encontrado"
        ((ERRORS++))
    fi
    
    # Verifica se o atalho existe
    if [[ ! -f "$DESKTOP_FILE" ]]; then
        log_error "Atalho na área de trabalho não encontrado"
        ((ERRORS++))
    fi
    
    # Tenta executar uma verificação rápida do Python
    if ! $PYTHON_CMD -c "import tkinter" &> /dev/null; then
        log_error "Tkinter não está funcionando corretamente"
        ((ERRORS++))
    fi
    
    if [[ $ERRORS -eq 0 ]]; then
        log_success "Instalação verificada com sucesso!"
        return 0
    else
        log_error "Instalação com $ERRORS erro(s)"
        return 1
    fi
}

# === FUNÇÃO PRINCIPAL ===
main() {
    print_banner
    
    # Detecta o gerenciador de pacotes
    detect_package_manager
    
    log_info "🚀 Iniciando instalação do Limpeza David..."
    log_info "📂 Área de trabalho detectada: $DESKTOP_DIR"
    
    # Verifica e instala dependências
    check_and_install_git
    check_and_install_python
    check_and_install_pip
    check_and_install_tkinter
    
    # Clona o repositório
    clone_repository
    
    # Instala dependências Python
    install_python_dependencies
    
    # Cria script de lançamento
    create_launcher_script
    
    # Cria atalho na área de trabalho
    create_desktop_shortcut
    
    # Verifica instalação
    verify_installation
    
    # Mensagem final
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}║   🎉  INSTALAÇÃO CONCLUÍDA COM SUCESSO!  🎉           ║${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Para executar o Limpeza David:${NC}"
    echo -e "  ${BOLD}1.${NC} Clique no atalho '${BOLD}Limpeza David${NC}' na área de trabalho"
    echo -e "  ${BOLD}2.${NC} Ou execute no terminal: ${BOLD}limpeza-david${NC}"
    echo -e "  ${BOLD}3.${NC} Ou execute: ${BOLD}$PYTHON_CMD $INSTALL_DIR/run.py${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Se o atalho não funcionar na primeira vez:${NC}"
    echo -e "    Clique com botão direito > Permitir execução"
    echo -e "    Ou execute: ${BOLD}chmod +x \"$DESKTOP_FILE\"${NC}"
    echo ""
    
    # Pergunta se deseja executar agora
    read -p "Deseja executar o Limpeza David agora? (s/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        log_info "Iniciando Limpeza David..."
        cd "$INSTALL_DIR"
        $PYTHON_CMD "$INSTALL_DIR/run.py" &
        disown
    fi
}

# Executa o script principal
main "$@"
