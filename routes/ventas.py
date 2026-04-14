from flask import Blueprint, render_template, request, redirect, url_for
from database import get_connection

ventas_bp = Blueprint('ventas', __name__, url_prefix="/ventas")


# 🔹 LISTAR VENTAS
@ventas_bp.route("/", methods=["GET"])
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cliente_id = request.args.get("cliente_id")

    if cliente_id:
        cursor.execute("""
            SELECT v.id, c.nombre AS cliente, v.total, v.fecha
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            WHERE v.activo = 1 AND v.cliente_id = ?
        """, (cliente_id,))
    else:
        cursor.execute("""
            SELECT v.id, c.nombre AS cliente, v.total, v.fecha
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            WHERE v.activo = 1
        """)

    ventas = cursor.fetchall()

    cursor.execute("SELECT id, nombre FROM clientes WHERE activo = 1")
    clientes = cursor.fetchall()

    conn.close()

    return render_template(
        "ventas/listar.html",
        ventas=ventas,
        clientes=clientes,
        cliente_id=cliente_id
    )


# 🔹 CREAR NUEVA VENTA
@ventas_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_venta():
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        # 🔴 1. VALIDAR CLIENTE
        cliente_id = request.form.get("cliente_id")

        if not cliente_id:
            conn.close()
            return render_template("ventas/crear.html", error="❌ Seleccione un cliente")

        # 🔴 2. PRODUCTOS
        productos = request.form.getlist("producto_id")
        cantidades = request.form.getlist("cantidad")

        if not productos or not cantidades:
            conn.close()
            return render_template("ventas/crear.html", error="❌ Agregue al menos un producto")

        subtotal = 0
        iva_total = 0
        total = 0
        detalles_guardar = []

        # 🔹 RECORRER PRODUCTOS
        for i in range(len(productos)):

            try:
                producto_id = int(productos[i])
                cantidad = int(cantidades[i])
            except:
                conn.close()
                return render_template("ventas/crear.html", error="❌ Datos inválidos")

            # 🔴 VALIDACIÓN CANTIDAD
            if cantidad <= 0:
                conn.close()
                return render_template("ventas/crear.html", error="❌ Cantidad inválida")

            # 🔹 OBTENER PRODUCTO
            cursor.execute("""
                SELECT precio, stock_actual, tiene_iva
                FROM productos
                WHERE id = ? AND activo = 1
            """, (producto_id,))
            producto = cursor.fetchone()

            # 🔴 VALIDACIÓN PRODUCTO
            if not producto:
                conn.close()
                return render_template("ventas/crear.html", error="❌ Producto no encontrado")

            # 🔴 VALIDACIÓN STOCK
            if producto["stock_actual"] < cantidad:
                conn.close()
                return render_template(
                    "ventas/crear.html",
                    error=f"❌ Stock insuficiente para producto ID {producto_id}"
                )

            precio = producto["precio"]
            tiene_iva = producto["tiene_iva"]

            # 🔹 CÁLCULOS
            sub = precio * cantidad
            iva = sub * 0.12 if tiene_iva else 0
            total_linea = sub + iva

            subtotal += sub
            iva_total += iva
            total += total_linea

            detalles_guardar.append({
                "producto_id": producto_id,
                "cantidad": cantidad,
                "precio": precio,
                "iva": iva,
                "total_linea": total_linea
            })

        # 🔴 VALIDACIÓN FINAL
        if total <= 0:
            conn.close()
            return render_template("ventas/crear.html", error="❌ Total inválido")

        # 🔹 INSERTAR VENTA
        cursor.execute("""
            INSERT INTO ventas (cliente_id, subtotal, iva, total, saldo, activo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (cliente_id, subtotal, iva_total, total, total))

        venta_id = cursor.lastrowid

        # 🔹 DETALLE + STOCK
        for d in detalles_guardar:
            cursor.execute("""
                INSERT INTO detalle_venta 
                (venta_id, producto_id, cantidad, precio, iva, total_linea)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                venta_id,
                d["producto_id"],
                d["cantidad"],
                d["precio"],
                d["iva"],
                d["total_linea"]
            ))

            cursor.execute("""
                UPDATE productos
                SET stock_actual = stock_actual - ?
                WHERE id = ?
            """, (d["cantidad"], d["producto_id"]))

        # 🔹 DEUDA CLIENTE
        cursor.execute("""
            UPDATE clientes
            SET total_deuda = total_deuda + ?
            WHERE id = ?
        """, (total, cliente_id))

        conn.commit()
        conn.close()

        return redirect(url_for("ventas.index"))

    # 🔹 GET
    cursor.execute("SELECT id, nombre FROM clientes WHERE activo = 1")
    clientes = cursor.fetchall()

    cursor.execute("""
        SELECT id, descripcion, precio, stock_actual
        FROM productos
        WHERE activo = 1
    """)
    productos = cursor.fetchall()

    conn.close()

    return render_template(
        "ventas/crear.html",
        clientes=clientes,
        productos=productos
    )


# ❌ ANULAR VENTA
@ventas_bp.route("/anular/<int:venta_id>", methods=["POST"])
def anular_venta(venta_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT total, cliente_id
        FROM ventas
        WHERE id = ? AND activo = 1
    """, (venta_id,))
    venta = cursor.fetchone()

    if not venta:
        conn.close()
        return redirect(url_for("ventas.index"))

    # 🔹 DETALLE
    cursor.execute("""
        SELECT producto_id, cantidad
        FROM detalle_venta
        WHERE venta_id = ?
    """, (venta_id,))
    detalles = cursor.fetchall()

    # 🔹 DEVOLVER STOCK
    for d in detalles:
        cursor.execute("""
            UPDATE productos
            SET stock_actual = stock_actual + ?
            WHERE id = ?
        """, (d["cantidad"], d["producto_id"]))

    total = venta["total"]
    cliente_id = venta["cliente_id"]

    # 🔹 DEVOLVER DEUDA
    cursor.execute("""
        UPDATE clientes
        SET total_deuda = total_deuda - ?
        WHERE id = ?
    """, (total, cliente_id))

    # 🔹 ANULAR
    cursor.execute("""
        UPDATE ventas
        SET activo = 0
        WHERE id = ?
    """, (venta_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("ventas.index"))