import re
from datetime import datetime
from connect import conectar
from uuid import uuid4

def salvar_obra(obra):
    """
    Salva uma instância de obra no banco de dados.

    Args:
        obra (Obra): Objeto obra contendo os dados a serem salvos.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO obras (identificador, titulo, autor, ano, categoria, quantidade)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (
        str(obra.ident), 
        obra.titulo,
        obra.autor,
        obra.ano,
        obra.categoria,
        obra.quantidade
    ))
    conn.commit()
    cur.close()
    conn.close()
    print("Obra salva com sucesso!")

def salvar_usuario(usuario):
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

def salvar_emprestimo(emprestimo):
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


def deletar_obra(id_obra):
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

def deletar_user(id_user):
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

def deletar_emprestimos(id_obra):
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
        print("\n--- Empréstimos pendentes ---")
        for i, emp in enumerate(emprestimos):
            emp_id, titulo, retirada, prev_devol, quantidade, obra_id = emp
            print(f"índice {i} | Obra: {titulo} | Quantidade: {quantidade} | Retirada: {retirada.strftime('%d/%m/%Y')} | Prev. Devolução: {prev_devol.strftime('%d/%m/%Y')}")

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
        quantidade_emprestada = emprestimos[i][4]
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
            SET quantidade_disponivel = quantidade_disponivel + %s
            WHERE identificador = %s;
        """, (quantidade_emprestada, obra_id))

        conn.commit()
        print("Devolução registrada e estoque atualizado com sucesso!")

    except Exception as e:
        print(f"Erro: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def renovar_emprestimo():
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

        print("\n--- Empréstimos pendentes ---")
        for i, emp in enumerate(emprestimos):
            emp_id, titulo, retirada, prev_devol = emp
            print(f"[{i}] ID {emp_id} | Obra: {titulo} | Retirada: {retirada.strftime('%d/%m/%Y')} | Prev. Devolução: {prev_devol.strftime('%d/%m/%Y')}")
        
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