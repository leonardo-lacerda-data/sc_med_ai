from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from src import config

# Caminho completo dos PDF

BASE_DIR = Path(__file__).parent.parent
pdf_paths = list((BASE_DIR / "data").glob("*.pdf"))


docs = []

for doc in pdf_paths:
    loader = PyPDFLoader(str(doc))
    paginas = loader.load()
    docs.extend(paginas)

    print(f"Documento '{doc.name}' carregado com sucesso!")

    print("\nMetadados:")
    for pagina in paginas:
        print(pagina.metadata)

    # Dividindo em pedaços menores
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size= 1000,
        chunk_overlap= 150
    )

    chunks = text_splitter.split_documents(docs)

    print(f"Chunks criados: {len(chunks)}")

    # Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)


# Guardar no ChromaDB
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
    )

print("Banco vetorial criado com sucesso!")