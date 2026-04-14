import sqlite3

DB_NAME = "inventario.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # 👤 CLIENTES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ci TEXT UNIQUE,
        nombre TEXT NOT NULL,
        direccion TEXT,
        telefono TEXT,
        email TEXT,
        total_deuda REAL DEFAULT 0,
        total_pagado REAL DEFAULT 0,
        activo INTEGER DEFAULT 1
    )
    """)

    # 📦 PRODUCTOS (🔥 AQUÍ VA STOCK MÍNIMO)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_barras TEXT UNIQUE,
        descripcion TEXT NOT NULL,
        stock_minimo INTEGER DEFAULT 5,
        stock_actual INTEGER DEFAULT 0,
        precio REAL NOT NULL,
        tiene_iva INTEGER DEFAULT 1,
        activo INTEGER DEFAULT 1
    )
    """)

    # =========================
    # 🛒 VENTAS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        subtotal REAL DEFAULT 0,
        iva REAL DEFAULT 0,
        total REAL DEFAULT 0,
        abono REAL DEFAULT 0,
        saldo REAL DEFAULT 0,
        observaciones TEXT,
        activo INTEGER DEFAULT 1,
        FOREIGN KEY(cliente_id) 
            REFERENCES clientes(id)
            ON DELETE RESTRICT
    )
    """)

    # =========================
    # 📄 DETALLE DE VENTA
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL CHECK(cantidad > 0),
        precio REAL NOT NULL CHECK(precio >= 0),
        iva REAL DEFAULT 0,
        total_linea REAL NOT NULL,
        FOREIGN KEY(venta_id) 
            REFERENCES ventas(id)
            ON DELETE CASCADE,
        FOREIGN KEY(producto_id) 
            REFERENCES productos(id)
            ON DELETE RESTRICT
    )
    """)

    # =========================
    # 💰 PAGOS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        cliente_id INTEGER NOT NULL,
        valor REAL NOT NULL CHECK(valor > 0),
        observaciones TEXT,
        activo INTEGER DEFAULT 1,
        FOREIGN KEY(cliente_id) 
            REFERENCES clientes(id)
            ON DELETE RESTRICT
    )
    """)

    # =========================
    # 🔐 USUARIOS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # =========================
    # 📈 ÍNDICES (MEJOR RENDIMIENTO)
    # =========================
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente ON ventas(cliente_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_producto ON detalle_venta(producto_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pago_cliente ON pagos(cliente_id)")

    # =========================
    # 👤 ADMIN
    # =========================
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", ("admin",))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO usuarios (username, password)
            VALUES (?, ?)
        """, ("admin", "1234"))

    conn.commit()
    conn.close()