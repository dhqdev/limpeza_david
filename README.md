# 🧹 Limpeza David

<p align="center">
  <img src="assets/icon.png" alt="Limpeza David Logo" width="200"/>
</p>

<p align="center">
  <strong>Ferramenta open-source de limpeza de sistema para Windows e Linux</strong>
</p>

<p align="center">
  <a href="#-características">Características</a> •
  <a href="#-instalação-rápida">Instalação Rápida</a> •
  <a href="#-uso">Uso</a> •
  <a href="#-o-que-é-limpo">O que é limpo</a> •
  <a href="#-segurança">Segurança</a> •
  <a href="#-contribuição">Contribuição</a>
</p>

---

## 📖 Sobre

**Limpeza David** é uma ferramenta de limpeza de sistema inspirada no CCleaner, porém completamente **open-source**, **gratuita** e focada em **simplicidade** e **segurança**.

Com apenas um comando, você pode instalar e executar a ferramenta em qualquer máquina Windows ou Linux, mesmo sem ter Git ou Python instalados previamente.

## ✨ Características

- 🖥️ **Cross-platform**: Funciona no Windows 10+ e distribuições Linux baseadas em Debian/Ubuntu, Fedora, Arch, etc.
- 🎨 **Interface gráfica moderna**: GUI intuitiva com Tkinter
- 🔒 **Seguro**: Nunca apaga arquivos críticos do sistema
- 📊 **Transparente**: Mostra exatamente o que será apagado antes de executar
- 📝 **Logs detalhados**: Registro completo de todas as operações
- ⚡ **Instalação simples**: Um único comando para instalar tudo
- 🆓 **100% Gratuito e Open Source**

---

## 🚀 Instalação Rápida (Um Comando)

### 🪟 Windows

Abra o **PowerShell como Administrador** e execute:

```powershell
irm https://raw.githubusercontent.com/dhqdev/limpeza_david/main/installer/install_windows.ps1 | iex
```

### 🐧 Linux (Ubuntu/Debian)

Abra o **Terminal** e execute:

```bash
curl -fsSL https://raw.githubusercontent.com/dhqdev/limpeza_david/main/installer/install_linux.sh | bash
```

---

## 📦 Instalação Manual Completa

Se preferir instalar manualmente, siga os passos abaixo:

### 🐧 Linux (Ubuntu/Debian/Mint)

```bash
# 1. Atualizar sistema e instalar dependências
sudo apt update
sudo apt install -y git python3 python3-pip python3-tk

# 2. Clonar o repositório
git clone https://github.com/SEU_USUARIO/limpeza_david.git
cd limpeza_david

# 3. (Opcional) Instalar dependências extras
pip3 install -r requirements.txt

# 4. Executar o programa
python3 run.py
```

### 🐧 Linux (Fedora/RHEL)

```bash
# 1. Instalar dependências
sudo dnf install -y git python3 python3-pip python3-tkinter

# 2. Clonar o repositório
git clone https://github.com/SEU_USUARIO/limpeza_david.git
cd limpeza_david

# 3. Executar o programa
python3 run.py
```

### 🐧 Linux (Arch/Manjaro)

```bash
# 1. Instalar dependências
sudo pacman -S git python python-pip tk

# 2. Clonar o repositório
git clone https://github.com/SEU_USUARIO/limpeza_david.git
cd limpeza_david

# 3. Executar o programa
python run.py
```

### 🪟 Windows

```powershell
# 1. Instalar Python (se não tiver)
# Baixe em: https://www.python.org/downloads/
# Marque "Add Python to PATH" durante instalação

# 2. Instalar Git (se não tiver)
# Baixe em: https://git-scm.com/download/win

# 3. Clonar o repositório
git clone https://github.com/SEU_USUARIO/limpeza_david.git
cd limpeza_david

# 4. (Opcional) Instalar dependências extras
pip install -r requirements.txt

# 5. Executar o programa
python run.py
```

---

## 💻 Uso

### 🎨 Interface Gráfica (Recomendado)

1. Execute o programa:
   ```bash
   python3 run.py
   ```

2. Na interface:
   - ✅ Selecione as categorias que deseja limpar
   - 🔍 Clique em **"Analisar Sistema"** para ver o que será removido
   - 📊 Revise os arquivos encontrados no log
   - 🗑️ Clique em **"Limpar Selecionados"** para executar a limpeza
   - ✔️ Confirme a ação na janela de diálogo

### 📋 Comandos Rápidos

```bash
# Executar da pasta do projeto
cd limpeza_david
python3 run.py

# Ou diretamente
python3 /caminho/para/limpeza_david/run.py

# Após instalação automática (Linux)
limpeza-david
```

---

## 🧹 O que é Limpo

### 🪟 Windows

| Categoria | Local | Descrição |
|-----------|-------|-----------|
| 📁 Temp Usuário | `%TEMP%` | Arquivos temporários do usuário |
| 🪟 Temp Windows | `C:\Windows\Temp` | Arquivos temporários do sistema |
| ⚡ Prefetch | `C:\Windows\Prefetch` | Arquivos de pré-carregamento |
| 🌐 Cache Navegadores | AppData | Chrome, Firefox, Edge |
| 💾 Cache Windows | LocalAppData | Thumbnails e ícones |
| 📋 Arquivos Recentes | AppData | Lista de arquivos recentes |
| 📝 Logs | Diversos | Arquivos `.log` antigos |
| 📦 Backups | Diversos | `.old`, `.bak`, `.tmp` |

### 🐧 Linux

| Categoria | Local | Descrição |
|-----------|-------|-----------|
| 📁 /tmp | `/tmp` | Arquivos temporários (> 1 hora) |
| 📂 /var/tmp | `/var/tmp` | Temporários persistentes (> 7 dias) |
| 💾 Cache Usuário | `~/.cache` | Cache de aplicações |
| 🌐 Cache Navegadores | `~/.config/*` | Chrome, Firefox, Brave, Opera |
| 🖼️ Thumbnails | `~/.cache/thumbnails` | Miniaturas de imagens |
| 📝 Logs Antigos | `/var/log` | Logs com mais de 7 dias |
| 🗑️ Lixeira | `~/.local/share/Trash` | Arquivos na lixeira |
| 📦 Backups | `~/` | `.old`, `.bak`, `~` |
| 📦 Cache Pacotes | `/var/cache/apt` | Cache do apt/dnf/pacman |

---

## 🔒 Segurança

### ✅ O que a ferramenta FAZ:
- ✔️ Remove apenas arquivos temporários e cache
- ✔️ Solicita confirmação antes de apagar
- ✔️ Mostra exatamente o que será removido
- ✔️ Mantém logs de todas as operações
- ✔️ Verifica permissões antes de agir

### ❌ O que a ferramenta NUNCA faz:
- ❌ Apagar arquivos do sistema operacional
- ❌ Remover documentos, fotos ou downloads do usuário
- ❌ Acessar pastas protegidas sem permissão
- ❌ Modificar configurações do sistema
- ❌ Enviar dados para servidores externos

### 🛡️ Diretórios Protegidos

**Windows:**
- `C:\Windows\System32`, `C:\Windows\SysWOW64`
- `C:\Program Files`, `C:\Program Files (x86)`
- `Documentos`, `Downloads`, `Imagens`, `Área de Trabalho`

**Linux:**
- `/bin`, `/boot`, `/dev`, `/etc`, `/lib`, `/opt`, `/proc`, `/root`, `/sbin`, `/sys`, `/usr`
- `~/Documents`, `~/Downloads`, `~/Pictures`, `~/Desktop`
- `~/.ssh`, `~/.gnupg`, `~/.config`

---

## 📁 Estrutura do Projeto

```
limpeza_david/
├── app/
│   ├── __init__.py            # Módulo principal
│   ├── main.py                # 🎨 Interface gráfica (Tkinter)
│   ├── utils.py               # 🛠️ Funções utilitárias
│   └── cleaner/
│       ├── __init__.py
│       ├── windows.py         # 🪟 Limpeza para Windows
│       └── linux.py           # 🐧 Limpeza para Linux
├── installer/
│   ├── install_windows.ps1    # 💻 Instalador automático Windows
│   └── install_linux.sh       # 🐧 Instalador automático Linux
├── assets/
│   └── icon.png               # 🎨 Ícone do aplicativo
├── build/                     # 📦 Arquivos de build
├── .gitignore
├── LICENSE                    # 📜 Licença MIT
├── README.md                  # 📖 Esta documentação
├── requirements.txt           # 📋 Dependências Python
└── run.py                     # 🚀 Script de execução rápida
```

---

## 🛠️ Desenvolvimento

### Requisitos do Sistema

| Requisito | Windows | Linux |
|-----------|---------|-------|
| Python | 3.8+ | 3.8+ |
| Tkinter | Incluído | `python3-tk` |
| Git | Opcional | Opcional |

### Configurando Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/limpeza_david.git
cd limpeza_david

# (Opcional) Crie um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute em modo de desenvolvimento
python3 run.py
```

### 📦 Criando Executável Standalone

```bash
# Instale PyInstaller
pip install pyinstaller

# Windows (cria .exe)
pyinstaller --onefile --windowed --name "LimpezaDavid" --icon=assets/icon.ico run.py

# Linux (cria binário)
pyinstaller --onefile --name "limpeza-david" --icon=assets/icon.png run.py

# O executável estará em dist/
```

---

## 🤝 Contribuição

Contribuições são bem-vindas! 

### Como Contribuir

1. 🍴 **Fork** o repositório
2. 🌿 Crie uma **branch** para sua feature:
   ```bash
   git checkout -b feature/MinhaNovaFeature
   ```
3. 💾 **Commit** suas mudanças:
   ```bash
   git commit -m '✨ Adiciona MinhaNovaFeature'
   ```
4. 📤 **Push** para a branch:
   ```bash
   git push origin feature/MinhaNovaFeature
   ```
5. 🔄 Abra um **Pull Request**

### 📋 Diretrizes

- ✅ Siga o estilo de código existente
- ✅ Adicione comentários em português
- ✅ Teste em Windows E Linux antes de enviar
- ✅ Documente novas funcionalidades
- ✅ Use emojis nos commits para clareza

---

## 📝 Changelog

### v1.0.0 (2026-01-28)
- 🎉 Lançamento inicial
- ✅ Suporte completo a Windows 10/11
- ✅ Suporte a Linux (Ubuntu, Debian, Fedora, Arch)
- ✅ Interface gráfica com Tkinter
- ✅ Instaladores automáticos
- ✅ 8+ categorias de limpeza por sistema
- ✅ Sistema de logs detalhado
- ✅ Proteção contra exclusão de arquivos críticos

---

## ❓ Solução de Problemas

### Erro: "No module named 'tkinter'"

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3-tk
```

**Linux (Fedora):**
```bash
sudo dnf install python3-tkinter
```

**Linux (Arch):**
```bash
sudo pacman -S tk
```

### Erro: "Permission denied"

Execute com permissões apropriadas ou verifique se o arquivo/pasta não está em uso.

### A interface não abre

Verifique se você tem um ambiente gráfico (X11/Wayland) funcionando. Em servidores sem GUI, use a versão CLI (em desenvolvimento).

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👤 Autor

**David Fernandes**

- GitHub: [@SEU_USUARIO](https://github.com/SEU_USUARIO)

---

## 💖 Agradecimentos

- Inspirado no [CCleaner](https://www.ccleaner.com/)
- Comunidade Python
- Todos os contribuidores

---

<p align="center">
  <strong>Feito com ❤️ por David Fernandes</strong>
</p>

<p align="center">
  ⭐ Se este projeto te ajudou, deixe uma estrela no GitHub!
</p>

---

## 📊 Status do Projeto

| Funcionalidade | Status |
|----------------|--------|
| Limpeza de arquivos temporários | ✅ Completo |
| Limpeza de cache do sistema | ✅ Completo |
| Limpeza de cache de navegadores | ✅ Completo |
| Interface gráfica (GUI) | ✅ Completo |
| Suporte Windows 10/11 | ✅ Completo |
| Suporte Linux (Debian-based) | ✅ Completo |
| Suporte Linux (Fedora/Arch) | ✅ Completo |
| Instalador automático | ✅ Completo |
| Criação de atalho desktop | ✅ Completo |
| Sistema de logs | ✅ Completo |
| Proteção de arquivos críticos | ✅ Completo |
| Versão CLI | 🔄 Em desenvolvimento |
| Agendamento de limpeza | 📅 Planejado |
| Limpeza de registro (Windows) | 📅 Planejado |
