# Crawty 🏠

Um software web completo para capturar, catalogar e exibir um compilado de imóveis das imobiliárias de São João del Rei e região.

- 🌐 **Frontend (Vercel)**: [https://crawty-8dlt.vercel.app](https://crawty-8dlt.vercel.app)
- ⚙️ **Backend API (Google Cloud Run)**: [https://crawty-api-808358144730.us-central1.run.app](https://crawty-api-808358144730.us-central1.run.app)
- 🗄️ **Banco de Dados**: MongoDB Atlas

---

## 📋 Arquitetura do Sistema

```
Crawty/
├── backend/               # API FastAPI e conexão com MongoDB
│   ├── api.py            # Endpoints REST (/imoveis, /filtros, etc.)
│   ├── database.py       # Inicialização e pool do MongoDB
│   └── models.py         # Schemas e validação com Pydantic
├── crawlers/              # Módulos de captura das imobiliárias
│   ├── base_homeclix.py  # Base para portais Homeclix (API REST)
│   ├── zanfer.py, chaves.py, flavio.py, lider.py, krasis.py, ...
│   └── domicilium.py     # Scraper concorrente Domicilium
├── dados_imoveis/         # Saída JSON individual por crawler
├── frontend/              # Interface Web (React + Vite + Tailwind CSS)
├── Dockerfile             # Containerização do Backend para Cloud Run
├── credentials.env        # Credenciais locais do MongoDB (não versionar)
├── main.py                # Execução concorrente dos crawlers
└── loader_mongo.py        # Carga seletiva/interativa para o MongoDB
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
   gcloud run deploy crawty-api \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "MONGODB_URL=mongodb+srv://<USER>:<PASS>@crawfy.tcfndp8.mongodb.net/?retryWrites=true&w=majority&appName=Crawfy,DB_NAME=imobiliaria_db"
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