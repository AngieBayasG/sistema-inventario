from flask import Blueprint, render_template, request, redirect, url_for
from database import get_connection
import re

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


# 🔍 VALIDAR EMAIL
def validar_email(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email)


# 📋 LISTAR CLIENTES
@clientes_bp.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes WHERE activo=1")
    clientes = cursor.fetchall()

    conn.close()
    return render_template("clientes/listar.html", clientes=clientes)


# ➕ CREAR CLIENTE
@clientes_bp.route("/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":

        # 🔹 CAPTURAR
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip()
        ci = request.form.get("ci") or None

        # ✅ VALIDACIONES
        if not nombre:
            return render_template("clientes/crear.html", error="❌ Nombre obligatorio")

        if not validar_email(email):
            return render_template("clientes/crear.html", error="❌ Email inválido")

        conn = get_connection()
        cursor = conn.cursor()

        # ✅ CI ÚNICO
        if ci:
            cursor.execute("SELECT id FROM clientes WHERE ci = ?", (ci,))
            if cursor.fetchone():
                conn.close()
                return render_template("clientes/crear.html", error="❌ CI ya registrado")

        # ✅ INSERT
        cursor.execute("""
            INSERT INTO clientes (ci, nombre, email, activo)
            VALUES (?, ?, ?, 1)
        """, (ci, nombre, email))

        conn.commit()
        conn.close()

        return redirect(url_for("clientes.index"))

    return render_template("clientes/crear.html")


# ✏️ EDITAR CLIENTE (MEJORADO)
@clientes_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 OBTENER CLIENTE
    cursor.execute("SELECT * FROM clientes WHERE id=?", (id,))
    cliente = cursor.fetchone()

    if not cliente:
        conn.close()
        return "❌ Cliente no encontrado"

    if request.method == "POST":

        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip()
        ci = request.form.get("ci") or None

        # ✅ VALIDACIONES
        if not nombre:
            conn.close()
            return render_template("clientes/editar.html", cliente=cliente, error="❌ Nombre obligatorio")

        if not validar_email(email):
            conn.close()
            return render_template("clientes/editar.html", cliente=cliente, error="❌ Email inválido")

        # ✅ CI ÚNICO (EXCLUYENDO MISMO ID)
        if ci:
            cursor.execute("""
                SELECT id FROM clientes 
                WHERE ci = ? AND id != ?
            """, (ci, id))
            if cursor.fetchone():
                conn.close()
                return render_template("clientes/editar.html", cliente=cliente, error="❌ CI ya registrado")

        # ✅ UPDATE
        cursor.execute("""
            UPDATE clientes
            SET nombre=?, email=?, ci=?
            WHERE id=?
        """, (nombre, email, ci, id))

        conn.commit()
        conn.close()

        return redirect(url_for("clientes.index"))

    conn.close()
    return render_template("clientes/editar.html", cliente=cliente)


# 🗑️ ELIMINAR (LÓGICO)
@clientes_bp.route("/eliminar/<int:id>")
def eliminar(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clientes
        SET activo = 0
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("clientes.index"))