# AlfandeNew — Backend

API REST em Python (FastAPI) integrada ao Redis para o sistema de controle de tráfego marítimo.

## 🚀 Como executar

**1. Suba o Redis (Banco de Dados)**
Se tiver Docker, rode no terminal:
`docker run -d -p 6379:6379 --name redis redis:7`

**2. Instale as dependências**
`pip install fastapi uvicorn redis`

**3. Inicie o servidor**
`python -m uvicorn main:app --reload`

O servidor estará rodando em `http://localhost:8000`.
A documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

## 🔗 Integração com o Frontend
O frontend Angular já está configurado com um proxy (`proxy.conf.json`) para redirecionar as chamadas de `/api/v1/**` para cá. Basta rodar os dois lados (porta 8000 e 4200).

## 🗄️ Estrutura no Redis
- `contador`: Gera os IDs únicos sequenciais.
- `registros`: Guarda a lista de todos os IDs cadastrados.
- `registro:{id}`: Armazena o JSON do navio.

## ⚠️ Formato de Erro
Qualquer falha de regra de negócio ou validação retorna status HTTP 400 ou 404 com o JSON:
`{ "errorMessage": "string" }`
