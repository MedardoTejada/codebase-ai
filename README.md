# codebase-ai

Agente RAG para onboarding de codebases. Clona e indexa cualquier repositorio de GitHub y permite hacer preguntas sobre él en lenguaje natural. Las respuestas citan el archivo fuente y el repositorio.

## Cómo funciona

1. Le das una URL de GitHub
2. Clona el repositorio, divide el código en chunks y genera embeddings vectoriales
3. Cuando haces una pregunta, encuentra los chunks más relevantes y los envía al LLM
4. El LLM responde basándose únicamente en el código real, citando siempre el archivo fuente

Todo corre localmente — no se requieren APIs en la nube.

## Inicio rápido

**Requisitos previos:** Python 3.10+, [Ollama](https://ollama.com) instalado y corriendo.

Instrucciones completas de configuración → [docs/installation.md](docs/installation.md)

```bash
# 1. Clonar e instalar
git clone https://github.com/MedardoTejada/codebase-ai.git
cd codebase-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configurar
cp .env.example .env
# Edita .env y agrega tu HF_TOKEN (ver docs/installation.md)

# 3. Descargar el LLM (una sola vez, ~2 GB)
ollama pull llama3.2

# 4. Indexar un repositorio
python main.py index https://github.com/owner/repo

# 5. Hacer preguntas
python main.py ask "¿qué hace este proyecto?"
python main.py ask "¿cómo se maneja la autenticación?"
python main.py ask "¿dónde se configuran las conexiones a la base de datos?"
```

## Comandos

```
python main.py index <github_url>    Clona e indexa un repositorio
python main.py ask "<pregunta>"      Hace una pregunta sobre los repos indexados
python main.py list                  Muestra todos los repositorios indexados
```

## Configuración

Todos los parámetros viven en `config.py` y pueden sobreescribirse desde `.env`:

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `HF_TOKEN` | *(vacío)* | Token de acceso de HuggingFace (evita límites de velocidad en descargas) |
| `GITHUB_TOKEN` | *(vacío)* | Personal Access Token de GitHub para repos privados |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Endpoint del servidor Ollama |
| `OLLAMA_MODEL` | `llama3.2` | Modelo LLM a usar para las respuestas |

## Tipos de archivo soportados

| Categoría | Extensiones |
|---|---|
| Código | `.py` `.java` `.js` `.ts` `.kt` `.feature` `.karate` |
| Documentación | `.md` `.txt` `.yaml` `.yml` `.json` |

## Stack tecnológico

| Componente | Herramienta |
|---|---|
| Orquestación | LangChain (LCEL) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (local, CPU) |
| Vector store | ChromaDB (local, persistente) |
| LLM | Ollama `llama3.2` (local) |
| Clonado de repos | GitPython |

## Estructura del proyecto

```
codebase-ai/
├── main.py              # Punto de entrada CLI (index / ask / list)
├── config.py            # Toda la configuración y valores por defecto
├── indexer/
│   ├── cloner.py        # Clonado con timeout + inyección de token
│   ├── parser.py        # Recorrido de archivos y chunking
│   └── embedder.py      # Embeddings de HuggingFace (con caché)
├── store/
│   └── vector_store.py  # Lectura/escritura en ChromaDB + metadata de repos
├── agent/
│   ├── retriever.py     # Similarity search + formateo del contexto
│   └── chain.py         # RAG chain con LangChain y Ollama
├── data/
│   ├── repos/           # Repos clonados (ignorados por git)
│   └── chroma/          # Base de datos vectorial persistente (ignorada por git)
├── docs/
│   ├── architecture.md  # Diseño del sistema y posibles mejoras
│   └── installation.md  # Configuración paso a paso incluyendo cuentas
├── .env.example
├── .gitignore
└── requirements.txt
```

## Documentación

- [Guía de instalación](docs/installation.md) — cuentas a crear, tokens, dependencias, solución de problemas
- [Arquitectura](docs/architecture.md) — diseño del sistema, descripción de componentes y posibles mejoras
