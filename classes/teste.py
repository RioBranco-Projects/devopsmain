import sqlite3

class Teste:
    def __init__(self, produto_id):
        self.produto_id = produto_id

    def realizar_teste(self):
        # Conectar ao banco de dados
        conn = sqlite3.connect('projeto.db')
        cursor = conn.cursor()

        # Buscar todas as avaliações do produto
        cursor.execute('''SELECT p.texto, a.nota, p.peso 
                          FROM avaliacoes a
                          JOIN perguntas p ON a.pergunta_id = p.id
                          WHERE a.produto_id = ?''', (self.produto_id,))
        avaliacoes = cursor.fetchall()
        
        # Calcular a média ponderada
        soma_ponderada = 0
        total_peso = 0
        for avaliacao in avaliacoes:
            nota = avaliacao[1]
            peso = avaliacao[2]
            soma_ponderada += nota * peso
            total_peso += peso
        
        # Garantir que o total de pesos seja maior que zero antes de dividir
        if total_peso > 0:
            media_ponderada = soma_ponderada / total_peso
        else:
            media_ponderada = 0

        conn.close()
        
        # Retorna a média ponderada e os detalhes das avaliações
        return {
            'produto_id': self.produto_id,
            'media_ponderada': media_ponderada,
            'avaliacoes': [{'pergunta': avaliacao[0], 'nota': avaliacao[1], 'peso': avaliacao[2]} for avaliacao in avaliacoes]
        }
