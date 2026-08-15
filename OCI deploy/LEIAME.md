# SCMedAI — stack para o OCI Resource Manager

VCN, instância `E2.1.Micro` atrás de um Load Balancer flexível, aplicação
baixada direto do repositório público no GitHub.

| Camada | Escolha |
|---|---|
| Fonte da aplicação | tarball do repositório público, com o índice vetorial versionado |
| Runtime | ambiente virtual Python sob systemd |
| Publicação | nginx como proxy reverso, com suporte a WebSocket |
| Provisionamento | cloud-init |
| Entrada | Load Balancer flexível, 10 Mbps |

O índice vetorial está **versionado no repositório**. A instância nunca
indexa: ela baixa o código, instala as dependências e sobe o serviço.

> **Por que GitHub e não Object Storage:** o tarball público não exige
> token, não expira e não depende do bucket de ninguém. Qualquer pessoa
> pode aplicar esta stack com a própria chave do Gemini e obter a
> aplicação funcionando — o que uma Pre-Authenticated Request não
> permitiria.

> O OCI Container Registry não está disponível em conta Always Free
> ("Free tier account is not supported"). O `Dockerfile` na raiz do
> projeto continua válido e a imagem funciona localmente.

---

## Passo 1 — Publicar o índice no repositório

Na sua máquina, gere o índice e envie junto com o código:

```powershell
python -m src.pdf_loader
git add . && git commit -m "atualiza indice" && git push
```

O `chroma_db/` é versionado de propósito: são 2,1 MB e é o que permite
que a instância suba sem reindexar.

---

## Passo 2 — Confirmar que o tarball responde

```powershell
curl.exe -IL "https://github.com/leonardo-lacerda-data/sc_med_ai/archive/refs/heads/main.tar.gz"
```

Precisa terminar em `200 OK`. Se o repositório for privado, retorna 404 —
nesse caso torne-o público ou troque a fonte.

---

## Passo 3 — Subir a stack

1. Compacte **esta pasta** (`OCI deploy`) em um zip
2. Console → **Developer Services → Resource Manager → Stacks → Create Stack**
3. Origem: **My configuration** → **.zip file**
4. Preencha:
   - **Fonte da aplicação** — já vem preenchida com o tarball do repositório
   - **Chave da API do Gemini** — campo mascarado
   - **Chave pública SSH** — para ler o log se algo falhar
   - **Shape** — `VM.Standard.E2.1.Micro`
   - **Banda do Load Balancer** — 10/10
5. **Plan** → confira → **Apply**

---

## Passo 4 — Verificar

O `apply` termina antes da aplicação estar no ar. O cloud-init ainda baixa
o pacote e instala as dependências — cerca de 8 minutos, dominados pelo
`pip install`.

```bash
ssh -i ~/.ssh/scmedai-key ubuntu@<IP-da-instancia>

cloud-init status
ls -la /opt/scmedai
systemctl status scmedai
sudo tail -50 /var/log/cloud-init-output.log
```

O `ls` entrega muito: se `/opt/scmedai` tiver só `.env` e `.venv`, o
download ou a extração falhou.

Só depois abra a URL do Load Balancer, **com `http://`** — não existe
listener na 443. Teste de outra rede, do celular com dados móveis.

---

## Atualizar a aplicação

Faça `git push` e, na instância:

```bash
wget -O /tmp/app.tar.gz "https://github.com/leonardo-lacerda-data/sc_med_ai/archive/refs/heads/main.tar.gz"
sudo tar -xzf /tmp/app.tar.gz -C /opt/scmedai --strip-components=1
sudo chown -R ubuntu:ubuntu /opt/scmedai
sudo -u ubuntu /opt/scmedai/.venv/bin/pip install --no-cache-dir -r /opt/scmedai/requirements.txt
sudo systemctl restart scmedai
```

O `.env` sobrevive: ele não existe no repositório.

---

## Decisões que valem explicar na entrega

**Índice versionado no repositório.** A instância tem 1 GB de RAM. Gerar
embeddings nela seria o maior pico de memória da implantação. Com o índice
pronto, a instância só instala dependências e serve consultas.

**Fonte no GitHub, não em bucket.** O tarball público dispensa token e não
expira. Isso torna a stack reproduzível por terceiros — critério que uma
Pre-Authenticated Request não atende, porque ela pertence a uma conta.

**Uma instância, não duas.** O Streamlit guarda o estado da conversa na
memória do processo. Duas instâncias exigiriam persistência de sessão no
balanceador, e ainda assim não dariam redundância real — quem estivesse na
instância que caísse perderia a conversa de qualquer forma.

**Load Balancer com um backend só.** Não é balanceamento: é ponto de
entrada estável. O IP público da instância muda a cada recriação; o do
balanceador não.

**nginx entre o balanceador e a aplicação.** O Streamlit conversa por
WebSocket. Sem os cabeçalhos de Upgrade, a página carrega e trava em
"Connecting...".

**Dois firewalls.** A Security List da VCN libera 80 e 443 na borda; a
imagem Ubuntu da OCI vem com iptables bloqueando tudo menos a 22. O
cloud-init trata o segundo. Esquecer qualquer um dá o mesmo sintoma.

---

## Quando algo der errado

| Sintoma | Onde olhar |
|---|---|
| 502 no navegador | nginx está de pé, o Streamlit não: `systemctl status scmedai` |
| `/opt/scmedai` só com `.env` | o download falhou: teste o tarball com `curl -IL` |
| Serviço reinicia sozinho | estouro de memória: `free -h`, confirme o swap |
| Página trava em "Connecting..." | WebSocket — confira o bloco `proxy_set_header Upgrade` |
| Erro de índice em toda pergunta | `chroma_db/` não está versionado no repositório |
| SSH com timeout | rota `0.0.0.0/0` para o Internet Gateway na tabela de rotas |
| Erro de capacidade no apply | a `E2.1.Micro` existe em um único AD; tente outro |

---

## Pendência de conformidade

A chave da API fica em `/opt/scmedai/.env` com permissão `0600`, lida pelo
systemd via `EnvironmentFile`. Para uso com dado de instituição,
deve migrar para o **OCI Vault**.
