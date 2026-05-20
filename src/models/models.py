from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship

db = create_engine("sqlite:///database/banco.db")

Base = declarative_base()

class StatusPedido(Enum):
    PENDENTE = "PENDENTE"
    CANCELADO = "CANCELADO"
    FINALIZADO = "FINALIZADO"

class Usuario(Base):
    __tablename__="usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", SQLEnum(StatusPedido), default=StatusPedido.PENDENTE)
    usuario_id = Column("usuario_id", ForeignKey("usuarios.id"))
    preco = Column("preco", Integer, default=0)
    itens = relationship("ItemPedido", cascade="all, delete")

    def __init__(
                self,
                preco: Decimal = Decimal("0"),
                usuario_id: int | None = None,
                status: StatusPedido = StatusPedido.PENDENTE
                ):
        self.status = status
        self.preco = int(preco * 100)
        self.usuario_id = usuario_id

    def calcular_preco(self):
        self.preco = sum(item.preco_unitario * item.quantidade for item in self.itens)



class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Integer)
    pedido_id = Column("pedido_id", ForeignKey("pedidos.id"))

    def __init__(self, sabor: str, preco_unitario: Decimal, pedido_id: int, quantidade: int, tamanho: str):
        self.sabor = sabor
        self.tamanho = tamanho
        self.quantidade = quantidade
        self.preco_unitario = int(preco_unitario * 100)
        self.pedido_id = pedido_id
