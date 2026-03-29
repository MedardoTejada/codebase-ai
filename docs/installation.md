# Guía de instalación

## Requisitos

- Python 3.10 o superior
- macOS, Linux, o Windows (se recomienda WSL en Windows)
- ~2 GB de espacio en disco para el modelo LLM
- Conexión a internet en la primera ejecución (para descargar el modelo de embeddings y el LLM)

---

## Paso 1 — Cuentas y tokens

### HuggingFace (requerido)

El modelo de embeddings (`all-MiniLM-L6-v2`) se descarga desde HuggingFace en la primera ejecución. Se necesita una cuenta y un access token.

1. Crea una cuenta gratuita en [huggingface.co](https://huggingface.co/join)
2. Ve a **Settings → Access Tokens** ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))
3. Haz clic en **New token** → elige el rol **Read** → copia el token (empieza con `hf_`)
4. Agrégalo a tu archivo `.env`:
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
   ```

> Sin este token las descargas funcionan igual pero con límite de velocidad. Puedes ver el mensaje: `"You are sending unauthenticated requests to the HF Hub"` — no es un error, pero es mejor tener el token configurado.

### GitHub (opcional — solo para repos privados)

Si quieres indexar repositorios privados:

1. Ve a **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Crea un token con permiso **Contents: Read** para los repos que necesitas
3. Agrégalo a tu archivo `.env`:
   ```
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
   ```

Los repos públicos funcionan sin ningún token.

---

## Paso 2 — Instalar Ollama

Ollama ejecuta el LLM localmente en tu máquina.

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS (Homebrew):**
```bash
brew install ollama
```

**Windows:** Descarga el instalador desde [ollama.com](https://ollama.com/download)

Luego inicia el servidor de Ollama:
```bash
ollama serve
```

Descarga el modelo LLM por defecto (descarga única, ~2 GB):
```bash
ollama pull llama3.2
```

Verifica que funciona:
```bash
ollama list
```

Deberías ver `llama3.2` en la lista.

> Ollama debe estar corriendo (`ollama serve`) cada vez que uses codebase-ai. En macOS, la app de escritorio lo inicia automáticamente.

---

## Paso 3 — Clonar y configurar el proyecto

```bash
git clone https://github.com/MedardoTejada/codebase-ai.git
cd codebase-ai
```

Crea y activa un entorno virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

Instala las dependencias:
```bash
pip install -r requirements.txt
```

---

## Paso 4 — Configurar el entorno

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

Edita `.env` y completa tus tokens:
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx        # Requerido — token de HuggingFace
GITHUB_TOKEN=                           # Opcional — solo para repos privados
OLLAMA_BASE_URL=http://localhost:11434   # Por defecto, cambiar si Ollama corre en otro lugar
OLLAMA_MODEL=llama3.2                   # Modelo por defecto, puedes usar llama3.1, mistral, etc.
```

---

## Paso 5 — Primera ejecución

La primera vez que indexas un repo se descargan dos cosas automáticamente:

1. **Modelo de embeddings de HuggingFace** (`all-MiniLM-L6-v2`, ~90 MB) — descarga única, queda en caché en `~/.cache/huggingface/`
2. **ONNX runtime de ChromaDB** (~79 MB) — descarga única, queda en caché en `~/.cache/chroma/`

Esto solo ocurre en la primera ejecución. Las siguientes son rápidas.

```bash
python main.py index https://github.com/algún/repo
```

---

## Resumen de dependencias

| Paquete | Propósito |
|---|---|
| `langchain`, `langchain-core`, `langchain-text-splitters` | Orquestación del RAG chain y división de texto |
| `langchain-chroma` | Integración de ChromaDB con LangChain |
| `langchain-huggingface` | Integración de embeddings de HuggingFace |
| `langchain-ollama` | Integración del LLM de Ollama |
| `chromadb` | Base de datos vectorial local |
| `sentence-transformers` | Carga y ejecuta el modelo de embeddings localmente |
| `gitpython` | Clona repositorios de GitHub |
| `python-dotenv` | Carga la configuración desde `.env` |

---

## Solución de problemas

**`ModuleNotFoundError`** — Asegúrate de que el entorno virtual esté activado: `source .venv/bin/activate`

**`Connection refused` al hacer preguntas** — Ollama no está corriendo. Inícialo con `ollama serve`.

**`Permission denied (publickey)` al hacer git push** — Tu clave SSH no está agregada a GitHub. Ver [documentación SSH de GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

**Advertencia de rate limit de HuggingFace** — Agrega tu `HF_TOKEN` al `.env` como se describe en el Paso 1.

**Timeout al clonar repos grandes** — El timeout por defecto es 30 segundos. Para repos grandes, clona manualmente primero o aumenta `CLONE_TIMEOUT` en `config.py`.
