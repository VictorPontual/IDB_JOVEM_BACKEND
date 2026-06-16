from src.banda_palestrante.model import BandaPalestrante
from src.banda_palestrante.repository import RepositorioBandaPalestrante
from src.banda_palestrante.schema import SolicitacaoBandaPalestrante


class ServicoBandaPalestrante:

    def __init__(self, repositorio: RepositorioBandaPalestrante):
        self.repositorio = repositorio

    def criar_banda_palestrante(self, dados: SolicitacaoBandaPalestrante):
        participante = BandaPalestrante(**dados.model_dump())
        return self.repositorio.salvar(participante)

    def listar_banda_palestrantes(self):
        return self.repositorio.buscar_todos()

    def buscar_banda_palestrante(self, participante_id: int):
        participante = self.repositorio.buscar_por_id(participante_id)

        if not participante:
            raise ValueError("Banda ou palestrante não encontrado.")

        return participante

    def atualizar_banda_palestrante(
        self, participante_id: int, dados: SolicitacaoBandaPalestrante
    ):
        participante = self.buscar_banda_palestrante(participante_id)

        for campo, valor in dados.model_dump().items():
            setattr(participante, campo, valor)

        return self.repositorio.atualizar(participante)

    def deletar_banda_palestrante(self, participante_id: int):
        participante = self.buscar_banda_palestrante(participante_id)
        self.repositorio.deletar(participante)
