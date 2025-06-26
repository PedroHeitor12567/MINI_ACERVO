import uuid
from datetime import datetime as dt

class BaseEntity:
    def __init__(self):
        self.id = self._gerar_id()
        self.data_criacao = dt.now()
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def _gerar_id(self):
        return uuid.uuid4()

    def __hash__(self):
        return hash(self.id)

class Obra(BaseEntity):
    def __init__(self, titulo, autor, ano, categoria, quantidade=1):
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quatidade = quantidade
    
    def disponivel(self, estoque):
        return estoque.get(self.id, 0) > 0
    
    def __str__(self):
        return f"Título: {self.titulo} \nAno: {self.ano}"
    
class Usuario(BaseEntity):
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email

    def __lt__(self, other):
        return self.nome < other.nome
    
    def __str__(self):
        return f"{self.nome}"

class Emprestimo(BaseEntity):
    def __init__(self, obra, ususario, data_retirada, data_prev_devol):
        super.__init__()
        self.obra = obra
        self.ususario = ususario
        self.data_retirada = data_retirada
        self.data_prev_devol = data_prev_devol
    
    def marcar_devolucao(self, data_dev_real):
        self.data_devol = data_dev_real
    
    def dias_atraso(self, data_ref):
        if self.data_ref > (self.data_prev_devol):
            return (self.data_ref - self.data_prev_devol).days
        return 0
    