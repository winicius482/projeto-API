import pytest
import json
from api import api
import sqlite3
import os

@pytest.fixture
def client():
    """Configurar cliente de teste"""
    api.config['TESTING'] = True
    with api.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def limpar_historico():
    """Limpar histórico de edições antes de cada teste"""
    db_path = 'C:/Users/winic/OneDrive/Área de trabalho/projeto API/filmes.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historico_edicoes")
        conn.commit()
        conn.close()
    yield

def test_obter_filmes(client):
    """Teste: obter todos os filmes"""
    response = client.get('/filmes')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    print("✓ GET /filmes - OK")

def test_obter_filme_por_id(client):
    """Teste: obter filme por ID"""
    response = client.get('/filmes/1')
    assert response.status_code in [200, 404]
    assert isinstance(response.json, dict)
    print("✓ GET /filmes/<id> - OK")

def test_adicionar_filme(client):
    """Teste: adicionar novo filme"""
    novo_filme = {
        "titulo": "Teste Filme",
        "diretor": "Diretor Teste",
        "ano": 2025
    }
    response = client.post('/filmes', 
                          data=json.dumps(novo_filme),
                          content_type='application/json')
    assert response.status_code == 201
    assert "sucesso" in response.json.get('mensagem', '').lower()
    print("✓ POST /filmes - OK")

def test_editar_filme(client):
    """Teste: editar filme existente"""
    # Primeiro adicionar um filme
    novo_filme = {
        "titulo": "Filme Original",
        "diretor": "Diretor Original",
        "ano": 2024
    }
    client.post('/filmes', 
               data=json.dumps(novo_filme),
               content_type='application/json')
    
    # Obter ID do primeiro filme
    filmes = client.get('/filmes').json
    if filmes:
        filme_id = filmes[0]['id']
        
        # Editar o filme
        filme_editado = {
            "titulo": "Filme Editado",
            "diretor": "Diretor Editado",
            "ano": 2025
        }
        response = client.put(f'/filmes/{filme_id}',
                             data=json.dumps(filme_editado),
                             content_type='application/json')
        assert response.status_code == 200
        assert "sucesso" in response.json.get('mensagem', '').lower()
        print("✓ PUT /filmes/<id> - OK")

def test_obter_historico_filme(client):
    """Teste: obter histórico de um filme"""
    response = client.get('/filmes/1/historico')
    assert response.status_code in [200, 404]
    assert isinstance(response.json, list)
    print("✓ GET /filmes/<id>/historico - OK")

def test_obter_historico_completo(client):
    """Teste: obter histórico completo"""
    response = client.get('/historico')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    print("✓ GET /historico - OK")

def test_deletar_filme(client):
    """Teste: deletar filme"""
    # Primeiro adicionar um filme
    novo_filme = {
        "titulo": "Filme para Deletar",
        "diretor": "Diretor Temp",
        "ano": 2025
    }
    client.post('/filmes', 
               data=json.dumps(novo_filme),
               content_type='application/json')
    
    # Obter ID do primeiro filme
    filmes = client.get('/filmes').json
    if filmes:
        filme_id = filmes[0]['id']
        
        # Deletar o filme
        response = client.delete(f'/filmes/{filme_id}')
        assert response.status_code == 200
        assert "sucesso" in response.json.get('mensagem', '').lower()
        print("✓ DELETE /filmes/<id> - OK")

def test_filme_nao_encontrado(client):
    """Teste: filme não encontrado"""
    response = client.get('/filmes/99999')
    assert response.status_code == 404
    assert "não encontrado" in response.json.get('erro', '').lower()
    print("✓ Validação: Filme não encontrado - OK")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
