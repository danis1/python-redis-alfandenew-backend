# AlfandeNew — Backend

API REST em Python (FastAPI) integrada ao Redis para o sistema de controle de tráfego marítimo.

## 🚀 Como executar

### Desenvolvimento com Docker Compose

**Pré-requisitos:** Docker Engine com Docker Compose v2.20 ou superior, ou Docker Desktop atualizado com contêineres Linux, e porta `8000` disponível.

Na raiz do repositório:

```sh
docker compose up --build --wait
```

O comando constrói a imagem da API, inicia os dois serviços em segundo plano e aguarda suas verificações de saúde:

- **API:** Python 3.12 e Uvicorn em `0.0.0.0:8000`, publicado em `http://localhost:8000`.
- **Redis:** Redis 7 na rede interna, acessível pela API em `redis:6379`. A porta `6379` não é publicada no host.
- **Recarga automática:** o código local é montado em `/app`; alterações em arquivos Python reiniciam a API automaticamente. Alterações em `requirements.txt` ou no Dockerfile exigem executar novamente `docker compose up --build --wait`.
- **Inicialização:** a API aguarda o Redis ficar saudável. A saúde da API consulta `/ping`, verificando também a conexão com o Redis.

**Os dados são temporários:** a persistência do Redis está desabilitada e `/data` usa memória temporária (`tmpfs`). Reiniciar, recriar ou remover o contêiner Redis apaga todos os registros e o contador de IDs.

### Acesso e verificação

| Endereço | Resultado esperado |
| --- | --- |
| `http://localhost:8000/` | `{"mensagem":"ok"}` |
| `http://localhost:8000/ping` | `true` quando a conexão com Redis funciona |
| `http://localhost:8000/docs` | Swagger para consultar e testar os endpoints |
| `http://localhost:8000/openapi.json` | Especificação OpenAPI |
| `http://localhost:8000/api/v1/registros` | Listagem de registros; inicialmente `{"data":[]}` |

Confira os serviços e acompanhe os logs:

```sh
docker compose ps
docker compose logs -f api redis
```

Os dois serviços devem aparecer como `healthy`. Para verificar o Redis diretamente:

```sh
docker compose exec redis redis-cli ping
```

A resposta esperada é `PONG`. Para encerrar e remover os contêineres e a rede:

```sh
docker compose down
```

### Configuração da conexão com Redis

A API lê a variável de ambiente `REDIS_URL`:

| Execução | URL |
| --- | --- |
| Sem a variável definida | `redis://localhost:6379/0` |
| Docker Compose | `redis://redis:6379/0` (definida em `compose.yaml`) |

O Dockerfile instala as versões de `requirements.txt` e inicia o Uvicorn sem recarga automática. O Compose adiciona a recarga e a montagem do código para desenvolvimento local.

### Execução sem Docker para a API

Com Python 3.12 e um Redis já acessível em `localhost:6379` (ou pela URL definida em `REDIS_URL`), instale as dependências e inicie o servidor:

```sh
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

O Redis do Compose fica restrito à rede dos contêineres; este modo exige um Redis acessível pelo host. A API e o Swagger continuam disponíveis nos endereços acima.

## 🔗 Integração com o Frontend
O frontend Angular já está configurado com um proxy (`proxy.conf.json`) para redirecionar as chamadas de `/api/v1/**` para cá. Basta rodar os dois lados (porta 8000 e 4200).

## 🗄️ Estrutura no Redis
- `contador`: Gera os IDs únicos sequenciais.
- `registros`: Guarda a lista de todos os IDs cadastrados.
- `registro:{id}`: Armazena o JSON do navio.

## ⚠️ Formato de Erro
Qualquer falha de regra de negócio ou validação retorna status HTTP 400 ou 404 com o JSON:
`{ "errorMessage": "string" }`
