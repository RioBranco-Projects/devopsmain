import sqlite3

class Tema:
    def __init__(self, nome, id=None):
        self.nome = nome
        self.id = id

    @staticmethod
    def adicionar_tema(nome):
        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO temas (nome) VALUES (?)', (nome,))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_temas():
        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM temas')
        temas = cursor.fetchall()
        conn.close()
        return [{'id': tema[0], 'nome': tema[1]} for tema in temas]

    @staticmethod
    def excluir_tema(tema_id):
        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM temas WHERE id = ?', (tema_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def validar_soma_pesos(tema_id, novo_peso):
        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()
        cursor.execute('SELECT peso FROM perguntas WHERE tema_id = ?', (tema_id,))
        pesos_existentes = cursor.fetchall()
        soma_pesos = sum(peso_existente[0] for peso_existente in pesos_existentes) + novo_peso

        if soma_pesos > 10:
            return False
        return True
