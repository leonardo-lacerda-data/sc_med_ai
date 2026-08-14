<p align="center">
  <img src="logo_web.png" alt="SCMedAI" width="170">
</p>

<p align="center">
  <strong>Assistente de consulta a protocolos clínicos para profissionais de saúde.</strong><br>
  Responde em linguagem natural citando o documento, a versão e a página de origem.
</p>

<p align="center">
  <em>Não diagnostica, não prescreve e não decide.</em>
</p>

Veja o agente funcionando: [https://scmedai.streamlit.app/](https://scmedai.streamlit.app)

## Arquitetura

| Camada | Tecnologia | Responsabilidade |
| --- | --- | --- |
| Interface | Streamlit | Chat, histórico de sessão e exibição das citações |
| Orquestração | LangChain | Pipeline de ingestão, recuperação e geração |
| Geração | `gemini-2.5-flash` | Respostas ancoradas nos trechos recuperados |
| Embeddings | `gemini-embedding-001` | Vetorização dos documentos e das perguntas |
| Banco vetorial | ChromaDB | Armazenamento e busca por similaridade |
| Publicação | Nginx | Proxy reverso com suporte a WebSocket |
| Infraestrutura | OCI — VM Ubuntu + Load Balancer | Execução e ponto de entrada estável |
| Provisionamento | Terraform + cloud-init | Stack no OCI Resource Manager |

> Roda com uma chave gratuita do [Google AI Studio](https://aistudio.google.com) — sem cartão de crédito. O `gemini-2.5-flash` está no tier gratuito.

## O que ele faz

- Localiza o protocolo pertinente a uma pergunta.
- Responde a pergunta citando a fonte do documento, versão, vigência e página.
- Recupera apenas documentos com status `vigente`.
- Abstém-se quando a informação não está no corpus.
- Registra cada consulta em log auditável.

## O que ele não faz

Escrito antes da lista do que ele faz, de propósito. É esta lista que
define o nível de risco do sistema.

- Não sugere nem comunica diagnóstico ou prognóstico.
- Não emite conduta, prescrição ou plano terapêutico.
- Não avalia caso individual nem calcula dose para paciente específico.
- Não interpreta exames, laudos ou imagens.
- Não recebe nem armazena dado identificado de paciente.
- Não responde nada fora do corpus institucional indexado.
- Não interage com pacientes.

---

## Como rodar

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux:    source .venv/bin/activate

pip install -r requirements.txt

cp .example .env      # e preencha a GOOGLE_API_KEY

python -m src.pdf_loader     # carrega PDFs e armazena no ChromaDB
```

## Estrutura

```
data/raw/         PDFs originais dos protocolos
data/metadata.csv ficha de metadados — sem isto, nada é indexado
data/index/       índice vetorial (artefato de build, não versionado)
respostas_esperadas.csv conjunto de referência e resultados de avaliação
prompts/          prompt de sistema versionado
src/              ingestão, recuperação, guardrails, cadeia
```

## Stack

LangChain · Google Gemini · ChromaDB · Streamlit
Implantação em Oracle Cloud Infrastructure.
