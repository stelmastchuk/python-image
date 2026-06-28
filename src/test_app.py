import pytest

import main as app_module


@pytest.fixture
def client():
    """Cliente de teste do Flask com as listas globais zeradas a cada teste."""
    app_module.app.config["TESTING"] = True
    app_module.times.clear()
    app_module.campeonatos.clear()

    with app_module.app.test_client() as client:
        yield client

    app_module.times.clear()
    app_module.campeonatos.clear()


# ---------------------------------------------------------------------------
# Rota "/"
# ---------------------------------------------------------------------------

def test_index_retorna_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_renderiza_html(client):
    response = client.get("/")
    assert b"<html" in response.data.lower()


# ---------------------------------------------------------------------------
# Rota "/times"
# ---------------------------------------------------------------------------

def test_get_times_inicialmente_vazio(client):
    response = client.get("/times")
    assert response.status_code == 200
    assert response.get_json() == []


def test_post_time_adiciona_e_retorna_mensagem(client):
    payload = {"nome": "Flamengo"}
    response = client.post("/times", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"message": "Time adicionado com sucesso!"}


def test_post_time_e_listado_no_get(client):
    payload = {"nome": "Palmeiras"}
    client.post("/times", json=payload)

    response = client.get("/times")
    data = response.get_json()

    assert len(data) == 1
    assert data[0] == payload


def test_post_varios_times_acumula_na_lista(client):
    client.post("/times", json={"nome": "Flamengo"})
    client.post("/times", json={"nome": "Palmeiras"})

    response = client.get("/times")
    data = response.get_json()

    assert len(data) == 2
    nomes = [t["nome"] for t in data]
    assert "Flamengo" in nomes
    assert "Palmeiras" in nomes


# ---------------------------------------------------------------------------
# Rota "/campeonatos"
# ---------------------------------------------------------------------------

def test_get_campeonatos_inicialmente_vazio(client):
    response = client.get("/campeonatos")
    assert response.status_code == 200
    assert response.get_json() == []


def test_post_campeonato_adiciona_e_retorna_mensagem(client):
    payload = {"nome": "Brasileirao"}
    response = client.post("/campeonatos", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"message": "Campeonato adicionado com sucesso!"}


def test_post_campeonato_e_listado_no_get(client):
    payload = {"nome": "Copa do Brasil"}
    client.post("/campeonatos", json=payload)

    response = client.get("/campeonatos")
    data = response.get_json()

    assert len(data) == 1
    assert data[0] == payload


# ---------------------------------------------------------------------------
# Isolamento entre testes (garante que o fixture realmente limpa o estado)
# ---------------------------------------------------------------------------

def test_estado_e_resetado_entre_testes(client):
    """Se o fixture não limpasse as listas, este teste falharia
    por causa dos dados inseridos nos testes anteriores."""
    assert app_module.times == []
    assert app_module.campeonatos == []


# ---------------------------------------------------------------------------
# Rota inexistente / 404
# ---------------------------------------------------------------------------

def test_rota_inexistente_retorna_404(client):
    response = client.get("/rota-que-nao-existe")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Pagina nao encontrada"}