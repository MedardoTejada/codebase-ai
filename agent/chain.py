from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from agent.retriever import retrieve, format_context

_PROMPT_TEMPLATE = """You are an expert software engineer helping a developer understand a codebase.
Use ONLY the context below to answer the question. For every fact you state, cite the source
in the format [repo_name → file_path].

If the answer is not found in the context, say "I don't have enough information in the indexed repos."

Context:
{context}

Question: {question}

Answer (with source citations):"""

_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=_PROMPT_TEMPLATE,
)


def _get_llm() -> OllamaLLM:
    return OllamaLLM(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=0.1,
    )


def ask(question: str) -> str:
    """Run the full RAG chain and return the answer string."""
    docs = retrieve(question)
    if not docs:
        return "No indexed content found. Run `python main.py index <github_url>` first."

    context = format_context(docs)

    chain = (
        {
            "context": lambda _: context,
            "question": RunnablePassthrough(),
        }
        | _PROMPT
        | _get_llm()
        | StrOutputParser()
    )

    return chain.invoke(question)
