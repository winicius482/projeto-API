from flask import Flask, jsonify, request  # pyright: ignore[reportMissingImports]
import sqlite3

api = Flask(__name__)

db_path = 'C:/Users/winic/OneDrive/Área de trabalho/projeto API/filmes.db'

# Consultar todos os filmes
@api.route('/filmes')
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
    conexao = sqlite3.connect(db_path)
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM filmes WHERE id = ?", (id,))
    resultado = cursor.fetchone()
    conexao.close()

    if resultado:
        filme = {
            "id": resultado[0],
            "titulo": resultado[1],
            "diretor": resultado[2],
            "ano": resultado[3]
        }
        return jsonify(filme)
    else:
        return jsonify({"erro": "Filme não encontrado"}), 404

# Editar um filme

@api.route('/filmes/<int:id>', methods=['PUT'])
def editar_filmes_id(id):
    filme_alterado = request.get_json()

    conexao = sqlite3.connect(db_path)
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM filmes WHERE id = ?', (id,))
    resultado = cursor.fetchone()

    if not resultado:
        conexao.close()
        return jsonify({'erro': 'Filme não encontrado'}), 404

    cursor.execute('''
        UPDATE filmes
        SET titulo = ?, diretor = ?, ano = ?
        WHERE id = ?
    ''', (filme_alterado['titulo'], filme_alterado['diretor'], filme_alterado['ano'], id))
    conexao.commit()

    cursor.execute('SELECT * FROM filmes WHERE id = ?', (id,))
    filme_atualizado = cursor.fetchone()
    conexao.close()

    return jsonify({
        'id': filme_atualizado[0],
        'titulo': filme_atualizado[1],
        'diretor': filme_atualizado[2],
        'ano': filme_atualizado[3]
    })

# Adicionar filmes ao banco
@api.route('/filmes', methods=['POST'])
def adicionar_filmes():
    novo_filme = request.get_json()

    conexao = sqlite3.connect(db_path)
    cursor = conexao.cursor()

    cursor.execute('''
        INSERT INTO filmes (titulo, diretor, ano)
        VALUES (?, ?, ?)
    ''', (novo_filme['titulo'], novo_filme['diretor'], novo_filme['ano']))

    conexao.commit()
    conexao.close()

    return jsonify({'mensagem': 'Filme adicionado com sucesso!'}), 201

# Inicia a API
api.run(port=5000, host='localhost', debug=True)



    



    

