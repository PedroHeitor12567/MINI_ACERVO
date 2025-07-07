from models import Obra, Usuario, Emprestimo
from core import Acervo
from datetime import datetime, timedelta, date
import re
from rich.console import Console
from rich.table import Table
from connect import conectar
import uuid, psycopg2

console = Console()

def menu_principal():
    """
    Exibe o menu principal do sistema, permitindo escolher entre as áreas
    do administrador, do usuário, ou sair do sistema.
    """
    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("[1] Área do Administrador")
        print("[2] Área do Usuário")
        print("[0] Sair")
        opcao = input("Escolha: ")

        if opcao == '1':
            menu_admin()
        elif opcao == '2':
            menu_usuario()
        elif opcao == '0':
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")

def menu_admin():
    """
    Área do administrador: gerencia obras, usuários, empréstimos e relatórios.
    Opções disponíveis:
    1 - Cadastrar nova obra
    2 - Remover obra
    3 - Cadastrar novo usuário
    4 - Remover usuário
    5 - Remover todos empréstimos de uma obra
    6 - Ver relatório do inventário
    7 - Ver relatório de débitos
    0 - Voltar ao menu principal
    """
    acervo = Acervo()
    conn = conectar()
    cur = conn.cursor()

    while True:
        print("\n--- ÁREA DO ADMINISTRADOR ---")
        print("[1] Cadastrar nova obra")
        print("[2] Remover obra")
        print("[3] Cadastrar novo usuário")
        print("[4] Remover usuário")
        print("[5] Remover empréstimos de uma obra")
        print("[6] Ver relatório do inventário")
        print("[7] Ver relatório de débitos")
        print("[0] Voltar")
        opcao = input("Escolha: ")

        if opcao == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            try:
                ano = int(input("Ano: "))
                quantidade = int(input("Quantidade: "))
            except ValueError:
                print("Ano e quantidade devem ser números inteiros.")
                continue
            categoria = input("Categoria: ")
            qtd_disponivel = quantidade
            obra = Obra(titulo, autor, ano, categoria, quantidade, qtd_disponivel)
            acervo += obra
            acervo.adicionar(obra)
            print(f"Obra '{titulo}' cadastrada com sucesso!")
        elif opcao == '2':
            titulo = input("Título da obra a remover: ").strip()

            try:
                # Buscar obra pelo título (ignorando maiúsculas/minúsculas)
                cur.execute("""
                    SELECT identificador FROM obras
                    WHERE LOWER(titulo) = LOWER(%s);
                """, (titulo,))
                resultado = cur.fetchone()

                if resultado:
                    obra_id = resultado[0]
                    acervo.remover(obra_id)  # Remove no banco
                    print(f"Obra '{titulo}' removida com sucesso.")
                else:
                    print("Obra não encontrada.")

            except Exception as e:
                print(f"Erro ao remover obra: {e}")
            finally:
                if cur: cur.close()
                if conn: conn.close()
        elif opcao == '3':
            nome = input("Nome: ")
            email = input("Email: ")
            usuario = Usuario(nome, email)
            acervo.salvar_usuario(usuario)
            print(f"Usuário '{nome}' cadastrado com sucesso!")
        elif opcao == '4':
            tabela = Table(title=f"Usuários cadastrados")
            tabela.add_column("Nome", justify="center", style="cyan")
            tabela.add_column("Email", justify="center", style="magenta")

            try:
                conn = conectar()
                cur = conn.cursor()

                cur.execute(""" 
                    SELECT nome, email FROM usuarios;
                """)
                resultados = cur.fetchall()

                if resultados:
                    for row in resultados:
                        nome, email = row
                        tabela.add_row(nome, email)
                    console.print(tabela)
                else:
                    print("Nenhum usuário cadastrado.")
            except Exception as e:
                print(f"Erro ao buscar usuários: {e}")

            nome = input("Nome do usuário a remover: ").strip()
            try:
                # Buscar usuário por nome (ignorando letras maiusculas e minusculas)
                cur.execute("""
                    SELECT identificador FROM usuarios
                    WHERE LOWER(nome) = LOWER(%s);
                """, (nome,))
                resultado = cur.fetchone()


                if resultado:
                    usuario_id = resultado[0]
                    acervo.deletar_user(usuario_id)  # Remove no banco
                    print(f"Usuário {nome} removido com sucesso!")
                else:
                    print("Usuário não encontrado!")

            except Exception as e:
                print(f"Erro ao remover usuário: {e}")
            finally:
                if cur: cur.close()
                if conn: conn.close()

        elif opcao == '5':
            titulo = input("Título da obra para remover empréstimos: ")
            id_obra = buscar_id_obra_por_titulo(titulo)
            try:
                cur.execute("""
                    SELECT obra FROM emprestimos
                    WHERE LOWER(obra) = LOWER(%s)
                """, (id_obra,))
                resultado = cur.fetchone()

                if resultado:
                    emprestimo_id = resultado[0]
                    acervo.deletar_emprestimos(emprestimo_id)  # Remove no banco
                    print(f"Emprestimos da obra {titulo} excluida com sucesso!")
                else:
                    print("Obra não encontrada!")
                
            except Exception as e:
                print(f"Erro ao tentar excluir os emprestimos: {e}")
            finally:
                if cur: cur.close()
                if conn: conn.close()

        elif opcao == '6':
            tabela = acervo.relatorio_inventario()
            console.print(tabela)
        elif opcao == '7':
            tabela = acervo.relatorio_debitos()
            console.print(tabela)
        elif opcao == '0':
            break
        else:
            print("Opção inválida! Tente novamente.")

def menu_usuario():
    """
    Área do usuário: permite realizar empréstimos, devoluções,
    renovações e consulta do histórico de empréstimos.
    Opções disponíveis:
    1 - Realizar empréstimo
    2 - Devolver obra
    3 - Renovar empréstimo
    4 - Ver histórico de empréstimos
    0 - Voltar ao menu principal
    """
    acervo = Acervo()
    while True:
        print("\n--- ÁREA DO USUÁRIO ---")
        print("[1] Realizar empréstimo")
        print("[2] Devolver obra")
        print("[3] Renovar empréstimo")
        print("[4] Ver histórico de empréstimos")
        print("[0] Voltar")
        opcao = input("Escolha: ")

        if opcao == '1':
            nome = input("Nome do usuário: ")
            usuario = encontrar_usuario_por_nome(nome)
            if not usuario:
                print("Usuário não encontrado.")
                continue
            titulo_input = input("Título da obra: ").strip()
            obra = encontrar_obra_por_titulo_iterativo(titulo_input)
            if not obra:
                print("Obra não encontrada.")
                continue
            try:
                dias = int(input("Quantos dias de empréstimo? "))
            except ValueError:
                print("Digite um número válido para os dias.")
                continue
            try:
                hoje = date.today()
                nova_data = hoje + timedelta(days=dias)
                emprestimo = Emprestimo(obra, usuario, hoje, nova_data)
                acervo.emprestar(emprestimo)
                atualizar_quantidade_obra(obra.titulo)
                print("Empréstimo realizado com sucesso!")
            except ValueError as e:
                print(f"Erro: {e}")
        elif opcao == '2':
            acervo.registrar_devolucao_interativa()
        elif opcao == '3':
            acervo.renovar()
        elif opcao == '4':
            nome = input("Nome do usuário: ")
            usuario = encontrar_usuario_por_nome(nome)
            if usuario:
                acervo = Acervo()
                tabela = acervo.historico_usuario(usuario)
                console.print(tabela)
            else:
                print("Usuário não encontrado.")
        elif opcao == '0':
            break
        else:
            print("Opção inválida! Tente novamente.")

def encontrar_usuario_por_nome(nome):
    """
    Busca um usuário pelo nome no banco PostgreSQL, ignorando maiúsculas/minúsculas.

    Args:
        nome (str): Nome do usuário a buscar.

    Returns:
        dict | None: Dicionário com os dados do usuário ou None se não existir.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT identificador, nome, email FROM usuarios WHERE nome = %s", (nome,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        ident, nome_db, email_db = row
        usuario = Usuario(nome=nome_db, email=email_db)
        usuario.ident = ident
        return usuario
    else:
        return None

def encontrar_obra_por_titulo_iterativo(titulo_busca: str):
    """
    Percorre todas as linhas da tabela 'obras', compara o título
    (ignorando maiúsculas/minúsculas) com o parâmetro 'titulo_busca'
    e retorna um objeto Obra caso encontre.

    Args:
        titulo_busca (str): título a procurar.

    Returns:
        Obra | None: a obra encontrada ou None se não existir.
    """
    titulo_busca = titulo_busca.strip().lower()

    try:
        conn = conectar()
        cur = conn.cursor()
        # Busca todas as colunas necessárias de obras
        cur.execute("""
            SELECT identificador, titulo, autor, ano, categoria, quantidade, quantidade_disponivel
              FROM obras;
        """)
        linhas = cur.fetchall()

        for row in linhas:
            id_str, titulo_db, autor, ano, categoria, quantidade, quantidade_disponivel = row
            if titulo_db.lower() == titulo_busca:
                return Obra(
                    titulo=titulo_db,
                    autor=autor,
                    ano=ano,
                    categoria=categoria,
                    quantidade=quantidade,
                    quantidade_disponivel=quantidade_disponivel
                )
        # não encontrou
        return None

    except psycopg2.Error as e:
        print(f"Erro ao ler tabela de obras: {e}")
        return None

    finally:
        if conn:
            conn.close()

def atualizar_quantidade_obra(titulo: str, quantidade_retirada: int = 1):
    """
    Atualiza a quantidade disponível da obra no banco de dados.

    Args:
        titulo (str): Título da obra.
        quantidade_retirada (int): Quantidade a ser subtraída (padrão 1).
    """
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Verifica a quantidade atual
        cursor.execute("""
            SELECT quantidade_disponivel FROM obras
            WHERE LOWER(titulo) = LOWER(%s)
        """, (titulo,))
        resultado = cursor.fetchone()

        if resultado:
            quantidade_atual = resultado[0]
            nova_quantidade = quantidade_atual - quantidade_retirada
            if nova_quantidade < 0:
                raise ValueError("Estoque insuficiente.")

            cursor.execute("""
                UPDATE obras
                SET quantidade_disponivel = %s
                WHERE LOWER(titulo) = LOWER(%s)
            """, (nova_quantidade, titulo))
            conn.commit()
        else:
            print("Obra não encontrada para atualizar quantidade.")
    except Exception as e:
        print(f"Erro ao atualizar quantidade da obra: {e}")
    finally:
        if conn:
            conn.close()

def validar_email(email: str) -> bool:
    """
    Valida se um e-mail tem o formato correto.

    Args:
        email (str): E-mail a ser validado.

    Returns:
        bool: True se o e-mail for válido, False caso contrário.
    """
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return bool(re.match(padrao, email))

def buscar_id_obra_por_titulo(titulo):
    """
    Busca o ID de uma obra pelo seu título.

    Args:
        titulo (str): Título da obra a ser buscada.

    Returns:
        str: Identificador da obra, ou None se não encontrada.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT identificador FROM obras WHERE LOWER(titulo) = LOWER(%s);", (titulo,))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    
    if resultado:
        return resultado[0]
    else:
        return None

if __name__ == "__main__":
    print("=====================================================")
    print("===Bem-vindo ao Sistema de Acervo Bibliográfico 📚===")
    print("=====================================================")
    menu_principal()