import sqlite3

class Produto:
    def __init__(self, projetista, marca, equipamento, modelo, id=None):
        self.projetista = projetista
        self.marca = marca
        self.equipamento = equipamento
        self.modelo = modelo
        self.id = id

    def adicionar_produto(self):
        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO produtos (projetista, marca, equipamento, modelo) VALUES (?, ?, ?, ?)',
                       (self.projetista, self.marca, self.equipamento, self.modelo))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_produtos():
        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos')
        produtos = cursor.fetchall()
        conn.close()
        return [{'id': produto[0], 'projetista': produto[1], 'marca': produto[2], 'equipamento': produto[3], 'modelo': produto[4]} for produto in produtos]