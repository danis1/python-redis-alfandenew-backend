# AlfandeNew — Backend de Controle de Tráfego Marítimo

API REST desenvolvida em Python para gerenciar o tráfego marítimo de cargas. Este repositório contém somente o backend (API); o frontend (Angular) deve ser executado separadamente. A API foi construída com FastAPI e utiliza o Redis como banco de dados em memória (NoSQL).

## Requisitos
- Python 3.10 ou superior.
- Redis (recomendado rodar via Docker).
- pip (gerenciador de pacotes do Python).

## Executar o Backend

1. **Suba o banco de dados (Redis):**
   Se você tiver o Docker instalado, rode no terminal:
   ```bash
   docker run -d -p 6379:6379 --name redis redis:7
