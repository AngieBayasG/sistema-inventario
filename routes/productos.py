from flask import Blueprint, render_template, request, redirect, url_for
from database import get_connection

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")


# 📋 LISTAR PRODUCTOS
@productos_bp.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, descripcion, precio, stock_actual, stock_minimo
        FROM productos
        WHERE activo = 1
    """)

    productos = cursor.fetchall()
    conn.close()

    return render_template("productos/listar.html", productos=productos)


# ➕ CREAR PRODUCTO
@productos_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():

    if request.method == "POST":

        # 🔹 CAPTURAR DATOS
        descripcion = request.form["descripcion"].strip()
        precio = float(request.form["precio"])
        stock = int(request.form["stock_actual"])
        stock_minimo = int(request.form["stock_minimo"])   # 🔥 NUEVO
        codigo = request.form.get("codigo_barras") or None

        # 🔹 VALIDACIONES
        if not descripcion:
            return render_template("productos/crear.html", error="❌ Descripción requerida")

        if precio < 0:
            return render_template("productos/crear.html", error="❌ Precio no puede ser negativo")

        if stock < 0:
            return render_template("productos/crear.html", error="❌ Stock inválido")

        if stock_minimo < 0:
            return render_template("productos/crear.html", error="❌ Stock mínimo inválido")

        # 🔹 CONEXIÓN DB
        conn = get_connection()
        cursor = conn.cursor()

        # ✅ VALIDAR CÓDIGO ÚNICO
        if codigo:
            cursor.execute("SELECT id FROM productos WHERE codigo_barras = ?", (codigo,))
            if cursor.fetchone():
                conn.close()
                return render_template("productos/crear.html", error="❌ Código de barras ya existe")

        # 🔹 INSERTAR
        cursor.execute("""
            INSERT INTO productos (codigo_barras, descripcion, precio, stock_actual, stock_minimo, activo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (codigo, descripcion, precio, stock, stock_minimo))

        conn.commit()
        conn.close()

        return redirect(url_for("productos.index"))

    return render_template("productos/crear.html")


# ✏️ EDITAR PRODUCTO
@productos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        descripcion = request.form["descripcion"].strip()
        precio = float(request.form["precio"])
        stock = int(request.form["stock_actual"])
        stock_minimo = int(request.form["stock_minimo"])  # 🔥 NUEVO
        codigo = request.form.get("codigo_barras") or None

        # 🔹 VALIDACIONES
        if not descripcion:
            conn.close()
            return render_template("productos/editar.html", error="❌ Descripción requerida")

        if precio < 0:
            conn.close()
            return render_template("productos/editar.html", error="❌ Precio inválido")

        if stock < 0:
            conn.close()
            return render_template("productos/editar.html", error="❌ Stock inválido")

        if stock_minimo < 0:
            conn.close()
            return render_template("productos/editar.html", error="❌ Stock mínimo inválido")

        # ✅ VALIDAR CÓDIGO ÚNICO
        if codigo:
            cursor.execute("""
                SELECT id FROM productos
                WHERE codigo_barras = ? AND id != ?
            """, (codigo, id))

            if cursor.fetchone():
                conn.close()
                return render_template("productos/editar.html", error="❌ Código ya existe")

        # 🔹 UPDATE
        cursor.execute("""
            UPDATE productos
            SET descripcion = ?, precio = ?, stock_actual = ?, stock_minimo = ?, codigo_barras = ?
            WHERE id = ?
        """, (descripcion, precio, stock, stock_minimo, codigo, id))

        conn.commit()
        conn.close()

        return redirect(url_for("productos.index"))

    # 🔹 GET
    cursor.execute("SELECT * FROM productos WHERE id = ?", (id,))
    producto = cursor.fetchone()
    conn.close()

    return render_template("productos/editar.html", producto=producto)


# 🗑️ ELIMINAR
@productos_bp.route("/eliminar/<int:id>")
def eliminar(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE productos
        SET activo = 0
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("productos.index"))