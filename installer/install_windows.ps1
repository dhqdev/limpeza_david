<#
.SYNOPSIS
    Script de instalação do Limpeza David para Windows
    
.DESCRIPTION
    Este script automatiza a instalação do Limpeza David:
    - Verifica e instala Git (se necessário)
    - Verifica e instala Python (se necessário)
    - Clona o repositório
    - Instala dependências
    - Cria atalho na Área de Trabalho
    
.NOTES
    Autor: David Fernandes
    Versão: 1.0.0
    
.EXAMPLE
    irm https://raw.githubusercontent.com/dhqdev/limpeza_david/main/installer/install_windows.ps1 | iex
#>

# Configurações
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Variáveis do projeto
$REPO_URL = "https://github.com/dhqdev/limpeza_david.git"
$APP_NAME = "Limpeza David"
$INSTALL_DIR = "$env:LOCALAPPDATA\limpeza_david"
$DESKTOP_PATH = [Environment]::GetFolderPath("Desktop")

# Cores para output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                                                       ║" -ForegroundColor Magenta
    Write-Host "║   🧹  LIMPEZA DAVID - Instalador Windows  🧹          ║" -ForegroundColor Magenta
    Write-Host "║                                                       ║" -ForegroundColor Magenta
    Write-Host "║   Versão 1.0.0 | Open Source                          ║" -ForegroundColor Magenta
    Write-Host "║                                                       ║" -ForegroundColor Magenta
    Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

function Test-AdminPrivileges {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Chocolatey {
    Write-ColorOutput "📦 Instalando Chocolatey..." "Yellow"
    
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-ColorOutput "✅ Chocolatey já está instalado" "Green"
        return $true
    }
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Atualiza o PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        
        Write-ColorOutput "✅ Chocolatey instalado com sucesso" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Erro ao instalar Chocolatey: $_" "Red"
        return $false
    }
}

function Install-Git {
    Write-ColorOutput "🔧 Verificando Git..." "Cyan"
    
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $gitVersion = git --version
        Write-ColorOutput "✅ Git já está instalado: $gitVersion" "Green"
        return $true
    }
    
    Write-ColorOutput "📥 Instalando Git..." "Yellow"
    
    try {
        # Tenta usar winget primeiro
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements
        }
        else {
            # Usa Chocolatey como fallback
            if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
                Install-Chocolatey
            }
            choco install git -y
        }
        
        # Atualiza o PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        $env:Path += ";C:\Program Files\Git\bin"
        
        Write-ColorOutput "✅ Git instalado com sucesso" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Erro ao instalar Git: $_" "Red"
        return $false
    }
}

function Install-Python {
    Write-ColorOutput "🐍 Verificando Python..." "Cyan"
    
    # Verifica se Python está instalado
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.") {
            Write-ColorOutput "✅ Python já está instalado: $pythonVersion" "Green"
            return $true
        }
    }
    
    # Verifica python3
    $python3Cmd = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3Cmd) {
        $pythonVersion = python3 --version 2>&1
        Write-ColorOutput "✅ Python já está instalado: $pythonVersion" "Green"
        return $true
    }
    
    Write-ColorOutput "📥 Instalando Python..." "Yellow"
    
    try {
        # Tenta usar winget primeiro
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install --id Python.Python.3.11 -e --source winget --accept-source-agreements --accept-package-agreements
        }
        else {
            # Usa Chocolatey como fallback
            if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
                Install-Chocolatey
            }
            choco install python3 -y
        }
        
        # Atualiza o PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        
        Write-ColorOutput "✅ Python instalado com sucesso" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Erro ao instalar Python: $_" "Red"
        return $false
    }
}

function Clone-Repository {
    Write-ColorOutput "📂 Preparando diretório de instalação..." "Cyan"
    
    # Remove instalação anterior se existir
    if (Test-Path $INSTALL_DIR) {
        Write-ColorOutput "🗑️ Removendo instalação anterior..." "Yellow"
        Remove-Item -Path $INSTALL_DIR -Recurse -Force
    }
    
    # Cria diretório pai
    $parentDir = Split-Path $INSTALL_DIR -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
    
    Write-ColorOutput "📥 Baixando Limpeza David..." "Yellow"
    
    try {
        git clone $REPO_URL $INSTALL_DIR
        Write-ColorOutput "✅ Repositório clonado com sucesso" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Erro ao clonar repositório: $_" "Red"
        return $false
    }
}

function Install-Dependencies {
    Write-ColorOutput "📦 Instalando dependências Python..." "Cyan"
    
    try {
        Set-Location $INSTALL_DIR
        
        # Upgrade pip
        python -m pip install --upgrade pip
        
        # Instala dependências
        if (Test-Path "$INSTALL_DIR\requirements.txt") {
            python -m pip install -r requirements.txt
        }
        
        Write-ColorOutput "✅ Dependências instaladas com sucesso" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Erro ao instalar dependências: $_" "Red"
        return $false
    }
}

function Convert-PngToIco {
    param(
        [string]$PngPath,
        [string]$IcoPath
    )
    
    try {
        # Usa Python com Pillow para converter PNG para ICO
        $pythonScript = @"
import sys
try:
    from PIL import Image
    img = Image.open(r'$PngPath')
    # Redimensiona para tamanhos de ícone padrão
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(r'$IcoPath', format='ICO', sizes=icon_sizes)
    print('OK')
except ImportError:
    # Se Pillow não está instalado, instala e tenta novamente
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow', '-q'])
    from PIL import Image
    img = Image.open(r'$PngPath')
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(r'$IcoPath', format='ICO', sizes=icon_sizes)
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
"@
        
        $result = python -c $pythonScript 2>&1
        return $result -eq 'OK'
    }
    catch {
        return $false
    }
}

function Create-Shortcut {
    Write-ColorOutput "🔗 Criando atalho na Área de Trabalho..." "Cyan"
    
    try {
        $shortcutPath = Join-Path $DESKTOP_PATH "$APP_NAME.lnk"
        $pythonPath = (Get-Command python).Source
        $scriptPath = "$INSTALL_DIR\app\main.py"
        $iconPathIco = "$INSTALL_DIR\assets\icon.ico"
        $iconPathPng = "$INSTALL_DIR\assets\icon.png"
        
        # Converte PNG para ICO se necessário
        if ((Test-Path $iconPathPng) -and (-not (Test-Path $iconPathIco))) {
            Write-ColorOutput "🎨 Convertendo ícone PNG para ICO..." "Yellow"
            $converted = Convert-PngToIco -PngPath $iconPathPng -IcoPath $iconPathIco
            if ($converted) {
                Write-ColorOutput "✅ Ícone convertido com sucesso" "Green"
            }
        }
        
        # Cria o atalho
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $pythonPath
        $shortcut.Arguments = "`"$scriptPath`""
        $shortcut.WorkingDirectory = $INSTALL_DIR
        $shortcut.Description = "Limpeza David - Limpador de Sistema"
        $shortcut.WindowStyle = 1
        
        # Define ícone (prioriza ICO, depois tenta ícone do sistema)
        if (Test-Path $iconPathIco) {
            $shortcut.IconLocation = $iconPathIco
        }
        else {
            # Usa um ícone padrão do sistema
            $shortcut.IconLocation = "%SystemRoot%\System32\cleanmgr.exe,0"
        }
        
        $shortcut.Save()
        
        Write-ColorOutput "✅ Atalho criado: $shortcutPath" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Erro ao criar atalho: $_" "Red"
        return $false
    }
}

function Create-BatchLauncher {
    Write-ColorOutput "📝 Criando launcher batch..." "Cyan"
    
    try {
        $batchContent = @"
@echo off
title Limpeza David
cd /d "$INSTALL_DIR"
python app\main.py
pause
"@
        
        $batchPath = "$INSTALL_DIR\limpeza_david.bat"
        Set-Content -Path $batchPath -Value $batchContent -Encoding UTF8
        
        Write-ColorOutput "✅ Launcher criado: $batchPath" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Erro ao criar launcher: $_" "Red"
        return $false
    }
}

function Build-Executable {
    Write-ColorOutput "🔨 Criando executável (opcional)..." "Cyan"
    
    try {
        # Verifica se PyInstaller está disponível
        $hasInstaller = python -c "import PyInstaller" 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "📦 Instalando PyInstaller..." "Yellow"
            python -m pip install pyinstaller
        }
        
        Set-Location $INSTALL_DIR
        
        # Cria o executável
        $iconArg = ""
        if (Test-Path "$INSTALL_DIR\assets\icon.ico") {
            $iconArg = "--icon=assets\icon.ico"
        }
        
        python -m PyInstaller --noconfirm --onefile --windowed `
            --name "LimpezaDavid" `
            --add-data "assets;assets" `
            $iconArg `
            app\main.py
        
        # Move o executável para o diretório raiz
        if (Test-Path "$INSTALL_DIR\dist\LimpezaDavid.exe") {
            Move-Item "$INSTALL_DIR\dist\LimpezaDavid.exe" "$INSTALL_DIR\LimpezaDavid.exe" -Force
            
            # Atualiza o atalho para usar o executável
            $shortcutPath = Join-Path $DESKTOP_PATH "$APP_NAME.lnk"
            $shell = New-Object -ComObject WScript.Shell
            $shortcut = $shell.CreateShortcut($shortcutPath)
            $shortcut.TargetPath = "$INSTALL_DIR\LimpezaDavid.exe"
            $shortcut.Arguments = ""
            $shortcut.Save()
            
            Write-ColorOutput "✅ Executável criado: $INSTALL_DIR\LimpezaDavid.exe" "Green"
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "⚠️ Não foi possível criar executável (o script ainda funcionará)" "Yellow"
        return $false
    }
}

# === MAIN ===
function Main {
    Clear-Host
    Write-Banner
    
    # Verifica privilégios
    if (-not (Test-AdminPrivileges)) {
        Write-ColorOutput "⚠️  Este script funciona melhor com privilégios de Administrador" "Yellow"
        Write-ColorOutput "   Algumas funcionalidades podem não estar disponíveis" "Yellow"
        Write-Host ""
    }
    
    Write-ColorOutput "🚀 Iniciando instalação do Limpeza David..." "Cyan"
    Write-Host ""
    
    # Etapa 1: Instalar Git
    if (-not (Install-Git)) {
        Write-ColorOutput "❌ Falha ao instalar Git. Abortando." "Red"
        exit 1
    }
    Write-Host ""
    
    # Etapa 2: Instalar Python
    if (-not (Install-Python)) {
        Write-ColorOutput "❌ Falha ao instalar Python. Abortando." "Red"
        exit 1
    }
    Write-Host ""
    
    # Etapa 3: Clonar repositório
    if (-not (Clone-Repository)) {
        Write-ColorOutput "❌ Falha ao baixar o projeto. Abortando." "Red"
        exit 1
    }
    Write-Host ""
    
    # Etapa 4: Instalar dependências
    if (-not (Install-Dependencies)) {
        Write-ColorOutput "❌ Falha ao instalar dependências. Abortando." "Red"
        exit 1
    }
    Write-Host ""
    
    # Etapa 5: Criar launcher batch
    Create-BatchLauncher | Out-Null
    Write-Host ""
    
    # Etapa 6: Criar atalho
    if (-not (Create-Shortcut)) {
        Write-ColorOutput "⚠️ Não foi possível criar atalho na Área de Trabalho" "Yellow"
    }
    Write-Host ""
    
    # Etapa 7 (Opcional): Criar executável
    Write-ColorOutput "❓ Deseja criar um executável (.exe)? (pode demorar alguns minutos)" "Yellow"
    $createExe = Read-Host "   Digite 's' para sim ou 'n' para não"
    
    if ($createExe -eq 's' -or $createExe -eq 'S') {
        Build-Executable | Out-Null
    }
    
    # Conclusão
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-ColorOutput "✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!" "Green"
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-ColorOutput "📂 Instalado em: $INSTALL_DIR" "Cyan"
    Write-ColorOutput "🖥️  Atalho criado na Área de Trabalho" "Cyan"
    Write-Host ""
    Write-ColorOutput "🚀 Para iniciar o Limpeza David:" "Yellow"
    Write-ColorOutput "   - Clique duas vezes no atalho 'Limpeza David' na Área de Trabalho" "White"
    Write-ColorOutput "   - Ou execute: python $INSTALL_DIR\app\main.py" "White"
    Write-Host ""
    
    # Pergunta se quer iniciar agora
    Write-ColorOutput "❓ Deseja iniciar o Limpeza David agora? (s/n)" "Yellow"
    $startNow = Read-Host "   "
    
    if ($startNow -eq 's' -or $startNow -eq 'S') {
        Write-ColorOutput "🚀 Iniciando Limpeza David..." "Green"
        Start-Process python -ArgumentList "$INSTALL_DIR\app\main.py" -WorkingDirectory $INSTALL_DIR
    }
}

# Executa
Main
