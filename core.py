from datetime import date, timedelta
from rich.table import Table
from models import Obra, Usuario, Emprestimo

class Acervo:
    """
    Classe responsável por gerenciar o acervo de obras, os usuários
    cadastrados e os históricos de empréstimos.
    """

    def __init__(self):
        """
        Inicializa as estruturas de dados internas do acervo:
        - obras: dicionário {titulo: Obra}
        - usuarios: conjunto de usuários cadastrados
        - estoque: dicionário {id_obra: quantidade disponível}
        - historico_emprestimos: lista de todos os empréstimos realizados
        """
        self.obras = {}
        self.usuarios = set()
        self.estoque = {}
        self.historico_emprestimos = []

    def __iadd__(self, obra: Obra):
        """
        Sobrecarga do operador '+=' para adicionar uma obra ao acervo
        ou incrementar a quantidade no estoque se já existir.

        Args:
            obra (Obra): Obra a ser adicionada.

        Returns:
            Acervo: A própria instância atualizada.
        """
        self._valida_obra(obra)
        if obra.titulo in self.obras:
            self.estoque[obra.id] = self.estoque.get(obra.id, 0) + obra.quantidade
        else:
            self.obras[obra.titulo] = obra
            self.estoque[obra.id] = obra.quantidade
        return self

    def __isub__(self, obra: Obra):
        """
        Sobrecarga do operador '-=' para remover uma unidade da obra
        do acervo ou excluí-la completamente se for o último exemplar.

        Args:
            obra (Obra): Obra a ser removida.

        Returns:
            Acervo: A própria instância atualizada.
        """
        self._valida_obra(obra)
        if obra.titulo in self.obras:
            if self.estoque.get(obra.id, 0) > 1:
                self.estoque[obra.id] -= 1
            else:
                del self.estoque[obra.id]
                del self.obras[obra.titulo]
        return self

    def adicionar(self, obra: Obra):
        """
        Adiciona uma obra ao acervo (forma alternativa ao operador '+=')

        Args:
            obra (Obra): Obra a ser adicionada.
        """
        self += obra

    def remover(self, obra: Obra):
        """
        Remove uma obra do acervo (forma alternativa ao operador '-=')

        Args:
            obra (Obra): Obra a ser removida.
        """
        self -= obra

    def emprestar(self, obra: Obra, usuario: Usuario, dias=7):
        """
        Realiza o empréstimo de uma obra para um usuário, se houver exemplar disponível.

        Args:
            obra (Obra): Obra a ser emprestada.
            usuario (Usuario): Usuário que está pegando emprestado.
            dias (int, opcional): Prazo de empréstimo em dias. Padrão é 7.

        Returns:
            Emprestimo: Objeto representando o empréstimo.

        Raises:
            ValueError: Se a obra estiver indisponível.
        """
        self._valida_obra(obra)
        if self.estoque.get(obra.id, 0) < 1:
            raise ValueError(f"Obra '{obra.titulo}' indisponível.")
        data_retirada = date.today()
        data_prev_devol = data_retirada + timedelta(days=dias)
        emprestimo = Emprestimo(obra, usuario, data_retirada, data_prev_devol)
        self.estoque[obra.id] -= 1
        self.historico_emprestimos.append(emprestimo)
        return emprestimo

    def devolver(self, emprestimo: Emprestimo, data_dev: date):
        """
        Registra a devolução de uma obra e atualiza o estoque.

        Args:
            emprestimo (Emprestimo): Objeto de empréstimo a ser finalizado.
            data_dev (date): Data em que a devolução foi realizada.
        """
        emprestimo.marcar_devolucao(data_dev)
        self.estoque[emprestimo.obra.id] = self.estoque.get(emprestimo.obra.id, 0) + 1

    def renovar(self, emprestimo: Emprestimo, dias_extra: int):
        """
        Prorroga a data prevista de devolução do empréstimo.

        Args:
            emprestimo (Emprestimo): Empréstimo a ser renovado.
            dias_extra (int): Dias adicionais para prorrogação.

        Raises:
            ValueError: Se a nova data for anterior ou igual à data atual de devolução prevista.
        """
        nova_data = emprestimo.data_prev_devol + timedelta(days=dias_extra)
        if nova_data <= emprestimo.data_prev_devol:
            raise ValueError("Nova data deve ser posterior à atual.")
        emprestimo.data_prev_devol = nova_data

    def valor_multa(self, emprestimo: Emprestimo, data_ref: date) -> float:
        """
        Calcula o valor da multa com base nos dias de atraso.

        Args:
            emprestimo (Emprestimo): Empréstimo para cálculo.
            data_ref (date): Data de referência para verificar atraso.

        Returns:
            float: Valor da multa (R$1,00 por dia de atraso).
        """
        atraso = emprestimo.dias_atraso(data_ref)
        return float(atraso)

    def relatorio_inventario(self) -> Table:
        """
        Gera uma tabela formatada com todas as obras cadastradas no acervo e suas quantidades.

        Returns:
            Table: Tabela formatada com dados das obras.
        """
        tabela = Table(title="Inventário do Acervo")
        tabela.add_column("Título", justify="left", style="cyan", no_wrap=True)
        tabela.add_column("Autor", style="magenta")
        tabela.add_column("Ano", justify="center")
        tabela.add_column("Categoria", justify="left")
        tabela.add_column("Quantidade", justify="right")

        for obra in sorted(self.obras.values(), key=lambda o: o.titulo):
            qtd = self.estoque.get(obra.id, 0)
            tabela.add_row(obra.titulo, obra.autor, str(obra.ano), obra.categoria, str(qtd))
        return tabela

    def relatorio_debitos(self) -> Table:
        """
        Gera uma tabela com os usuários que possuem empréstimos em atraso.

        Returns:
            Table: Tabela com nome do usuário e valor da multa.
        """
        tabela = Table(title="Débitos em aberto")
        tabela.add_column("Usuário", style="yellow")
        tabela.add_column("Multa (R$)", justify="right", style="red")

        hoje = date.today()
        multas = {}
        for emprestimo in self.historico_emprestimos:
            if emprestimo.data_devolucao is None:
                atraso = emprestimo.dias_atraso(hoje)
                if atraso > 0:
                    nome = emprestimo.usuario.nome
                    multas[nome] = multas.get(nome, 0) + atraso

        for usuario, valor in multas.items():
            tabela.add_row(usuario, f"{valor:.2f}")
        return tabela

    def historico_usuario(self, usuario: Usuario) -> Table:
        """
        Exibe o histórico de empréstimos de um usuário em formato de tabela.

        Args:
            usuario (Usuario): Usuário para consulta.

        Returns:
            Table: Tabela com obras, datas e status dos empréstimos.
        """
        tabela = Table(title=f"Histórico de {usuario.nome}")
        tabela.add_column("Obra", style="cyan")
        tabela.add_column("Retirada", justify="center")
        tabela.add_column("Prev. Devol.", justify="center")
        tabela.add_column("Devolução", justify="center")
        tabela.add_column("Status", justify="center", style="magenta")

        for emp in self.historico_emprestimos:
            if emp.usuario == usuario:
                status = "Devolvido" if emp.data_devolucao else "Em aberto"
                devol = emp.data_devolucao.strftime('%d/%m/%Y') if emp.data_devolucao else "-"
                tabela.add_row(
                    emp.obra.titulo,
                    emp.data_retirada.strftime('%d/%m/%Y'),
                    emp.data_prev_devol.strftime('%d/%m/%Y'),
                    devol,
                    status
                )
        return tabela

    def _valida_obra(self, obra):
        """
        Verifica se o objeto fornecido é uma instância de Obra.

        Args:
            obra (object): Objeto a ser validado.

        Raises:
            TypeError: Se não for instância de Obra.
        """
        if not isinstance(obra, Obra):
            raise TypeError(f"Esperado Obra, mas veio {type(obra).__name__}")