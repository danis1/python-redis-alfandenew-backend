from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Optional, Literal
from pydantic import BaseModel, Field 
from datetime import datetime
from fastapi.exceptions import RequestValidationError
import redis
import json
import os



class Navio(BaseModel):
    nomeDeExibicao: str = Field(min_length=1)
    descricaoDaCarga: Optional[str] = None
    pais: str = Field(min_length=1)
    origem: str = Field(min_length=1)
    destino: str = Field(min_length=1)
    timestampSaida: datetime
    timestampChegada: Optional[datetime] = None
    status: Literal[
        "aguardando saída",
        "em trânsito",
        "aguardando alfândega",
        "em processamento",
        "finalizado",
        "cancelado",
    ]
    comandante: str = Field(min_length=1)


app = FastAPI()

r = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)

@app.get("/")
def mensagem():
    return {"mensagem": "ok"}

@app.get("/ping")
def ping():
    return r.ping()

@app.exception_handler(RequestValidationError)
def erro_validacao(request, exc):
    return JSONResponse(
        status_code=400,
        content={"errorMessage": "Dados inválidos"}
    )

#POST /api/v1/registros ===============================================
@app.post("/api/v1/registros")
def registros(navio: Navio):
    #RN1 – Não é possível definir a situação “aguardando alfândega” ou “finalizado” sem preencher a hora da chegada
    id = r.incr("contador")
    if navio.status in ("aguardando alfândega", "finalizado") and navio.timestampChegada is None:
        return JSONResponse(
            status_code=400,
            content={"errorMessage": "Para esse status, a data de chegada é obrigatória"}
        )
    if navio.timestampChegada is not None and navio.timestampSaida is not None:
        if navio.timestampSaida >= navio.timestampChegada:
            return JSONResponse(
                status_code=400,
                content={"errorMessage": "A data de saída deve ser anterior à data de chegada"}
            )
    dados = navio.model_dump(mode="json") #grava o objeto Navio em um dicionário
    dados["id"] = id # adiciona o ID ao dicionário
    r.sadd("registros", id)
    r.set(f"registro:{id}", json.dumps(dados)) #grava o registro no Redis
    return dados



#GET /api/v1/registros/{id:int} ===============================================

@app.get("/api/v1/registros/{id}")
def buscar_registro(id: int):
    texto = r.get(f"registro:{id}")

    if texto is None:
        return JSONResponse(
            status_code=404,
            content={"errorMessage": "Registro não encontrado"}
        )

    return json.loads(texto)
    

#PUT  /api/v1/registros/{id:int} ===============================================
@app.put("/api/v1/registros/{id}")
def atualizar(id: int, navio: Navio):
    registro_existente = r.get(f"registro:{id}")
    
    #RN1 – Não é possível definir a situação “aguardando alfândega” ou “finalizado” sem preencher a hora da chegada
    if navio.status in ("aguardando alfândega", "finalizado") and navio.timestampChegada is None:
        return JSONResponse(
            status_code=400,
            content={"errorMessage": "Para esse status, a data de chegada é obrigatória"}
        )
    if navio.timestampChegada is not None and navio.timestampSaida is not None:
        if navio.timestampSaida >= navio.timestampChegada:
            return JSONResponse(
                status_code=400,
                content={"errorMessage": "A data de saída deve ser anterior à data de chegada"}
            )
    if registro_existente is None:
        return JSONResponse(
            status_code=404,
            content={"errorMessage": "Registro não encontrado"}
        )
    dados_existente = json.loads(registro_existente)
    #RN2 – Não é possível alterar os atributos de uma rota que já foi finalizada
    if dados_existente.get("status") == "finalizado":
        return JSONResponse(
            status_code=400,
            content={"errorMessage": "Não é possível atualizar um registro finalizado"}
        )
    dados = navio.model_dump(mode="json") #grava o objeto Navio em um dicionário
    dados["id"] = id # adiciona o ID ao dicionário
    r.set(f"registro:{id}", json.dumps(dados)) #atualiza o registro
    return dados



#DELETE /api/v1/registros/{id:int} ===============================================
@app.delete("/api/v1/registros/{id}")
def excluir_registro(id: int):
    with r.pipeline() as transacao:
        transacao.delete(f"registro:{id}")
        transacao.srem("registros", id)
        excluidos, _ = transacao.execute()

    if not excluidos:
        return JSONResponse(
            status_code=404,
            content={"errorMessage": "Registro não encontrado"}
        )

    return {}


#LISTAGEM Rota GET /api/v1/registros ==============================================
@app.get("/api/v1/registros")
def listar_registros(search: Optional[str] = None):
    if search:
        busca = r.get(f"registro:{search}")
        if busca is None:
            return {"data": []} #se nao encontrar retorna lista vazia
        return {"data": [json.loads(busca)]} #se encontrar retorna o registro na lista
    
    #ordena os ids em ordem crescente e busca os registros no Redis
    ids = sorted(r.smembers("registros"), key=int)
    registros = []
    for id in ids:
        registro_navio = r.get(f"registro:{id}")
        if registro_navio is not None:
            registros.append(json.loads(registro_navio)) #adiciona o registro à lista
    return {"data": registros} #retorna a lista de registros
