import psycopg2 as pg

def conectar():
    return pg.connect(
        host="localhost",
        database="Acervo",
        user="postgres",
        password="plph2919"  
    )