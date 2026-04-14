from database import get_connection

def crear_cliente(nombre, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nombre, email) VALUES (?, ?)", (nombre, email))
    conn.commit()
    conn.close()

def listar_clientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE activo=1")
    data = cursor.fetchall()
    conn.close()
    return data