# Arquitectura

## Visión general

repo-guide es un agente RAG (Retrieval-Augmented Generation) que permite indexar cualquier repositorio de GitHub y hacer preguntas sobre él en lenguaje natural. El sistema clona el repositorio, divide el código en fragmentos, los convierte en vectores de embeddings, los almacena localmente, y usa un LLM para responder preguntas basadas en el contexto recuperado.

```
GitHub URL
    │
    ▼
┌─────────────┐
│   Cloner    │  GitPython — clona el repo a disco (data/repos/)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │  LangChain RecursiveCharacterTextSplitter
│             │  Lee archivos soportados → divide en chunks (1000 chars, 200 overlap)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Embedder   │  HuggingFace all-MiniLM-L6-v2 (corre localmente en CPU)
│             │  Convierte cada chunk en un vector de 384 dimensiones
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  ChromaDB   │  Vector store local persistente (data/chroma/)
│             │  Almacena vectores + metadata (repo, ruta de archivo, extensión)
└──────┬──────┘
       │
       ▼  (al momento de consultar)
┌─────────────┐
│  Retriever  │  Similarity search — retorna los 6 chunks más relevantes
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LLM Chain  │  LangChain + Ollama (llama3.2 por defecto, corre localmente)
│             │  El prompt incluye el contexto recuperado y las citas de fuente
└─────────────┘
```

---

## Componentes

### `indexer/cloner.py`
Clona un repositorio de GitHub usando GitPython. Soporta repos privados mediante `GITHUB_TOKEN` inyectado en la URL HTTPS. Tiene un timeout de 30 segundos usando señales UNIX. Si el repo ya estaba clonado, lo elimina y vuelve a clonar (reindexado completo).

### `indexer/parser.py`
Recorre el directorio clonado de forma recursiva. Omite directorios ocultos (`.git`, `.github`), `node_modules`, y tipos de archivo no soportados. Divide cada archivo con `RecursiveCharacterTextSplitter` (chunk size: 1000, overlap: 200). Cada chunk lleva metadata: `repo_url`, `repo_name`, `file_path`, `extension`.

### `indexer/embedder.py`
Carga `sentence-transformers/all-MiniLM-L6-v2` desde HuggingFace y lo ejecuta en CPU. El modelo queda en caché después de la primera carga. Los embeddings están normalizados (vectores unitarios), lo que mejora la calidad de la similitud coseno.

### `store/vector_store.py`
Envuelve ChromaDB mediante `langchain_chroma`. Los documentos se insertan en lotes de 5000 (límite máximo de ChromaDB: 5461). También mantiene una colección separada `repo_guide_meta` con metadata por repositorio (URL, timestamp de indexado, cantidad de archivos).

### `agent/retriever.py`
Ejecuta una búsqueda por similitud contra ChromaDB y formatea los 6 resultados más relevantes en un string de contexto numerado con citas `[repo_name → file_path]`.

### `agent/chain.py`
Construye una chain LCEL de LangChain: contexto + pregunta → PromptTemplate → OllamaLLM → StrOutputParser. El prompt instruye al LLM a responder solo desde el contexto provisto y siempre citar las fuentes.

---

## Herramientas y librerías

| Componente | Herramienta | Por qué |
|---|---|---|
| Orquestación | LangChain (LCEL) | Composición de chains, splitters, modelo de documentos |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` | Gratuito, corre localmente, rápido en CPU, buena calidad para código |
| Vector store | ChromaDB | Persistencia local, no requiere servidor, filtrado por metadata |
| LLM | Ollama (llama3.2) | Corre completamente local, sin costo de API, fácil de cambiar de modelo |
| Clonado de repos | GitPython | Python puro, soporta inyección de token para repos privados |
| Configuración | python-dotenv | Patrón simple de override con `.env` |

---

## Posibles mejoras

### LLM
El setup actual usa `llama3.2` via Ollama, que corre localmente en CPU/GPU. Funciona bien para experimentar pero tiene limitaciones:

- **Mejores modelos locales**: `llama3.1:8b`, `mistral`, `codellama` (especializado en código), `deepseek-coder` son alternativas más potentes para entender código.
- **LLMs en la nube**: Reemplazar Ollama con `langchain_openai` (GPT-4o) o `langchain_anthropic` (Claude) da un razonamiento significativamente mejor y context windows más grandes. Solo requiere cambiar `agent/chain.py` y agregar una API key.
- **Context window más grande**: Los LLMs actuales tienen context windows limitados. Cambiar a modelos con 128k+ tokens (GPT-4o, Claude 3.5) permitiría pasar más chunks recuperados.

### Embeddings
- `all-MiniLM-L6-v2` es rápido y liviano pero no fue entrenado específicamente en código.
- **Mejor alternativa**: `microsoft/codebert-base` o `nomic-ai/nomic-embed-text-v1.5` producen embeddings de mayor calidad para código fuente y mejorarían la relevancia del retrieval.
- **OpenAI embeddings**: `text-embedding-3-small` supera a los modelos locales en la mayoría de benchmarks a bajo costo.

### Retrieval
- Actualmente hace búsqueda plana por similitud (top-6 chunks). En repos grandes esto puede perder contexto relevante.
- **Mejoras posibles**: búsqueda híbrida (BM25 + vector), reranking con un modelo cross-encoder, o aumentar `k` y filtrar por tipo de archivo.
- **Búsqueda por repo específico**: Actualmente busca en todos los repos indexados. Agregar un flag `--repo` mejoraría la precisión.

### Indexado
- No hay indexado incremental: cada llamada a `index` hace un re-clonado y re-embedding completo.
- **Mejora posible**: rastrear hashes de archivos y solo re-embeddear los archivos modificados.
- El timeout de 30 segundos para el clonado es muy corto para repos grandes. Debería ser configurable o eliminarse para repos de gran tamaño.

### Interfaz
- Actualmente solo CLI. Una interfaz web simple (FastAPI + frontend minimalista) o un chat (Gradio, Streamlit) lo haría más accesible.
