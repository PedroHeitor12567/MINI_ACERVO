from connect import conectar

def salvar_obra(obra):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO obras (identificador, titulo, autor, ano, categoria, quantidade)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (
        str(obra.id), 
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
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usuarios (identificador, nome, email)
        VALUES (%s, %s, %s);
    """, (
        str(usuario.id),
        usuario.nome,
        usuario.email
    ))
    conn.commit()
    cur.close()
    conn.close()
    print("Usuário salvo com sucesso!")

def salvar_emprestimo(emprestimo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO emprestimo (obra, usuario, data_retirada, data_prev_devol)
        VALUES (%s, %s, %s, %s);
    """, (
        str(emprestimo.obra.id),
        str(emprestimo.usuario.id),
        emprestimo.data_retirada,
        emprestimo.data_prev_devol
    ))
    conn.commit()
    cur.close()
    conn.close()
    print("Empréstimo salvo com sucesso!")

def deletar_obra(id_obra):
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
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM usuarios WHERE identificador = %s;
    """, (str(id_user),))
    conn.commit()
    cur.close()
    conn.close()
    print("Obra excluída com sucesso.")

def deletar_emeprestimos(id_empres):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM emprestimo WHERE obra = %s;
    """, (str(id_empres),))
    conn.commit()
    cur.close()
    conn.close()
    print("Obra excluída com sucesso.")

deletar_user("e82758aa-f765-461f-9de6-8b550cda39ef")