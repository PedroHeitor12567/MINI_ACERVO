from datetime import date, timedelta, datetime
from rich.table import Table
from models import Obra, Usuario, Emprestimo
from connect import conectar
from uuid import uuid4
from rich.console import Console

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
            self.estoque[obra.ident] = self.estoque.get(obra.ident, 0) + obra.quantidade
        else:
            self.obras[obra.titulo] = obra
            self.estoque[obra.ident] = obra.quantidade
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
            if self.estoque.get(obra.ident, 0) > 1:
                self.estoque[obra.ident] -= 1
            else:
                del self.estoque[obra.ident]
                del self.obras[obra.titulo]
        return self

    def adicionar(self, obra: Obra):
        """
        Salva uma instância de obra no banco de dados.

        Args:
            obra (Obra): Objeto obra contendo os dados a serem salvos.
        """
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO obras (identificador, titulo, autor, ano, categoria, quantidade, quantidade_disponivel)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (
            str(obra.ident), 
            obra.titulo,
            obra.autor,
            obra.ano,
            obra.categoria,
            obra.quantidade,
            obra.quantidade_disponivel
        ))
        conn.commit()
        cur.close()
        conn.close()
        print("Obra salva com sucesso!")

    def remover(self, id_obra):
        """
        Remove uma obra do banco de dados pelo seu identificador.

        Args:
            id_obra (str): Identificador único da obra a ser removida.
        """
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM obras WHERE identificador = %s;
        """, (str(id_obra),))
        conn.commit()
        cur.close()
        conn.close()
        print("Obra excluída com sucesso.")

    def emprestar(self, emprestimo: Emprestimo):
        """
        Salva uma instância de empréstimo no banco de dados usando o objeto completo.

        Args:
            emprestimo (Emprestimo): Objeto empréstimo contendo os dados a serem salvos.
        """
        
        conn = conectar()
        cur = conn.cursor()
        id_emprestimo = str(uuid4())  # Gerar um novo ID único para o empréstimo

        # Buscar o ID da obra pelo título
        cur.execute("SELECT identificador FROM obras WHERE titulo = %s", (emprestimo.obra.titulo,))
        obra_row = cur.fetchone()
        if not obra_row:
            print(f"Obra '{emprestimo.obra.titulo}' não encontrada.")
            cur.close()
            conn.close()
            return
        id_obra = obra_row[0]

        # Buscar o ID do usuário pelo nome
        cur.execute("SELECT identificador FROM usuarios WHERE nome = %s", (emprestimo.usuario.nome,))
        user_row = cur.fetchone()
        if not user_row:
            print(f"Usuário '{emprestimo.usuario.nome}' não encontrado.")
            cur.close()
            conn.close()
            return
        id_usuario = user_row[0]

        # Inserir empréstimo no banco
        cur.execute("""
            INSERT INTO emprestimos (identificador, obra, usuario, data_retirada, data_prev_devol)
            VALUES (%s, %s, %s, %s, %s);
        """, (
            id_emprestimo,
            id_obra,
            id_usuario,
            emprestimo.data_retirada,
            emprestimo.data_prev_devol
        ))

        conn.commit()
        cur.close()
        conn.close()
        print("Empréstimo salvo com sucesso!")

    def registrar_devolucao_interativa():
        nome = input("Nome do usuário: ").strip()

        try:
            conn = conectar()
            cur = conn.cursor()

            # Busca o usuário pelo nome (case-insensitive)
            cur.execute("SELECT identificador FROM usuarios WHERE LOWER(nome) = LOWER(%s);", (nome,))
            resultado = cur.fetchone()
            if not resultado:
                print("Usuário não encontrado.")
                return
            id_usuario = resultado[0]

            # Busca os empréstimos pendentes com quantidade para atualizar estoque depois
            cur.execute("""
                SELECT e.identificador, o.titulo, e.data_retirada, e.data_prev_devol, o.quantidade, e.obra
                FROM emprestimos e
                JOIN obras o ON e.obra = o.identificador
                WHERE e.usuario = %s AND e.data_devol IS NULL;
            """, (id_usuario,))
            emprestimos = cur.fetchall()

            if not emprestimos:
                print("Nenhum empréstimo em aberto para este usuário.")
                return

            # Exibe os empréstimos pendentes
            table = Table(title="Empréstimos Pendentes")
            table.add_column("Índice", justify="center", style="cyan")
            table.add_column("Obra", justify="left", style="magenta")
            table.add_column("Quantidade", justify="center", style="green")
            table.add_column("Retirada", justify="center", style="yellow")
            table.add_column("Prev. Devolução", justify="center", style="yellow")

            for i, emp in enumerate(emprestimos):
                emp_id, titulo, retirada, prev_devol, quantidade, obra_id = emp
                table.add_row(
                str(i),
                titulo,
                str(quantidade),
                retirada.strftime('%d/%m/%Y'),
                prev_devol.strftime('%d/%m/%Y')
                )
            console = Console()
            console.print(table)

            # Escolhe o empréstimo a ser devolvido
            try:
                i = int(input("Escolha o índice do empréstimo a devolver: "))
                if i < 0 or i >= len(emprestimos):
                    print("Índice inválido.")
                    return
            except ValueError:
                print("Digite um índice válido.")
                return

            id_emprestimo = emprestimos[i][0]  # ID do empréstimo
            obra_id = emprestimos[i][5]

            # Solicita a data de devolução
            data_devol = input("Data da devolução (DD/MM/AAAA): ")
            try:
                data_devol = datetime.strptime(data_devol, "%d/%m/%Y").date()
            except ValueError:
                print("Formato de data inválido.")
                return

            # Atualiza a data de devolução no empréstimo
            cur.execute("""
                UPDATE emprestimos
                SET data_devol = %s
                WHERE identificador = %s;
            """, (data_devol, id_emprestimo))

            # Atualiza a quantidade disponível da obra, somando a quantidade devolvida
            cur.execute("""
                UPDATE obras
                SET quantidade_disponivel = quantidade_disponivel + 1
                WHERE identificador = %s;
            """, (obra_id,))

            conn.commit()
            print("Devolução registrada e estoque atualizado com sucesso!")

        except Exception as e:
            print(f"Erro: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    def renovar(self):
        nome_user = input("Digite seu nome de usuário: ")

        try:
            conn = conectar()
            cur = conn.cursor()

            # Busca o usuário pelo nome (case-insensitive)
            cur.execute("SELECT identificador FROM usuarios WHERE LOWER(nome) = LOWER(%s);", (nome_user,))
            resultado = cur.fetchone()
            if not resultado:
                print("Usuário não encontrado.")
                return
            id_usuario = resultado[0]

            # Busca os empréstimos pendentes com o ID sequencial do empréstimo
            cur.execute("""
                SELECT e.id, o.titulo, e.data_retirada, e.data_prev_devol
                FROM emprestimos e
                JOIN obras o ON e.obra = o.identificador
                WHERE e.usuario = %s AND e.data_devol IS NULL;
            """, (id_usuario,))
            emprestimos = cur.fetchall()

            if not emprestimos:
                print("Nenhum empréstimo em aberto para este usuário.")
                return

            # Exibe os empréstimos pendentes em uma tabela colorida (igual ao registrar_devolucao_interativa)
            table = Table(title="Empréstimos Pendentes")
            table.add_column("Índice", justify="center", style="cyan")
            table.add_column("Obra", justify="left", style="magenta")
            table.add_column("Retirada", justify="center", style="yellow")
            table.add_column("Prev. Devolução", justify="center", style="yellow")

            for i, emp in enumerate(emprestimos):
                emp_id, titulo, retirada, prev_devol = emp
                table.add_row(
                    str(i),
                    titulo,
                    retirada.strftime('%d/%m/%Y'),
                    prev_devol.strftime('%d/%m/%Y')
                )
            console = Console()
            console.print(table)
            try:
                i = int(input("Escolha o índice do empréstimo a revonar: "))
                if i < 0 or i >= len(emprestimos):
                    print("Índice inválido.")
                    return
            except ValueError:
                print("Digite um índice válido.")
                return

            id_emprestimo = emprestimos[i][0]  # Pega o ID sequencial do empréstimo

            data_devol = input("Data da renovação de emprestimo (DD/MM/AAAA): ")
            try:
                data_devol = datetime.strptime(data_devol, "%d/%m/%Y").date()
            except ValueError:
                print("Formato de data inválido.")
                return

            # Atualiza o empréstimo no banco com a data de devolução
            cur.execute("""
                UPDATE emprestimos
                SET data_prev_devol = %s
                WHERE id = %s;
            """, (data_devol, id_emprestimo))
            conn.commit()
            print("Renovação de empréstimo registrada com sucesso!")
        
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            cur.close()
            conn.close()

    def valor_multa(self, emprestimo: Emprestimo, data_ref: date) -> float:
        """
        Calcula o valor da multa com base nos dias de atraso.

        Args:
            emprestimo (Emprestimo): Empréstimo para cálculo.
            data_ref (date): Data de referência para verificar atraso.

        Returns:
            float: Valor da multa (R$5,00 por dia de atraso).
        """
        atraso = emprestimo.dias_atraso(data_ref)
        return float(atraso)

    def relatorio_inventario(self) -> Table:
        """
        Gera uma tabela formatada com todas as obras cadastradas no banco de dados
        e suas quantidades disponíveis em estoque.

        Returns:
            Table: Tabela formatada com dados das obras.
        """
        tabela = Table(title="Inventário do Acervo")
        tabela.add_column("Título", justify="left", style="cyan", no_wrap=True)
        tabela.add_column("Autor", style="magenta")
        tabela.add_column("Ano", justify="center", style="green")
        tabela.add_column("Categoria", justify="left", style="blue")
        tabela.add_column("Quantidade", justify="right", style="yellow")
        tabela.add_column("Disponível", justify="right", style="yellow")

        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute("""
                SELECT titulo, autor, ano, categoria, quantidade, quantidade_disponivel
                FROM obras
                ORDER BY titulo;
            """)

            resultados = cur.fetchall()
            for titulo, autor, ano, categoria, quantidade, quantidade_disponivel in resultados:
                tabela.add_row(titulo, autor, str(ano), categoria, str(quantidade), str(quantidade_disponivel))

        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")

        finally:
            cur.close()
            conn.close()

        return tabela

    def relatorio_debitos(self) -> Table:
        """
        Gera uma tabela com os usuários que devolveram obras com atraso,
        mostrando a multa (R$5 por dia de atraso).
        """
        tabela = Table(title="Usuários com Débitos (Multa por Atraso)")
        tabela.add_column("Usuário", style="yellow")
        tabela.add_column("Multa (R$)", justify="right", style="red")

        try:
            conn = conectar()
            cur = conn.cursor()

            # Busca todos os empréstimos que já foram devolvidos e que tiveram atraso
            cur.execute("""
                SELECT u.nome, e.data_prev_devol, e.data_devol
                FROM emprestimos e
                JOIN usuarios u ON e.usuario = u.identificador
                WHERE e.data_devol IS NOT NULL AND e.data_devol > e.data_prev_devol;
            """)

            resultados = cur.fetchall()

            for nome, data_prev_devol, data_devol in resultados:
                dias_atraso = (data_devol - data_prev_devol).days
                multa = dias_atraso * 5.0
                tabela.add_row(nome, f"{multa:.2f}")

        except Exception as e:
            print(f"Erro ao gerar relatório de débitos: {e}")

        finally:
            if cur: cur.close()
            if conn: conn.close()

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

    def historico_usuario(self, usuario):

        tabela = Table(title=f"Histórico de Empréstimos - {usuario.nome}")
        tabela.add_column("ID", justify="center")
        tabela.add_column("Título", style="cyan")
        tabela.add_column("Data Retirada", justify="center")
        tabela.add_column("Data Prev. Devolução", justify="center")
        tabela.add_column("Data Devolução", justify="center")
        tabela.add_column("Situação", justify="center", style="magenta")

        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute("""
                SELECT e.identificador, o.titulo, e.data_retirada, e.data_prev_devol, e.data_devol
                FROM emprestimos e
                JOIN obras o ON o.identificador = e.obra
                WHERE e.usuario = %s
                ORDER BY e.data_retirada DESC
            """, (str(usuario.ident),))  # <- aqui usamos o UUID, não o objeto

            for row in cur.fetchall():
                emp_id, titulo, retirada, prev_devol, devolucao = row
                status = "Devolvido" if devolucao else "Pendente"
                tabela.add_row(
                    str(emp_id),
                    titulo,
                    retirada.strftime("%d/%m/%Y"),
                    prev_devol.strftime("%d/%m/%Y"),
                    devolucao.strftime("%d/%m/%Y") if devolucao else "-",
                    status
                )

        except Exception as e:
            print(f"Erro ao gerar histórico: {e}")
        finally:
            cur.close()
            conn.close()

        return tabela
    
    def salvar_usuario(self, usuario):
        """
        Salva uma instância de usuário no banco de dados.

        Args:
            usuario (Usuario): Objeto usuário contendo os dados a serem salvos.
        """
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usuarios (identificador, nome, email)
            VALUES (%s, %s, %s);
        """, (
            str(usuario.ident),
            usuario.nome,
            usuario.email
        ))
        conn.commit()
        cur.close()
        conn.close()
        print("Usuário salvo com sucesso!")

    def deletar_user(self,id_user):
        """
        Remove um usuário do banco de dados pelo seu identificador.

        Args:
            id_user (str): Identificador único do usuário a ser removido.
        """
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM usuarios WHERE identificador = %s;
        """, (str(id_user),))
        conn.commit()
        cur.close()
        conn.close()
        print("Usuário excluído com sucesso.")

    def deletar_emprestimos(self, id_obra):
        """
        Remove todos os empréstimos relacionados a uma obra específica.

        Args:
            id_obra (str): Identificador único da obra cujos empréstimos serão removidos.
        """
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM emprestimos WHERE obra = %s;
        """, (str(id_obra),))
        conn.commit()
        cur.close()
        conn.close()
        print("Empréstimos da obra excluídos com sucesso.")