from flask import Flask, jsonify, request  # pyright: ignore[reportMissingImports]
import sqlite3
from datetime import datetime

api = Flask(__name__)

db_path = 'C:/Users/winic/OneDrive/Área de trabalho/projeto API/filmes.db'

# Inicializar tabela de histórico
def inicializar_historico():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_edicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filme_id INTEGER NOT NULL,
            titulo_anterior TEXT,
            titulo_novo TEXT,
            diretor_anterior TEXT,
            diretor_novo TEXT,
            ano_anterior INTEGER,
            ano_novo INTEGER,
            data_edicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (filme_id) REFERENCES filmes(id)
        )
    """)
    
    conn.commit()
    conn.close()

# Registrar edição no histórico
def registrar_edicao(filme_id, dados_antigos, dados_novos):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO historico_edicoes 
        (filme_id, titulo_anterior, titulo_novo, diretor_anterior, diretor_novo, ano_anterior, ano_novo, data_edicao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filme_id,
        dados_antigos.get('titulo'),
        dados_novos.get('titulo'),
        dados_antigos.get('diretor'),
        dados_novos.get('diretor'),
        dados_antigos.get('ano'),
        dados_novos.get('ano'),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()

# Inicializar tabela ao iniciar a API
inicializar_historico()

# Consultar todos os filmes
@api.route('/filmes', methods=['GET'])
def obter_filmes():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM filmes")
    dados = cursor.fetchall()
    colunas = [descricao[0] for descricao in cursor.description]
    resultado = [dict(zip(colunas, linha)) for linha in dados]

    conn.close()
    return jsonify(resultado)

# Consultar por ID
@api.route('/filmes/<int:id>', methods=['GET'])
def obter_filme_por_id(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM filmes WHERE id = ?", (id,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return jsonify({
            "id": resultado[0],
            "titulo": resultado[1],
            "diretor": resultado[2],
            "ano": resultado[3]
        })
    else:
        return jsonify({"erro": "Filme não encontrado"}), 404

# Adicionar filme
@api.route('/filmes', methods=['POST'])
def adicionar_filme():
    novo_filme = request.get_json()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO filmes (titulo, diretor, ano) VALUES (?, ?, ?)",
        (novo_filme['titulo'], novo_filme['diretor'], novo_filme['ano'])
    )

    conn.commit()
    conn.close()

    return jsonify({'mensagem': 'Filme adicionado com sucesso!'}), 201

# Editar filme
@api.route('/filmes/<int:id>', methods=['PUT'])
def editar_filme(id):
    filme = request.get_json()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM filmes WHERE id = ?", (id,))
    filme_existente = cursor.fetchone()
    
    if not filme_existente:
        conn.close()
        return jsonify({'erro': 'Filme não encontrado'}), 404

    # Guardar dados antigos para histórico
    dados_antigos = {
        'titulo': filme_existente[1],
        'diretor': filme_existente[2],
        'ano': filme_existente[3]
    }

    cursor.execute("""
        UPDATE filmes
        SET titulo = ?, diretor = ?, ano = ?
        WHERE id = ?
    """, (filme['titulo'], filme['diretor'], filme['ano'], id))

    conn.commit()
    conn.close()

    # Registrar a edição no histórico
    registrar_edicao(id, dados_antigos, filme)

    return jsonify({'mensagem': 'Filme atualizado com sucesso!'})

# Deletar filme
@api.route('/filmes/<int:id>', methods=['DELETE'])
def deletar_filme(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM filmes WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'erro': 'Filme não encontrado'}), 404

    cursor.execute("DELETE FROM filmes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({'mensagem': 'Filme deletado com sucesso!'})

# Obter histórico de um filme
@api.route('/filmes/<int:id>/historico', methods=['GET'])
def obter_historico(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar se o filme existe
    cursor.execute("SELECT * FROM filmes WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'erro': 'Filme não encontrado'}), 404

    # Obter histórico de edições
    cursor.execute("""
        SELECT id, filme_id, titulo_anterior, titulo_novo, diretor_anterior, diretor_novo, 
               ano_anterior, ano_novo, data_edicao 
        FROM historico_edicoes 
        WHERE filme_id = ? 
        ORDER BY data_edicao DESC
    """, (id,))
    
    dados = cursor.fetchall()
    colunas = [descricao[0] for descricao in cursor.description]
    resultado = [dict(zip(colunas, linha)) for linha in dados]
    
    conn.close()
    
    return jsonify(resultado)

# Obter histórico completo de todos os filmes editados
@api.route('/historico', methods=['GET'])
def obter_historico_completo():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filme_id, titulo_anterior, titulo_novo, diretor_anterior, diretor_novo, 
               ano_anterior, ano_novo, data_edicao 
        FROM historico_edicoes 
        ORDER BY data_edicao DESC
    """)
    
    dados = cursor.fetchall()
    colunas = [descricao[0] for descricao in cursor.description]
    resultado = [dict(zip(colunas, linha)) for linha in dados]
    
    conn.close()
    
    return jsonify(resultado)

# Inicia a API (SEMPRE NO FINAL)
api.run(port=5000, host='localhost', debug=True)

    

