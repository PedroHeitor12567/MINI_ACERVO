import psycopg2 as pg
import os
from dotenv import load_dotenv
import os

load_dotenv()

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
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        return conn
    except pg.DatabaseError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise
conn = conectar()
if conn:
    print("Conexão com o servidor estabelecida com sucesso!")
else:
    print("Falha ao conectar com o servidor.")