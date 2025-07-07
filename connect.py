import psycopg2 as pg

def conectar():
    """
    Estabelece e retorna uma conexão com o banco de dados PostgreSQL.

    Returns:
        connection: Objeto de conexão com o banco.
    
    Raises:
        psycopg2.DatabaseError: Se ocorrer erro na conexão.
    """
    try:
        conn = pg.connect(
            host="localhost",
            database="Acervo",
            user="postgres",
            password="sua senha"
        )
        return conn
    except pg.DatabaseError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise