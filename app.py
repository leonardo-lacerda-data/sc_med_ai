"""
Interface web do SCMedAI — chat de consulta a protocolos clínicos.

    streamlit run app.py
"""
import base64
from pathlib import Path

import streamlit as st

from src import config
from src.rag import responder_pergunta

BASE_DIR = Path(__file__).resolve().parent
ESCUDO = BASE_DIR / "escudo_header.png"

# --------------------------------------------------------------------
# Paleta. As duas faixas escuras (lateral e rodapé) emolduram a área de
# leitura clara. Ajuste aqui se quiser voltar à lateral clara.
# --------------------------------------------------------------------
NAVY = "#2B4A6F"          # marinho da logo
NAVY_FUNDO = "#1D3550"    # faixas escuras
NAVY_BORDA = "#2F4C6D"
VERDE = "#4F9B7A"         # verde da logo
VERDE_ESCURO = "#3F8465"
VERDE_CLARO = "#7DC4A0"   # acento sobre fundo escuro

FUNDO = "#F7FCF9"         # área de conversa
BALAO = "#FFFFFF"         # balões
MENTA_CARD = "#EDF6F1"    # cartão de boas-vindas
BORDA = "#D5E4DB"
TEXTO_CLARO = "#C9D9E8"   # texto sobre marinho

LARGURA_SIDEBAR = "310px"
LARGURA_CONTEUDO = "1080px"


def data_uri(caminho: Path) -> str:
    """Embute a imagem no HTML. st.markdown não carrega arquivo local."""
    return "data:image/png;base64," + base64.b64encode(
        caminho.read_bytes()
    ).decode()


st.set_page_config(
    page_title="SCMedAI",
    page_icon=str(ESCUDO) if ESCUDO.exists() else "🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
  /* ============ ÁREA DE CONVERSA ============ */
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"],
  section.main {{
      background-color: {FUNDO};
  }}
  [data-testid="stHeader"] {{ background: transparent; }}

  .block-container {{
      max-width: {LARGURA_CONTEUDO} !important;
      padding: 7rem 3rem 1rem !important;
  }}

  /* ============ CABEÇALHO FIXO — alinhado à esquerda ============ */
  .cabecalho {{
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 100;
      background: {FUNDO};
      border-bottom: 1px solid {BORDA};
      padding: .85rem 0 .8rem;
  }}
  [data-testid="stAppViewContainer"]:has(
      [data-testid="stSidebar"][aria-expanded="true"]
  ) .cabecalho {{
      left: {LARGURA_SIDEBAR};
  }}
  /* Mesma largura e recuo do bloco de conteúdo, para o escudo ficar na
     mesma linha vertical das mensagens abaixo. */
  .cabecalho .interno {{
      max-width: {LARGURA_CONTEUDO};
      margin: 0 auto;
      padding: 0 3rem;
      display: flex; align-items: center; gap: .8rem;
  }}
  .cabecalho img {{ height: 46px; width: auto; display: block; }}
  .wordmark {{
      font-size: 1.7rem; font-weight: 800; letter-spacing: -.02em;
      line-height: 1.05;
  }}
  .wordmark .sc, .wordmark .ai {{ color: {NAVY}; }}
  .wordmark .med {{ color: {VERDE}; }}
  .tagline {{ color: #6E8079; font-size: .8rem; margin-top: .1rem; }}

  /* ============ BARRA LATERAL EM MARINHO ============ */
  [data-testid="stSidebar"] {{
      background-color: {NAVY_FUNDO};
      border-right: none;
  }}
  [data-testid="stSidebar"] * {{ color: {TEXTO_CLARO}; }}
  [data-testid="stSidebar"] h2 {{
      color: #FFFFFF !important;
      font-size: 1.45rem; font-weight: 700;
      margin: .2rem 0 .1rem;
  }}
  [data-testid="stSidebar"] .rotulo {{
      color: {VERDE_CLARO} !important;
      font-size: .95rem; font-weight: 600;
      letter-spacing: .01em; margin: .1rem 0 .9rem;
  }}
  [data-testid="stSidebar"] .stButton > button {{
      width: 100%;
      background-color: {VERDE};
      color: #FFFFFF !important;
      border: 1px solid rgba(255,255,255,.10);
      border-radius: 10px;
      padding: .72rem .9rem;
      font-size: .95rem;
      font-weight: 600;
      text-align: left;
      line-height: 1.4;
      margin-bottom: .5rem;
      transition: background-color .15s ease, transform .1s ease;
  }}
  [data-testid="stSidebar"] .stButton > button:hover {{
      background-color: {VERDE_ESCURO};
      transform: translateX(2px);
  }}
  [data-testid="stSidebar"] .sobre {{
      margin-top: 1.6rem; padding-top: 1.1rem;
      border-top: 1px solid {NAVY_BORDA};
  }}
  [data-testid="stSidebar"] .sobre .titulo {{
      color: #FFFFFF !important;
      font-weight: 700; font-size: 1.05rem; margin-bottom: .6rem;
  }}
  [data-testid="stSidebar"] .sobre .item {{
      font-size: .86rem; line-height: 1.5; margin: .4rem 0;
      color: {TEXTO_CLARO} !important;
  }}
  [data-testid="stSidebar"] .sobre .item b {{
      color: {VERDE_CLARO} !important; font-weight: 600;
  }}

  /* ============ BALÕES ============ */
  [data-testid="stChatMessage"] {{
      background-color: {BALAO};
      border: 1px solid {BORDA};
      border-radius: 14px;
      padding: 1rem 1.2rem;
      margin-bottom: .8rem;
      box-shadow: 0 1px 3px rgba(29,53,80,.06);
  }}

  /* ============ FAIXA DE PERGUNTA EM MARINHO ============ */
  [data-testid="stBottom"] {{ background: transparent; }}
  [data-testid="stBottom"] > div {{
      background: {NAVY_FUNDO};
      border-top: 1px solid {NAVY_BORDA};
      padding-top: .3rem;
  }}
  [data-testid="stBottomBlockContainer"] {{
      max-width: {LARGURA_CONTEUDO} !important;
      padding-left: 3rem !important;
      padding-right: 3rem !important;
  }}
  [data-testid="stChatInput"] {{
      background: {BALAO} !important;
      border: 1px solid rgba(255,255,255,.14) !important;
      border-radius: 14px !important;
      box-shadow: 0 3px 14px rgba(0,0,0,.22);
  }}
  [data-testid="stChatInput"]:focus-within {{
      border-color: {VERDE_CLARO} !important;
      box-shadow: 0 0 0 3px rgba(125,196,160,.28);
  }}
  [data-testid="stChatInput"] textarea {{
      color: #22332C !important; font-size: 1rem !important;
  }}
  [data-testid="stChatInput"] textarea::placeholder {{ color: #90A79B !important; }}
  [data-testid="stChatInputSubmitButton"] {{
      background: {VERDE} !important; border-radius: 10px !important;
  }}
  [data-testid="stChatInputSubmitButton"]:hover {{ background: {VERDE_ESCURO} !important; }}
  [data-testid="stChatInputSubmitButton"] svg {{ fill: #fff !important; }}

  /* ============ DIVERSOS ============ */
  .boasvindas {{
      background: {MENTA_CARD};
      border-left: 4px solid {VERDE};
      border-radius: 10px;
      padding: 1.1rem 1.3rem;
      color: #33433C; font-size: .97rem; line-height: 1.65;
      margin-bottom: 1rem;
  }}
  .aviso {{
      color: #8A9691; font-size: .76rem; text-align: center;
      margin: 1.4rem 0 .4rem; padding-top: .9rem;
      border-top: 1px solid {BORDA};
  }}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# Perguntas frequentes — uma por documento indexado.
# --------------------------------------------------------------------
PERGUNTAS_RAPIDAS = [
    ("🧠  Suspeita de AVC",
     "Quais exames o protocolo de AVC exige na admissão e em que prazo?"),
    ("🩸  Sepse — primeira hora",
     "Quais medidas compõem o pacote de primeira hora do protocolo de sepse?"),
    ("❤️  Dor torácica",
     "Em quanto tempo o eletrocardiograma deve ser realizado na dor torácica?"),
    ("💉  Profilaxia de TEV",
     "A partir de quantos pontos se indica profilaxia farmacológica de TEV?"),
    ("🚨  Time de Resposta Rápida",
     "Quais são os critérios de acionamento do Time de Resposta Rápida?"),
    ("🫁  Pneumonia (PAC)",
     "Como o protocolo avalia a gravidade da pneumonia adquirida na comunidade?"),
]

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "pendente" not in st.session_state:
    st.session_state.pendente = None

# --------------------------------------------------------------------
# Barra lateral
# --------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📋 Protocolos")
    st.markdown('<div class="rotulo">Perguntas frequentes</div>',
                unsafe_allow_html=True)

    for i, (rotulo, texto) in enumerate(PERGUNTAS_RAPIDAS):
        if st.button(rotulo, key=f"rapida_{i}"):
            st.session_state.pendente = texto
            st.rerun()

    st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)

    if st.button("🗑️  Nova conversa", key="limpar"):
        st.session_state.mensagens = []
        st.session_state.pendente = None
        st.rerun()

    # A Resolução CFM 2.454/2026 exige identificar a ferramenta e a versão
    # do modelo empregado. Por isso este bloco lê do config, e não é fixo.
    st.markdown(f"""
    <div class="sobre">
      <div class="titulo">ℹ️ Sobre</div>
      <div class="item"><b>Modelo:</b> {config.CHAT_MODEL}</div>
      <div class="item"><b>Pesquisa:</b> RAG + ChromaDB</div>
      <div class="item"><b>Embeddings:</b> {config.EMBEDDING_MODEL}</div>
    </div>
    """, unsafe_allow_html=True)

try:
    config.validar_ambiente()
except RuntimeError as erro:
    st.error(str(erro))
    st.stop()

# --------------------------------------------------------------------
# Cabeçalho fixo, alinhado à esquerda com o conteúdo
# --------------------------------------------------------------------
escudo_img = f'<img src="{data_uri(ESCUDO)}" alt="">' if ESCUDO.exists() else ""

st.markdown(f"""
<div class="cabecalho">
  <div class="interno">
    {escudo_img}
    <div>
      <div class="wordmark"><span class="sc">SC</span><span class="med">Med</span><span class="ai">AI</span></div>
      <div class="tagline">Consulta a protocolos clínicos institucionais</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.mensagens:
    st.markdown(
        '<div class="boasvindas">👋 Sou o assistente de consulta a protocolos '
        'do SCMedAI. Ajudo profissionais de saúde a localizar rapidamente o '
        'que os protocolos vigentes da instituição dizem — sempre citando o '
        'documento e a página de origem.<br><br>'
        '<b>Não emito diagnóstico, conduta ou prescrição, e não avalio casos '
        'individuais.</b> A decisão clínica é sempre sua.</div>',
        unsafe_allow_html=True,
    )

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

digitada = st.chat_input("Faça uma pergunta sobre um protocolo...")

pergunta = digitada or st.session_state.pendente
st.session_state.pendente = None

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando os protocolos vigentes..."):
            try:
                resposta = responder_pergunta(pergunta)
            except Exception as erro:  # noqa: BLE001
                resposta = (
                    "Não consegui consultar o índice de protocolos.\n\n"
                    f"`{type(erro).__name__}: {erro}`\n\n"
                    "Se o índice ainda não foi construído, rode "
                    "`python -m src.doc_processor`."
                )
        st.markdown(resposta)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})

st.markdown(
    '<div class="aviso">Conteúdo de apoio informacional, baseado nos '
    'protocolos institucionais indexados. Não substitui julgamento clínico. '
    'A decisão é do profissional de saúde.</div>',
    unsafe_allow_html=True,
)
