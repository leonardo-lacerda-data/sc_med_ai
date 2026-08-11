# SCMedAI — stack para o OCI Resource Manager

Adaptação da estrutura de aula: VCN, instâncias `E2.1.Micro` atrás de um
Load Balancer flexível, provisionamento por cloud-init. Sem Docker.

**O que mudou em relação ao portal WordPress:**

| | Portal (aula) | SCMedAI |
|---|---|---|
| Runtime | Apache + PHP | Python + Streamlit sob systemd |
| Publicação | Apache serve arquivos | nginx faz proxy reverso com WebSocket |
| Dados | MySQL HeatWave em subnet privada | índice vetorial dentro do pacote |
| Segredo | senha escrita no cloud-init | variável sensível do Terraform |
| `template_file` | provider arquivado | função nativa `templatefile()` |

---

## Passo 1 — Construir o índice e empacotar a aplicação

Na sua máquina, **na raiz do projeto** (`scmedai/`, não nesta pasta):

```powershell
python -m src.doc_processor
```

Confirme que `chroma_db/` existe e não está vazio. Depois monte o zip com
exatamente estes itens **na raiz do arquivo**:

```
app.py
requirements-docker.txt
src/
prompts/
.streamlit/
chroma_db/
escudo_header.png
```

```powershell
Compress-Archive -Path app.py, requirements-docker.txt, src, prompts, .streamlit, chroma_db, escudo_header.png -DestinationPath scmedai.zip -Force
```

> Não inclua `.env`, `.venv/`, `data/`, `logo.png` nem `requirements.txt`.
> O `.env` traz credencial; o `requirements.txt` traz `sentence-transformers`,
> que arrasta o PyTorch e não instala em 1 GB de RAM.

---

## Passo 2 — Publicar o pacote no Object Storage

1. Console → **Storage → Buckets** → crie ou use um bucket existente
2. **Upload** do `scmedai.zip`
3. No objeto → menu ⋮ → **Create Pre-Authenticated Request**
   - Tipo: **Object** · Acesso: **Permit reads**
   - Validade: cubra todo o período de avaliação
4. **Copie a URL na hora** — ela não é exibida novamente

Essa URL vai no campo `app_bundle_url` da stack.

---

## Passo 3 — Subir a stack no Resource Manager

1. Compacte **esta pasta** (`OCI deploy`) em um zip
2. Console → **Developer Services → Resource Manager → Stacks → Create Stack**
3. Origem: **My configuration** → **.zip file** → envie o zip
4. Preencha o formulário (o `schema.yaml` monta a tela):
   - **URL do pacote da aplicação** — o PAR do passo 2
   - **Chave da API do Gemini** — campo mascarado
   - **Chave pública SSH** — para poder ler o log se algo falhar
   - **Shape** — `VM.Standard.E2.1.Micro`
   - **Banda do Load Balancer** — 10/10, para ficar na camada gratuita
5. **Plan** → confira o que será criado
6. **Apply**

---

## Passo 4 — Aguardar e verificar

O `apply` termina antes da aplicação estar no ar. O cloud-init ainda vai
criar swap, baixar o pacote e instalar as dependências — **cerca de 8
minutos**, dominados pelo `pip install`.

```bash
ssh ubuntu@<IP-da-instancia>
sudo tail -f /var/log/cloud-init-output.log     # acompanhe até o final_message
systemctl status scmedai
curl -I http://127.0.0.1/_stcore/health         # 200 antes de olhar o LB
```

Só depois abra a `URL_da_aplicacao` dos outputs. Teste de outra rede —
do celular com dados móveis — porque testar da sua própria rede esconde
problema de regra de entrada.

---

## Decisões que valem explicar na entrega

**Persistência de sessão no Load Balancer.** O Streamlit guarda o estado
da conversa na memória do processo. Com duas instâncias e round-robin
puro, o usuário salta de backend e o histórico "some". O backend set usa
cookie do próprio balanceador para prender cada usuário a uma instância.

**Timeout de 300s no listener.** O padrão de 60s derruba o WebSocket do
Streamlit enquanto o usuário lê a resposta, e a tela volta para
"Connecting...".

**Swap antes de tudo no cloud-init.** O `pip install` do chromadb com
langchain é o pico de memória de toda a implantação. Sem swap, o kernel
mata o processo e o cloud-init falha no meio — a máquina fica de pé e sem
aplicação, que é o pior modo de falha para diagnosticar.

**Dois firewalls.** A Security List da VCN libera 80/443 na borda, mas a
imagem Ubuntu da OCI vem com iptables bloqueando tudo menos a 22. O
cloud-init trata o segundo. Esquecer qualquer um dá o mesmo sintoma.

**Health check em `/_stcore/health`.** Endpoint próprio do Streamlit:
responde rápido, não renderiza a página e não abre sessão à toa.

---

## Quando algo der errado

| Sintoma | Onde olhar |
|---|---|
| LB responde 502 | `systemctl status scmedai` na instância |
| Página trava em "Connecting..." | WebSocket — confira o bloco `proxy_set_header Upgrade` do nginx |
| Histórico da conversa some | persistência de sessão do backend set |
| `cloud-init` parou no meio | `sudo tail -200 /var/log/cloud-init-output.log`; quase sempre é memória |
| Toda pergunta dá erro de índice | `chroma_db/` não entrou no zip, ou não está na raiz dele |
| Respostas ruins mas sem erro | `gemini_embedding_model` diferente do usado na indexação |
| Erro de capacidade no `apply` | a `E2.1.Micro` só existe em um AD; tente outro |

---

## Pendência de conformidade

A chave da API fica em `/opt/scmedai/.env` com permissão `0600`. Para uso
com dado de instituição, ela deve migrar para o **OCI Vault** — que é
Always Free até 150 segredos e está previsto no passo 7 do backlog.
