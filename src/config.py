"""
Configuração central do SCMedAI.

Tudo que é constante ou vem do ambiente mora aqui.
"""
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

GOLDEN_SET_CSV = Path("eval") / "golden_set.csv"
PROMPTS_DIR = Path("prompts")

# --------------------------------------------------------------------
# Credenciais e modelos
# --------------------------------------------------------------------

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

COLLECTION_NAME = "protocolos"



def validar_ambiente() -> None:
    """Falha cedo e com mensagem clara se faltar credencial.

    REGRA: mensagem de erro nunca imprime o valor de um segredo. Traceback
    vai parar em log, em print de tela, em issue do GitHub e em janela de
    chat. Diagnostique com presença, tamanho e prefixo — nunca com o valor.
    """
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY não encontrada.\n"
            "Configure a variável de ambiente ou crie um arquivo .env com:\n"
            "  GOOGLE_API_KEY=seu_segredo_aqui"
        )
