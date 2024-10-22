import sqlite3
from classes.tema import Tema

class Pergunta:
    def __init__(self, requisito, texto, peso, tema_id, id=None):
        self.requisito = requisito
        self.texto = texto
        self.peso = peso
        self.tema_id = tema_id
        self.id = id

    def adicionar_pergunta(self):
        if not Tema.validar_soma_pesos(self.tema_id, self.peso):
            raise ValueError('A soma dos pesos das perguntas do tema não pode ultrapassar 10')

        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO perguntas (requisito, texto, peso, tema_id) VALUES (?, ?, ?, ?)',
                       (self.requisito, self.texto, self.peso, self.tema_id))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_perguntas():
        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM perguntas')
        perguntas = cursor.fetchall()
        conn.close()
        return [{'id': pergunta[0], 'requisito': pergunta[1], 'texto': pergunta[2], 'peso': pergunta[3], 'tema_id': pergunta[4]} for pergunta in perguntas]

