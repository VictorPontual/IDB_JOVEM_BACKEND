from sqlalchemy.orm import Session
from src.banda_palestrante.model import BandaPalestrante


class RepositorioBandaPalestrante:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, participante: BandaPalestrante) -> BandaPalestrante:
        self.db.add(participante)
        self.db.commit()
        return participante

    def buscar_todos(self) -> list[BandaPalestrante]:
        return self.db.query(BandaPalestrante).all()

    def buscar_por_id(self, participante_id: int) -> BandaPalestrante | None:
        return (
            self.db.query(BandaPalestrante)
            .filter(BandaPalestrante.participante_id == participante_id)
            .first()
        )

    def atualizar(self, participante: BandaPalestrante) -> BandaPalestrante:
        self.db.commit()
        self.db.refresh(participante)
        return participante

    def deletar(self, participante: BandaPalestrante) -> None:
        self.db.delete(participante)
        self.db.commit()