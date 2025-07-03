import psycopg2 as pg

def conectar():
    return pg.connect(
        host="localhost",
        database="Acervo",
        user="postgres",
        port="5432",
        password="plph2919"
    )