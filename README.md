# Crawty (MatchLar) 🏠

Uma plataforma web completa para capturar, catalogar, analisar e exibir um compilado de imóveis das imobiliárias e corretores parceiros de São João del Rei e região.

- 🌐 **Frontend (Vercel)**: [https://crawty-8dlt.vercel.app](https://crawty-8dlt.vercel.app)
- ⚙️ **Backend API (Google Cloud Run)**: [https://crawty-api-808358144730.us-central1.run.app](https://crawty-api-808358144730.us-central1.run.app)
- 🗄️ **Banco de Dados**: MongoDB Atlas

---

## ✨ Principais Funcionalidades

1. **Busca Centralizada e Monitoramento de Preços (`/`)**:
   - Filtros combinados por modalidade (Venda/Aluguel), cidade, bairro, tipo/subtipo, faixa de preço, área útil, quartos, suítes, banheiros e vagas.
   - Rastreamento automático de histórico de preços (`historico_precos`) com selo de **Oportunidade / Queda de Preço** para imóveis que tiveram redução de valor.
   - Contabilização de cliques e geração de leads qualificados (`/leads/clique`) ao redirecionar o cliente para a imobiliária ou corretor.

2. **Modo Match — Descoberta Estilo "Tinder" (`/match`)**:
   - Experiência interativa onde o usuário define primeiro suas **Preferências de Perfil** (objetivo, cidade, bairro, tipo de imóvel, orçamento máximo e quartos mínimos) e, em seguida, navega por uma fila de cards visuais.
   - Galeria rápida de fotos integrada ao card e suporte a atalhos de teclado (`←` para passar e `→` para dar Match).
   - **Persistência em Cookies (`crawty_matches`)**: Todos os imóveis marcados com *Match!* ficam salvos nos cookies do navegador do usuário para consulta em acessos futuros, com opção de visitar o anúncio na imobiliária ou excluir matches individualmente.

3. **Portal B2B — Área do Corretor e Imobiliárias Parceiras (`/corretor/login` e `/corretor`)**:
   - Acesso fechado e exclusivo para corretores autônomos e imobiliárias credenciadas mediante contrato.
   - **Gestão Completa de Imóveis Próprios (CRUD)**: Cadastro com fotos múltiplas, histórico de preços automático, pausa/reativação e contato direto no WhatsApp.
   - **Sistema de Impulsionamento & Destaque (Vitrine Premium)**: Corretores podem impulsionar seus imóveis por períodos de 7, 15 ou 30 dias. Imóveis impulsionados recebem o selo dourado **"⭐ Destaque"** e posicionamento prioritário no topo da busca padrão por relevância e no Modo Match.
   - **Painel de Métricas & Desempenho**: Visão analítica em tempo real de imóveis na carteira, ativos, pausados, impulsionados e total de cliques/leads gerados.
   - Edição de **Dados Comerciais e Contato Direto** (Nome, Registro CRECI, WhatsApp para leads, Telefone, E-mail e Site/Instagram), permitindo que pequenos corretores divulguem seus imóveis mesmo sem possuir site próprio.

4. **Inteligência de Mercado Exclusiva (`/estatisticas`)**:
   - Painel analítico **restrito a corretores autenticados** (oculto para visitantes comuns e protegido via Bearer Token na API).
   - Indicadores estratégicos em tempo real: valor médio do $\text{m}^2$ de venda e locação por bairro, ticket médio e mediana, taxa de absorção de estoque, distribuição por faixas de preço e *market share* por imobiliária.

---

## 📋 Arquitetura do Sistema

```
Crawty/
├── backend/                  # API FastAPI, Segurança B2B e conexão com MongoDB
│   ├── api.py               # Endpoints REST (/imoveis, /filtros, /estatisticas, /auth/*)
│   ├── auth.py              # Hash PBKDF2-SHA256, Tokens HMAC-SHA256 e proteção de rotas
│   ├── database.py          # Inicialização e índices do MongoDB (imoveis, cliques, corretores)
│   ├── models.py            # Schemas e validação com Pydantic
│   └── normalizer.py        # Padronização de cidades, bairros, tipos e subtipos
├── crawlers/                 # Módulos de captura das imobiliárias
│   ├── base_homeclix.py     # Base para portais Homeclix (API REST)
│   ├── zanfer.py, chaves.py, flavio.py, lider.py, krasis.py, ...
│   └── domicilium.py        # Scraper concorrente Domicilium
├── dados_imoveis/            # Saída JSON individual por crawler (ignorado no Git)
├── frontend/                 # Interface Web (React + Vite + Tailwind CSS)
│   └── src/
│       ├── pages/           # Home, DetalhesImovel, ModoMatch, LoginCorretor, PainelCorretor, Estatisticas
│       └── utils/           # Persistência de cookies do Modo Match e sessão B2B do corretor
├── Dockerfile                # Containerização do Backend para Cloud Run
├── credentials.env           # Credenciais locais do MongoDB (não versionado)
├── main.py                   # Execução concorrente dos crawlers
├── loader_mongo.py           # Carga seletiva/interativa para o MongoDB
└── gerenciar_corretores.py   # CLI administrativa para criar e gerenciar contas de corretores
```

---

## 🔐 Gestão de Contas de Corretores (`gerenciar_corretores.py`)

O acesso à **Área do Corretor** (`/corretor`) e ao painel de **Inteligência de Mercado** (`/estatisticas`) não possui auto-cadastro público: as contas são criadas e gerenciadas pela administração da plataforma através do utilitário de linha de comando [`gerenciar_corretores.py`](file:///c:/UFSJ/Crawty/gerenciar_corretores.py).

### 1. Criar um novo corretor ou imobiliária parceira (`criar`)
```bash
python gerenciar_corretores.py criar \
  --usuario "joao.corretor" \
  --senha "SenhaSegura123" \
  --nome "João Silva" \
  --imobiliaria "João Silva Consultoria Imobiliária" \
  --creci "MG-54321" \
  --whatsapp "(32) 99999-8888" \
  --telefone "(32) 3371-0000" \
  --email "contato@joaosilvaimoveis.com.br" \
  --site "https://instagram.com/joaosilvaimoveis" \
  --role corretor
```

**Parâmetros disponíveis no comando `criar`:**
| Parâmetro | Obrigatório | Descrição |
| :--- | :---: | :--- |
| `--usuario` | **Sim** | Login único do parceiro (convertido automaticamente para minúsculas). |
| `--senha` | **Sim** | Senha inicial de acesso (armazenada com hash `PBKDF2-HMAC-SHA256`). |
| `--nome` | **Sim** | Nome completo do corretor ou responsável pela conta. |
| `--imobiliaria` | Não | Nome comercial da imobiliária ou marca do corretor autônomo (se omitido, usa `--nome`). |
| `--creci` | Não | Número do registro CRECI (ex: `MG-12345`). |
| `--whatsapp` | Não | Número de WhatsApp para recebimento direto de leads. |
| `--telefone` | Não | Telefone fixo ou secundário. |
| `--email` | Não | E-mail comercial de contato. |
| `--site` | Não | Link externo para site ou perfil de rede social. |
| `--role` | Não | Perfil da conta: `corretor` (padrão) ou `admin`. |

### 2. Listar todos os corretores cadastrados (`listar`)
Exibe uma tabela no terminal com o login, nome do responsável, imobiliária/marca, perfil (`role`) e status atual (`ATIVO` ou `SUSPENSO`):
```bash
python gerenciar_corretores.py listar
```

### 3. Redefinir a senha de um corretor (`alterar-senha`)
Caso o parceiro esqueça a senha, você pode definir uma nova senha imediatamente:
```bash
python gerenciar_corretores.py alterar-senha --usuario "joao.corretor" --senha "NovaSenha456"
```

### 4. Suspender ou reativar o acesso de um corretor (`status`)
Se um contrato for encerrado ou estiver pendente de renovação, você pode suspender (ou reativar) o acesso sem apagar os dados da conta:
```bash
# Suspender acesso (bloqueia login e invalida o token atual imediatamente)
python gerenciar_corretores.py status --usuario "joao.corretor" --ativo false

# Reativar acesso
python gerenciar_corretores.py status --usuario "joao.corretor" --ativo true
```

---

## ☁️ Deploy do Backend no Google Cloud Run

O backend é executado no **Google Cloud Run** como o serviço `crawty-api` (na região `us-central1`).

### Caso 1: Apenas atualizar credenciais ou variáveis de ambiente (Sem rebuild)

Se você apenas alterou a senha do MongoDB ou variáveis e não mudou o código Python:

#### Opção A: Pelo Console Web (Recomendado e mais rápido)
1. Acesse o [Google Cloud Console - Cloud Run](https://console.cloud.google.com/run).
2. Selecione o serviço **`crawty-api`** (região `us-central1`).
3. Clique em **Editar e implantar nova revisão** (*Edit & Deploy New Revision*).
4. Na aba **Contêiner(es)** ➔ **Variáveis e segredos** (*Variables & Secrets*):
   - Atualize `MONGODB_URL` com a nova connection string do MongoDB Atlas.
   - Verifique `DB_NAME` (padrão: `imobiliaria_db`).
5. Clique em **Implantar** (*Deploy*). Em poucos segundos uma nova revisão estará ativa.

#### Opção B: Pelo Terminal via `gcloud`
1. Efetue login no SDK do Google Cloud (caso o token tenha expirado):
   ```bash
   gcloud auth login
   ```
2. Atualize as variáveis do serviço:
   ```bash
   gcloud run services update crawty-api \
     --region us-central1 \
     --update-env-vars "MONGODB_URL=mongodb+srv://<USER>:<PASS>@crawfy.tcfndp8.mongodb.net/?retryWrites=true&w=majority&appName=Crawfy,DB_NAME=imobiliaria_db"
   ```

---

### Caso 2: Atualizar o código da API (Novo Build e Deploy)

Sempre que fizer alterações nos arquivos da pasta `backend/` ou no `requirements.txt`:

1. Faça login na sua conta Google Cloud:
   ```bash
   gcloud auth login
   ```
2. Garanta que o projeto correto está ativo:
   ```bash
   gcloud config set project <SEU_PROJECT_ID>
   ```
3. Dispare a compilação e deploy direto da raiz do projeto usando o Cloud Build (não requer Docker rodando na sua máquina):
   ```bash
   gcloud run deploy crawty-api
     --source .
     --region us-central1
     --allow-unauthenticated
   ```

*(Opcional com Docker local)*: Caso prefira compilar a imagem localmente com o Docker Desktop aberto:
```bash
docker build -t gcr.io/<SEU_PROJECT_ID>/crawty-api:latest .
docker push gcr.io/<SEU_PROJECT_ID>/crawty-api:latest
gcloud run deploy crawty-api --image gcr.io/<SEU_PROJECT_ID>/crawty-api:latest --region us-central1
```

---

## 🕷️ Como Rodar os Crawlers e Carregar no MongoDB

### 1. Configurar credenciais locais
Crie ou edite o arquivo `credentials.env` na raiz:
```env
MONGODB_URL=mongodb+srv://<USER>:<SENHA>@crawfy.tcfndp8.mongodb.net/?retryWrites=true&w=majority&appName=Crawfy
DB_NAME=imobiliaria_db
```

### 2. Executar a Captura de Imóveis
Execute o script principal:
```bash
python main.py
```
- Dispara múltiplos crawlers simultaneamente com `ThreadPoolExecutor`.
- Gera um arquivo `.json` individual para cada imobiliária na pasta `dados_imoveis/` (ex: `imoveis_zanfer.json`, `imoveis_chaves.json`, etc.).
- Não gera arquivo consolidado único, permitindo inspecionar cada fonte separadamente.

### 3. Enviar Dados ao MongoDB (`loader_mongo.py`)
Você pode escolher exatamente quais imobiliárias deseja enviar:

- **Modo Interativo** (Menu numérico com contagem de ativos e histórico):
  ```bash
  python loader_mongo.py
  ```
  Permite escolher pelo número (ex: `1`), múltiplos arquivos (ex: `1, 3` ou `1-5`) ou todos (`T`).

- **Modo Linha de Comando Direta**:
  ```bash
  # Enviar apenas uma imobiliária
  python loader_mongo.py zanfer

  # Enviar arquivo específico
  python loader_mongo.py dados_imoveis/imoveis_zanfer.json

  # Enviar todos os arquivos de uma vez
  python loader_mongo.py --todos
  ```

---

## 🏛️ Gestão de Histórico e Imóveis Descontinuados (Auditoria)

O sistema segue uma política rigorosa de **preservação histórica de dados**:

1. **Nunca Deletar**: Imóveis que deixam de ser listados pelas imobiliárias **nunca são excluídos** do MongoDB.
2. **Ciclo de Vida Automático**:
   - Cada imóvel presente no arquivo capturado é marcado como ativo (`ativo = True`, `descontinuado_em = None`, `last_updated = agora`).
   - Imóveis daquela **mesma imobiliária** que já existiam no banco, mas **não vieram na captura mais recente**, são automaticamente marcados como descontinuados (`ativo = False`, `descontinuado_em = agora`).
   - Caso um imóvel retorne ao ar futuramente, ele é automaticamente reativado.
3. **Exibição no Frontend**:
   - O site na Vercel consome apenas imóveis ativos (`/imoveis?status=ativos`).
   - Os filtros agregam apenas bairros, cidades e tipos com imóveis ativos disponíveis.
   - Caso um usuário acerte um link direto para um imóvel descontinuado, a tela de detalhes avisa educadamente: *⚠️ Imóvel retirado do ar pela imobiliária*.
4. **Auditoria via API**:
   - Para auditar ou analisar o histórico, a API permite:
     - `/imoveis?status=ativos` (Padrão do site)
     - `/imoveis?status=descontinuados` (Apenas imóveis históricos)
     - `/imoveis?status=todos` (Base completa)

---

## 💻 Frontend (Vercel)

Para rodar o frontend localmente em modo desenvolvimento:
```bash
cd frontend
npm install
npm run dev
```

Para gerar o build de produção:
```bash
cd frontend
npm run build
```
O deploy para produção é acionado automaticamente a cada `git push` na branch `main` conectado à **Vercel**.

---

## 📝 Licença
Este projeto está sob licença MIT.