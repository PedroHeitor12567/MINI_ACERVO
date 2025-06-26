from models import BaseEntity, Obra, Emprestimo, Usuario

class Acervo:
    def __init__(self):
        self.obras = {}
        self.usuarios = set()
        self.historico_esmprestimos = []