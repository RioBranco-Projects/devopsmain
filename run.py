from flask import Flask, jsonify, request
import sqlite3
import matplotlib.pyplot as plt

app = Flask(__name__)

# Conexão com o banco de dados
def conectar_bd():
    return sqlite3.connect('projeto.db')

# Inicializar o banco de dados
def inicializar_banco():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS temas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS perguntas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        requisito TEXT NOT NULL,
                        texto TEXT NOT NULL,
                        peso INTEGER NOT NULL,
                        tema_id INTEGER,
                        FOREIGN KEY (tema_id) REFERENCES temas (id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        projetista TEXT NOT NULL,
                        marca TEXT NOT NULL,
                        equipamento TEXT NOT NULL,
                        modelo TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS avaliacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        produto_id INTEGER,
                        pergunta_id INTEGER,
                        nota INTEGER NOT NULL,
                        FOREIGN KEY (produto_id) REFERENCES produtos (id),
                        FOREIGN KEY (pergunta_id) REFERENCES perguntas (id))''')

    conn.commit()
    conn.close()

# Inicializando o banco de dados
inicializar_banco()

# CRUD para Temas
@app.route('/temas', methods=['POST'])
def adicionar_tema():
    dados = request.json
    nome = dados.get('nome')
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO temas (nome) VALUES (?)', (nome,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Tema adicionado com sucesso!'})

@app.route('/temas', methods=['GET'])
def listar_temas():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM temas')
    temas = cursor.fetchall()
    conn.close()
    return jsonify([{'id': tema[0], 'nome': tema[1]} for tema in temas])

@app.route('/temas/<int:tema_id>', methods=['DELETE'])
def excluir_tema(tema_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM temas WHERE id = ?', (tema_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Tema excluído com sucesso!'})

# CRUD para Perguntas
@app.route('/perguntas', methods=['POST'])
def adicionar_pergunta():
    dados = request.json
    requisito = dados.get('requisito')
    texto = dados.get('texto')
    peso = dados.get('peso')
    tema_id = dados.get('tema_id')

    # Verificar a soma dos pesos das perguntas já existentes para o tema
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT peso FROM perguntas WHERE tema_id = ?', (tema_id,))
    pesos_existentes = cursor.fetchall()

    soma_pesos = sum(peso_existente[0] for peso_existente in pesos_existentes) + peso

    # Verificar se a soma dos pesos ultrapassa 10
    if soma_pesos > 10:
        return jsonify({'error': 'A soma dos pesos das perguntas do tema não pode ultrapassar 10'}), 400

    # Inserir a nova pergunta se o peso for válido
    cursor.execute('INSERT INTO perguntas (requisito, texto, peso, tema_id) VALUES (?, ?, ?, ?)',
                   (requisito, texto, peso, tema_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Pergunta adicionada com sucesso!'})

@app.route('/perguntas', methods=['GET'])
def listar_perguntas():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM perguntas')
    perguntas = cursor.fetchall()
    conn.close()
    return jsonify([{'id': pergunta[0], 'requisito': pergunta[1], 'texto': pergunta[2], 'peso': pergunta[3], 'tema_id': pergunta[4]} for pergunta in perguntas])

# CRUD para Produtos
@app.route('/produtos', methods=['POST'])
def adicionar_produto():
    dados = request.json
    projetista = dados.get('projetista')
    marca = dados.get('marca')
    equipamento = dados.get('equipamento')
    modelo = dados.get('modelo')
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (projetista, marca, equipamento, modelo) VALUES (?, ?, ?, ?)',
                   (projetista, marca, equipamento, modelo))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Produto adicionado com sucesso!'})

@app.route('/produtos', methods=['GET'])
def listar_produtos():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    conn.close()
    return jsonify([{'id': produto[0], 'projetista': produto[1], 'marca': produto[2], 'equipamento': produto[3], 'modelo': produto[4]} for produto in produtos])

# Avaliação de Produtos e Gráficos
@app.route('/produtos/<int:produto_id>/avaliar', methods=['POST'])
def avaliar_produto(produto_id):
    dados = request.json
    conn = conectar_bd()
    cursor = conn.cursor()

    for avaliacao in dados.get('avaliacoes'):
        pergunta_id = avaliacao['pergunta_id']
        nota = avaliacao['nota']
        cursor.execute('INSERT INTO avaliacoes (produto_id, pergunta_id, nota) VALUES (?, ?, ?)',
                       (produto_id, pergunta_id, nota))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Avaliação registrada com sucesso!'})

@app.route('/produtos/<int:produto_id>/grafico', methods=['GET'])
def gerar_grafico(produto_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''SELECT p.texto, a.nota FROM avaliacoes a
                      JOIN perguntas p ON a.pergunta_id = p.id
                      WHERE a.produto_id = ?''', (produto_id,))
    avaliacoes = cursor.fetchall()

    perguntas = [avaliacao[0] for avaliacao in avaliacoes]
    notas = [avaliacao[1] for avaliacao in avaliacoes]

    plt.bar(perguntas, notas)
    plt.xlabel('Perguntas')
    plt.ylabel('Notas')
    plt.title('Avaliação do Produto')
    plt.savefig('grafico_produto.png')
    plt.close()

    return jsonify({'message': 'Gráfico gerado e salvo como grafico_produto.png'})

# Filtro de Produtos e Rankeamento
@app.route('/produtos/filtro', methods=['GET'])
def filtrar_produtos():
    tema_id = request.args.get('tema_id')
    min_nota = request.args.get('min_nota', 0)
    max_nota = request.args.get('max_nota', 10)

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''SELECT p.id, p.projetista, p.marca, p.equipamento, AVG(a.nota) as media_nota
                      FROM produtos p
                      JOIN avaliacoes a ON p.id = a.produto_id
                      WHERE a.nota BETWEEN ? AND ?
                      GROUP BY p.id''', (min_nota, max_nota))
    produtos = cursor.fetchall()
    conn.close()

    return jsonify([{'id': produto[0], 'projetista': produto[1], 'marca': produto[2], 'equipamento': produto[3], 'media_nota': produto[4]} for produto in produtos])

@app.route('/produtos/ranking', methods=['GET'])
def rankear_produtos():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''SELECT p.id, p.projetista, p.marca, p.equipamento, AVG(a.nota) as media_nota
                      FROM produtos p
                      JOIN avaliacoes a ON p.id = a.produto_id
                      GROUP BY p.id
                      ORDER BY media_nota DESC''')
    produtos = cursor.fetchall()
    conn.close()

    return jsonify([{'id': produto[0], 'projetista': produto[1], 'marca': produto[2], 'equipamento': produto[3], 'media_nota': produto[4]} for produto in produtos])


if __name__ == '__main__':
    app.run(debug=True)
