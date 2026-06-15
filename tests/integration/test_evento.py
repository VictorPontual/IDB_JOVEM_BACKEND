
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.evento.controller import router as evento_router, get_servico
from src.security import obter_usuario_atual
from src.evento.schema import RespostaEvento


EVENTO_BASE = {
    "nome": "Retiro Teen 2025",
    "tipo_evento": "Conferência",
    "descricao": "Retiro anual",
    "local_latitude": -15.7801,
    "local_longitude": -47.9292,
    "data_inicio": "2025-07-10T08:00:00",
    "data_fim": "2025-07-12T18:00:00",
    "link_galeria": None,
    "formulario_link": None,
}

EVENTO_RESPOSTA = {
    **EVENTO_BASE,
    "evento_id": 1,
    "calendario_evento_id": None,
    "nome_local": None,
}

USUARIO_ADMIN = {"sub": "user-123", "realm_access": {"roles": ["admin", "superadmin"]}}


@pytest.fixture
def servico_mock():
    return MagicMock()


@pytest.fixture
def client_evento(servico_mock):
    app = FastAPI()
    app.include_router(evento_router)
    app.dependency_overrides[get_servico] = lambda: servico_mock
    app.dependency_overrides[obter_usuario_atual] = lambda: USUARIO_ADMIN
    with TestClient(app) as c:
        yield c, servico_mock
    app.dependency_overrides.clear()


class TestListarEventos:
    def test_retorna_200_com_lista_vazia(self, client_evento):
        client, servico = client_evento
        servico.listar_evento.return_value = []
        response = client.get("/evento/")
        assert response.status_code == 200
        assert response.json() == []

    def test_retorna_200_com_eventos(self, client_evento):
        client, servico = client_evento
        servico.listar_evento.return_value = [RespostaEvento(**EVENTO_RESPOSTA)]
        response = client.get("/evento/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["nome"] == "Retiro Teen 2025"


class TestBuscarEventoPorId:
    def test_retorna_200_quando_existe(self, client_evento):
        client, servico = client_evento
        servico.buscar_evento.return_value = RespostaEvento(**EVENTO_RESPOSTA)
        response = client.get("/evento/1")
        assert response.status_code == 200
        assert response.json()["evento_id"] == 1

    def test_retorna_404_quando_nao_existe(self, client_evento):
        client, servico = client_evento
        servico.buscar_evento.side_effect = ValueError("Evento não encontrado")
        response = client.get("/evento/999")
        assert response.status_code == 404


PAYLOADS_EVENTO_VALIDOS = [
    pytest.param({**EVENTO_BASE}, id="payload_completo"),
    pytest.param(
        {**EVENTO_BASE, "descricao": None, "link_galeria": None},
        id="payload_sem_campos_opcionais",
    ),
    pytest.param(
        {**EVENTO_BASE, "nome": "Encontro Jovem",
         "formulario_link": "https://forms.google.com/123"},
        id="payload_com_formulario",
    ),
]


@pytest.mark.parametrize("payload", PAYLOADS_EVENTO_VALIDOS)
def test_criar_evento_payload_valido(client_evento, payload):
    client, servico = client_evento
    servico.criar_evento.return_value = RespostaEvento(
        **{**payload, "evento_id": 1, "calendario_evento_id": None, "nome_local": None}
    )
    response = client.post("/evento/", json=payload)
    assert response.status_code == 201
    assert response.json()["nome"] == payload["nome"]


PAYLOADS_EVENTO_INVALIDOS = [
    pytest.param({}, id="payload_vazio"),
    pytest.param({"nome": "Evento X"}, id="sem_coordenadas_e_datas"),
    pytest.param({**EVENTO_BASE, "local_latitude": "invalido"}, id="latitude_invalida"),
    pytest.param({**EVENTO_BASE, "data_inicio": "data-invalida"}, id="data_invalida"),
    pytest.param(
        {k: v for k, v in EVENTO_BASE.items() if k != "tipo_evento"},
        id="sem_tipo_evento",
    ),
    pytest.param(
        {**EVENTO_BASE, "tipo_evento": "Retiro"},
        id="tipo_evento_invalido",
    ),
]


@pytest.mark.parametrize("payload", PAYLOADS_EVENTO_INVALIDOS)
def test_criar_evento_payload_invalido_retorna_422(client_evento, payload):
    client, _ = client_evento
    response = client.post("/evento/", json=payload)
    assert response.status_code == 422


class TestDeletarEvento:
    def test_retorna_204_quando_existe(self, client_evento):
        client, servico = client_evento
        servico.deletar_evento.return_value = None
        response = client.delete("/evento/1")
        assert response.status_code == 204

    def test_retorna_404_quando_nao_existe(self, client_evento):
        client, servico = client_evento
        servico.deletar_evento.side_effect = ValueError("Evento não encontrado")
        response = client.delete("/evento/999")
        assert response.status_code == 404


PARTICIPANTE_RESPOSTA = {
    "participante_id": 1,
    "nome": "DJ Fulano",
    "link_foto": "https://exemplo.com/foto.jpg",
    "profissao": "Palestrante",
}


class TestListarParticipantesEvento:
    def test_retorna_200_com_lista(self, client_evento):
        client, servico = client_evento
        servico.listar_participantes.return_value = [PARTICIPANTE_RESPOSTA]
        response = client.get("/evento/1/participantes")
        assert response.status_code == 200
        assert response.json()[0]["participante_id"] == 1
        servico.listar_participantes.assert_called_once_with(1)

    def test_retorna_200_com_lista_vazia(self, client_evento):
        client, servico = client_evento
        servico.listar_participantes.return_value = []
        response = client.get("/evento/1/participantes")
        assert response.status_code == 200
        assert response.json() == []

    def test_retorna_404_quando_evento_nao_existe(self, client_evento):
        client, servico = client_evento
        servico.listar_participantes.side_effect = ValueError("Evento não encontrado.")
        response = client.get("/evento/999/participantes")
        assert response.status_code == 404


class TestAdicionarParticipanteEvento:
    def test_retorna_201_quando_vincula(self, client_evento):
        client, servico = client_evento
        servico.adicionar_participante.return_value = PARTICIPANTE_RESPOSTA
        response = client.post("/evento/1/participantes/1")
        assert response.status_code == 201
        assert response.json()["participante_id"] == 1
        servico.adicionar_participante.assert_called_once_with(1, 1)

    def test_retorna_400_quando_participante_nao_existe(self, client_evento):
        client, servico = client_evento
        servico.adicionar_participante.side_effect = ValueError(
            "Banda ou palestrante não encontrado."
        )
        response = client.post("/evento/1/participantes/999")
        assert response.status_code == 400

    def test_retorna_400_quando_vinculo_duplicado(self, client_evento):
        client, servico = client_evento
        servico.adicionar_participante.side_effect = ValueError(
            "Participante já vinculado a este evento."
        )
        response = client.post("/evento/1/participantes/1")
        assert response.status_code == 400


class TestRemoverParticipanteEvento:
    def test_retorna_204_quando_desvincula(self, client_evento):
        client, servico = client_evento
        servico.remover_participante.return_value = None
        response = client.delete("/evento/1/participantes/1")
        assert response.status_code == 204
        servico.remover_participante.assert_called_once_with(1, 1)

    def test_retorna_404_quando_vinculo_nao_existe(self, client_evento):
        client, servico = client_evento
        servico.remover_participante.side_effect = ValueError(
            "Vínculo entre evento e participante não encontrado."
        )
        response = client.delete("/evento/1/participantes/999")
        assert response.status_code == 404