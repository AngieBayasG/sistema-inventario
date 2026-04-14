from flask import Flask, render_template, redirect, session, request, url_for, send_file
from database import get_connection, inicializar_db


# 🔹 IMPORTAR BLUEPRINTS
from routes.clientes import clientes_bp
from routes.productos import productos_bp
from routes.ventas import ventas_bp
from routes.pagos import pagos_bp

# 🔹 CREAR APP (PRIMERO SIEMPRE)
app = Flask(__name__)
app.secret_key = "clave_secreta"


# =========================
# 🔹 REGISTRAR BLUEPRINTS
# =========================
# ⚠️ NO repetir url_prefix (ya está dentro de cada archivo)
app.register_blueprint(clientes_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(pagos_bp)


# =========================
# ❌ MANEJO DE ERRORES
# =========================
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("errores/404.html"), 404


@app.errorhandler(500)
def error_servidor(error):
    return render_template("errores/500.html"), 500


# =========================
# 🔐 VALIDAR LOGIN
# =========================
def login_requerido():
    return "user" in session


# =========================
# 🏠 DASHBOARD
# =========================
@app.route("/")
def index():
    if not login_requerido():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo=1")
    total_clientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM productos WHERE activo=1")
    total_productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ventas WHERE activo=1")
    total_ventas = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_deuda) FROM clientes WHERE activo=1")
    deuda_total = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        "index.html",
        total_clientes=total_clientes,
        total_productos=total_productos,
        total_ventas=total_ventas,
        deuda_total=deuda_total
    )


# =========================
# 🔐 LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username=?", (user,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario and usuario["password"] == password:
            session["user"] = user
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="❌ Usuario o contraseña incorrectos")

    return render_template("login.html")


# =========================
# 🚪 LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================
# 📊 DATOS PARA GRÁFICAS
# =========================
@app.route("/dashboard-data")
def dashboard_data():
    if not login_requerido():
        return {}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE(fecha), SUM(total)
        FROM ventas
        WHERE activo=1
        GROUP BY DATE(fecha)
    """)

    datos = cursor.fetchall()
    conn.close()

    fechas = [d[0] for d in datos]
    totales = [d[1] for d in datos]

    return {"fechas": fechas, "totales": totales}

# =========================
# 🧾 GENERAR PDF
# =========================
@app.route("/reporte/pdf")
def reporte_pdf():
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors
    from flask import send_file
    import io

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT nombre, total_deuda FROM clientes WHERE activo=1")
    data = cursor.fetchall()
    conn.close()

    # 🔥 Crear PDF en memoria
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)

    tabla_data = [["Cliente", "Deuda"]] + [list(d) for d in data]

    tabla = Table(tabla_data)

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    doc.build([tabla])

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="reporte_clientes.pdf")

# =========================
# 🚀 INICIO
# =========================
if __name__ == "__main__":
    inicializar_db()
    app.run(debug=True, use_reloader=False)