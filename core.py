from models import BaseEntity, Obra, Usuario, Emprestimo  
from repositorio import salvar_obra, salvar_usuario, salvar_emprestimo
from datetime import date

class Acervo:
    """Gerencia o acervo de obras, usuários e histórico de empréstimos."""

    def __init__(self):
        """Inicializa as estruturas internas do acervo."""
        self.obras = {}
        self.usuarios = set()
        self.historico_emprestimos = []

    def __iadd__(self, obra: Obra):
        """Adiciona uma obra ao acervo usando o operador '+='.

        Args:
            obra (Obra): Obra a ser adicionada.

        Returns:
            Acervo: A própria instância atualizada.
        """
        self.__valida_obra(obra)
        chave = getattr(obra, 'titulo', None)
        if chave:
            self.obras[chave] = obra
            print(f"Obra '{chave}' adicionada ao acervo.")
        else:
            print("Não foi possível adicionar a obra: chave não encontrada.")
        return self

    def __isub__(self, chave_obra):
        """Remove uma obra do acervo usando o operador '-='.

        Args:
            chave_obra (str): Título ou chave identificadora da obra.

        Returns:
            Acervo: A própria instância atualizada.
        """
        if chave_obra in self.obras:
            del self.obras[chave_obra]
            print(f"Obra '{chave_obra}' removida do acervo.")
        else:
            print(f"Obra '{chave_obra}' não encontrada no acervo.")
        return self

    def adicionar(self, obra):
        """Adiciona uma obra ao acervo (método alternativo ao '+=').

        Args:
            obra (Obra): Obra a ser adicionada.
        """
        self.__valida_obra(obra)
        chave = obra.titulo
        self.obras[chave] = obra
        print(f"Obra '{chave}' adicionada ao acervo (via método adicionar).")

    def __valida_obra(self, obra):
        """Valida se o objeto passado é uma instância da classe Obra.

        Args:
            obra (object): Objeto a ser validado.

        Raises:
            TypeError: Se o objeto não for uma instância de Obra.
        """
        if not isinstance(obra, Obra):
            raise TypeError(f'O tipo Obra era esperado, mas foi recebido: {type(obra).__name__}')

# Teste do sistema
livro = Obra("Dom Casmurro", "Machado de Assis", 1899, "Romance", 3)
usuario = Usuario("Maria", "maria@email.com")
emprestimo = Emprestimo(livro, usuario, date.today(), date(2025, 7, 15))

# Salvando no repositório
salvar_obra(livro)
salvar_usuario(usuario)
salvar_emprestimo(emprestimo)