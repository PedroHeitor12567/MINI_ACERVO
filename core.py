from models import BaseEntity, Obra, Usuario, Emprestimo

class Acervo:
    def __init__(self):
        self.obras = {}
        self.usuarios = set()
        self.historico_esmprestimos = []
    
    def __iadd__(self, obra: Obra):
        # Validando se obra é mesmo instanciado em Obra
        __valida_obra(obra)

        # Adiciona a obra ao acervo usando o id ou título como chave
        chave = getattr(obra, 'titulo', None)
        if chave:
            self.obras[chave] = obra
            print(f"Obra '{chave}' adicionada ao acervo.")
        else:
            print("Não foi possível adicionar a obra: chave não encontrada.")
        return self

    def __isub__(self, chave_obra):
        # Remove a obra do acervo pela chave (id ou título)
        if chave_obra in self.obras:
            del self.obras[chave_obra]
            print(f"Obra '{chave_obra}' removida do acervo.")
        else:
            print(f"Obra '{chave_obra}' não encontrada no acervo.")
        return self
    
    def adicionar(self, obra):
        __valida_obra(obra)
        

def __valida_obra(self, obra):
        from models import Obra as ObraClass
        if not isinstance(obra, ObraClass):
            raise TypeError(f'O tipo obra ers esperado, porém apareceu {type(obra).__name__}.')