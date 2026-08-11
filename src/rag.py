from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from src import config

PROMPT_PATH = config.PROMPTS_DIR / "system_v1.md"


def carregar_prompt() -> str:
    """Lê o prompt a cada pergunta.

    Lido uma vez na importação, o Python guardaria em cache e toda edição
    do .md só valeria depois de reiniciar o Streamlit — o que faz parecer
    que a mudança no prompt não teve efeito.
    """
    return PROMPT_PATH.read_text(encoding="utf-8")

load_dotenv()

# Criar embeddings (mesmo modelo usado no vector_store)
embeddings = GoogleGenerativeAIEmbeddings(
    model=config.EMBEDDING_MODEL
)

# Carregar o vectorstore do ChromaDB
load_vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# Mecanismo de pesquisa (retriever)
retriever = load_vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 6}
)

# Modelo de chat
llm = ChatGoogleGenerativeAI(
    model=config.CHAT_MODEL
)

def responder_pergunta(pergunta: str) -> str:
    """Responde a uma pergunta usando o modelo de chat e o vectorstore."""
    # Recuperar documentos relevantes
    docs = retriever.invoke(pergunta)

    # Criar contexto a partir dos documentos recuperados, com a citação da fonte
    contexto = "\n\n---\n\n".join(
        f"[Fonte: {doc.metadata.get('title', 'desconhecida')} "
        f"— página {doc.metadata.get('page_label', '?')}]\n{doc.page_content}"
        for doc in docs
    )

    # Montar o prompt final a partir do template e gerar a resposta
    prompt = carregar_prompt().format(context=contexto, question=pergunta)
    resposta = llm.invoke(prompt)

    return resposta.content

