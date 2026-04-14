from flask import Blueprint, render_template, request, redirect, url_for
from database import get_connection

pagos_bp = Blueprint("pagos", __name__, url_prefix="/pagos")


# 📋 LISTAR PAGOS + FILTRO
@pagos_bp.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cliente_id = request.args.get("cliente_id")

    if cliente_id:
        cursor.execute("""
            SELECT p.id, c.nombre, p.valor, p.fecha
            FROM pagos p
            JOIN clientes c ON p.cliente_id = c.id
            WHERE p.activo = 1 AND p.cliente_id = ?
        """, (cliente_id,))
    else:
        cursor.execute("""
            SELECT p.id, c.nombre, p.valor, p.fecha
            FROM pagos p
            JOIN clientes c ON p.cliente_id = c.id
            WHERE p.activo = 1
        """)

    pagos = cursor.fetchall()

    cursor.execute("SELECT id, nombre FROM clientes WHERE activo = 1")
    clientes = cursor.fetchall()

    conn.close()

    return render_template(
        "pagos/listar.html",
        pagos=pagos,
        clientes=clientes,
        cliente_id=cliente_id
    )


# ➕ NUEVO PAGO
@pagos_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        try:
            # 🔹 1. CAPTURAR DATOS
            cliente_id = int(request.form["cliente_id"])
            valor = float(request.form["valor"])
            observaciones = request.form.get("observaciones") or ""

        except:
            conn.close()
            return render_template("pagos/crear.html", error="❌ Datos inválidos")

        # 🔹 2. VALIDACIONES

        # ❌ VALOR
        if valor <= 0:
            conn.close()
            return render_template("pagos/crear.html", error="❌ El pago debe ser mayor a 0")

        # ❌ CLIENTE EXISTE
        cursor.execute("SELECT total_deuda FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()

        if not cliente:
            conn.close()
            return render_template("pagos/crear.html", error="❌ Cliente no existe")

        # ❌ NO PAGAR MÁS DE LO QUE DEBE
        if valor > cliente["total_deuda"]:
            conn.close()
            return render_template("pagos/crear.html", error="❌ Está pagando más de lo que debe")

        # 🔹 3. INSERTAR PAGO
        cursor.execute("""
            INSERT INTO pagos (cliente_id, valor, observaciones, activo)
            VALUES (?, ?, ?, 1)
        """, (cliente_id, valor, observaciones))

        # 🔹 4. ACTUALIZAR CLIENTE
        cursor.execute("""
            UPDATE clientes
            SET total_deuda = total_deuda - ?,
                total_pagado = total_pagado + ?
            WHERE id = ?
        """, (valor, valor, cliente_id))

        conn.commit()
        conn.close()

        return redirect(url_for("pagos.index"))

    # 🔹 GET
    cursor.execute("SELECT id, nombre FROM clientes WHERE activo = 1")
    clientes = cursor.fetchall()
    conn.close()

    return render_template("pagos/crear.html", clientes=clientes)


# ❌ ANULAR PAGO (OBLIGATORIO)
@pagos_bp.route("/anular/<int:pago_id>", methods=["POST"])
def anular_pago(pago_id):
    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 Verificar que exista y esté activo
    cursor.execute("""
        SELECT cliente_id, valor
        FROM pagos
        WHERE id = ? AND activo = 1
    """, (pago_id,))
    pago = cursor.fetchone()

    if not pago:
        conn.close()
        return redirect(url_for("pagos.index"))

    cliente_id = pago["cliente_id"]
    valor = pago["valor"]

    # 🔹 DEVOLVER DEUDA
    cursor.execute("""
        UPDATE clientes
        SET total_deuda = total_deuda + ?,
            total_pagado = total_pagado - ?
        WHERE id = ?
    """, (valor, valor, cliente_id))

    # 🔹 ANULAR PAGO
    cursor.execute("""
        UPDATE pagos
        SET activo = 0
        WHERE id = ?
    """, (pago_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("pagos.index"))