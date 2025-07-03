import uuid
from datetime import datetime as dt

class BaseEntity:
    """Classe base com atributos comuns para todas as entidades."""

    def __init__(self):
        """Inicializa a entidade com um ID único e a data de criação."""
        self.id = self.__gerar_id()
        self.data_criacao = dt.now()

    def __eq__(self, other):
        """Compara duas entidades pelo ID."""
        return isinstance(other, self.__class__) and self.id == other.id

    def __gerar_id(self):
        """Gera um ID único usando UUID4.

        Returns:
            UUID: Identificador único.
        """
        return uuid.uuid4()

    def __hash__(self):
        """Permite que a entidade seja usada em conjuntos e como chave de dicionário."""
        return hash(self.id)

class Obra(BaseEntity):
    """Representa uma obra no acervo (livro, revista, etc)."""

    def __init__(self, titulo, autor, ano, categoria, quantidade=1):
        """
        Args:
            titulo (str): Título da obra.
            autor (str): Autor da obra.
            ano (int): Ano de publicação.
            categoria (str): Categoria/assunto.
            quantidade (int): Número de exemplares disponíveis.
        """
        super().__init__()
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quantidade = quantidade

    def disponivel(self, estoque):
        """Verifica se há pelo menos um exemplar disponível no estoque.

        Args:
            estoque (dict): Dicionário com ID da obra como chave e quantidade como valor.

        Returns:
            bool: True se houver exemplares disponíveis.
        """
        return estoque.get(self.id, 0) > 0

    def __str__(self):
        return f"Título: {self.titulo} \nAno: {self.ano}"

class Usuario(BaseEntity):
    """Representa um usuário que pode pegar obras emprestadas."""

    def __init__(self, nome, email):
        """
        Args:
            nome (str): Nome do usuário.
            email (str): E-mail de contato.
        """
        super().__init__()
        self.nome = nome
        self.email = email

    def __lt__(self, other):
        """Permite ordenação por nome."""
        return self.nome < other.nome

    def __str__(self):
        return f"{self.nome}"

class Emprestimo(BaseEntity):
    """Representa um empréstimo de uma obra feita por um usuário."""

    def __init__(self, obra, usuario, data_retirada, data_prev_devol):
        """
        Args:
            obra (Obra): Obra emprestada.
            usuario (Usuario): Usuário que pegou a obra.
            data_retirada (date): Data em que a obra foi retirada.
            data_prev_devol (date): Data prevista de devolução.
        """
        super().__init__()
        self.obra = obra
        self.usuario = usuario 
        self.data_retirada = data_retirada
        self.data_prev_devol = data_prev_devol

    def marcar_devolucao(self, data_dev_real):
        """Registra a data real de devolução.

        Args:
            data_dev_real (date): Data em que a obra foi devolvida.
        """
        self.data_devol = data_dev_real

    def dias_atraso(self, data_ref):
        """Calcula os dias de atraso com base em uma data de referência.

        Args:
            data_ref (date): Data para comparar com a data prevista de devolução.

        Returns:
            int: Número de dias de atraso. Se não houver atraso, retorna 0.
        """
        if data_ref > self.data_prev_devol:
            return (data_ref - self.data_prev_devol).days
        return 0

    def __str__(self):
        """Representação textual do empréstimo."""
        return (f"Empréstimo de '{self.obra.titulo}' por {self.usuario.nome} "
                f"em {self.data_retirada.strftime('%d/%m/%Y')} "
                f"(Devolução prevista: {self.data_prev_devol.strftime('%d/%m/%Y')})")