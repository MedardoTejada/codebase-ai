#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${GREEN}[setup]${NC} $1"; }
warn()    { echo -e "${YELLOW}[warn]${NC}  $1"; }
error()   { echo -e "${RED}[error]${NC} $1"; exit 1; }

# ---------------------------------------------------------------------------
# 1. Python 3.10+
# ---------------------------------------------------------------------------
info "Verificando Python..."

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VERSION=$("$cmd" -c 'import sys; print(sys.version_info[:2])')
        MAJOR=$("$cmd" -c 'import sys; print(sys.version_info[0])')
        MINOR=$("$cmd" -c 'import sys; print(sys.version_info[1])')
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

[ -z "$PYTHON" ] && error "Se requiere Python 3.10 o superior. Instálalo desde https://python.org"
info "Usando $($PYTHON --version)"

# ---------------------------------------------------------------------------
# 2. Virtualenv
# ---------------------------------------------------------------------------
if [ ! -d ".venv" ]; then
    info "Creando entorno virtual .venv ..."
    $PYTHON -m venv .venv
else
    info "Entorno virtual .venv ya existe, omitiendo creación."
fi

# Activar
# shellcheck disable=SC1091
source .venv/bin/activate

# ---------------------------------------------------------------------------
# 3. Dependencias
# ---------------------------------------------------------------------------
info "Instalando dependencias (esto puede tardar unos minutos la primera vez)..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
info "Dependencias instaladas."

# ---------------------------------------------------------------------------
# 4. Ollama
# ---------------------------------------------------------------------------
info "Verificando Ollama..."

if ! command -v ollama &>/dev/null; then
    warn "Ollama no está instalado."
    echo ""
    echo "  Instálalo con:"
    echo "    Mac:   brew install ollama"
    echo "    Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    echo "  Luego vuelve a ejecutar este script."
    exit 1
fi

info "Ollama encontrado: $(ollama --version 2>/dev/null || echo 'versión desconocida')"

# Leer modelo del .env si existe, si no usar el default
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2}"
if [ -f ".env" ]; then
    MODEL_FROM_ENV=$(grep -E '^OLLAMA_MODEL=' .env | cut -d= -f2 | tr -d ' ')
    [ -n "$MODEL_FROM_ENV" ] && OLLAMA_MODEL="$MODEL_FROM_ENV"
fi

info "Descargando modelo '$OLLAMA_MODEL' (puede tardar según tu conexión)..."
ollama pull "$OLLAMA_MODEL"

# ---------------------------------------------------------------------------
# 5. .env
# ---------------------------------------------------------------------------
if [ ! -f ".env" ]; then
    cp .env.example .env
    info "Archivo .env creado desde .env.example."
    warn "Si vas a indexar repos privados, agrega tu GITHUB_TOKEN en .env"
else
    info "Archivo .env ya existe, omitiendo."
fi

# ---------------------------------------------------------------------------
# Listo
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}Setup completado.${NC}"
echo ""
echo "  Para activar el entorno en tu terminal:"
echo "    source .venv/bin/activate"
echo ""
echo "  Comandos disponibles:"
echo "    python main.py index <github_url>   # indexar un repositorio"
echo "    python main.py ask \"<pregunta>\"      # hacer una pregunta"
echo "    python main.py list                  # ver repos indexados"
echo ""
