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

---

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

## O que ele faz

- Localiza o protocolo pertinente a uma pergunta.
- Cita o trecho literal com documento, versão, vigência e página.
- Recupera apenas documentos com status `vigente`.
- Abstém-se quando a informação não está no corpus.
- Registra cada consulta em log auditável.

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
eval/             conjunto de referência e resultados de avaliação
prompts/          prompt de sistema versionado
src/              ingestão, recuperação, guardrails, cadeia
```

## Stack

LangChain · Google Gemini · ChromaDB · Streamlit
Implantação em Oracle Cloud Infrastructure.
