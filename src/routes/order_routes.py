from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.models import ItemPedido, Pedido, StatusPedido, Usuario
from src.schemas.schemas import ItemPedidoSchema, PedidoSchema, ResponsePedidoSchema
from src.utils.dependecies import get_db, verificar_token

order_router = APIRouter(prefix="/order", tags=["order"], dependencies=[Depends(verificar_token)])


@order_router.get("/")
async def pedidos():
    return {"mensagem": "Voce acessou a rota de pedidos!"}


@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Annotated[Session, Depends(get_db)]):
    novo_pedido = Pedido(preco=Decimal("0"), usuario_id=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": "Pedido feito com sucesso!"}


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(
    id_pedido: int,
    usuario: Annotated[Usuario, Depends(verificar_token)],
    session: Annotated[Session, Depends(get_db)],
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido nao encontrado")

    if not (usuario.admin or usuario.id == pedido.usuario_id):
        raise HTTPException(status_code=400, detail="Voce nao tem autorizacao para acessar essa rota")

    pedido.status = StatusPedido.CANCELADO
    session.commit()
    return {"mensagem": f"Pedido numero: {id_pedido} cancelado com sucesso.", "pedido": pedido}


@order_router.get("/listar")
async def listar_pedidos(
    usuario: Annotated[Usuario, Depends(verificar_token)],
    session: Annotated[Session, Depends(get_db)],
):
    if not usuario.admin:
        raise HTTPException(status_code=400, detail="Voce nao tem autorizacao para acessar essa rota")

    pedidos = session.query(Pedido).all()
    return {"pedidos": pedidos}


@order_router.post("/pedido/adicionar_item/{id_pedido}")
async def adicionar_item_pedido(
    id_pedido: int,
    item_pedido_schema: ItemPedidoSchema,
    usuario: Annotated[Usuario, Depends(verificar_token)],
    session: Annotated[Session, Depends(get_db)],
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido nao encontrado")
    if not (usuario.admin or usuario.id == pedido.usuario_id):
        raise HTTPException(status_code=400, detail="Voce nao tem autorizacao para executar essa operacao")

    item_pedido = ItemPedido(
        quantidade=item_pedido_schema.quantidade,
        sabor=item_pedido_schema.sabor,
        tamanho=item_pedido_schema.tamanho,
        preco_unitario=item_pedido_schema.preco_unitario,
        pedido_id=id_pedido,
    )

    session.add(item_pedido)
    session.flush()
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco,
    }


@order_router.get("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(
    id_item_pedido: int,
    usuario: Annotated[Usuario, Depends(verificar_token)],
    session: Annotated[Session, Depends(get_db)],
):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()

    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item nao encontrado")

    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido nao encontrado")
    if not (usuario.admin or usuario.id == pedido.usuario_id):
        raise HTTPException(status_code=400, detail="Voce nao tem autorizacao para executar essa operacao")

    session.delete(item_pedido)
    session.flush()
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item removido com sucesso",
        "preco_pedido": pedido.preco,
        "pedido": pedido,
    }


@order_router.post("/pedido/finalizado/{id_pedido}")
async def finalizar_pedido(
    id_pedido: int,
    usuario: Annotated[Usuario, Depends(verificar_token)],
    session: Annotated[Session, Depends(get_db)],
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido nao encontrado")

    if not (usuario.admin or usuario.id == pedido.usuario_id):
        raise HTTPException(status_code=400, detail="Voce nao tem autorizacao para acessar essa rota")

    pedido.status = StatusPedido.FINALIZADO
    session.commit()
    return {"mensagem": f"Pedido numero: {id_pedido} finalizado com sucesso.", "pedido": pedido}


@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(
    id_pedido: int,
    usuario: Annotated[Usuario, Depends(verificar_token)],
    session: Annotated[Session, Depends(get_db)],
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido nao encontrado")

    if not (usuario.admin or usuario.id == pedido.usuario_id):
        raise HTTPException(status_code=400, detail="Voce nao tem autorizacao para acessar essa rota")

    return {
        "quantidade_item_pedido": len(pedido.itens),
        "pedido": pedido,
    }


@order_router.get("/listar/pedidos-usuario", response_model=list[ResponsePedidoSchema])
async def listar_produtos(
    usuario: Annotated[Usuario, Depends(verificar_token)],
    session: Annotated[Session, Depends(get_db)],
):
    pedidos = session.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()
    return pedidos
