import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esta-clave")

# Base de datos MySQL local de XAMPP (usuario root, sin contraseña).
# Si tu MySQL tiene contraseña o usa otro puerto, cambia los valores de abajo
# o define la variable de entorno DATABASE_URL.
DB_USUARIO = "root"
DB_CLAVE = ""
DB_HOST = "localhost"
DB_PUERTO = 3306
DB_NOMBRE = "prueba_db"


def obtener_url_db():
    url = os.environ.get("DATABASE_URL")
    if url:
        return url.replace("mysql://", "mysql+pymysql://", 1)
    return f"mysql+pymysql://{DB_USUARIO}:{DB_CLAVE}@{DB_HOST}:{DB_PUERTO}/{DB_NOMBRE}"


def crear_base_si_no_existe(url):
    """Crea la base de datos en MySQL si todavía no existe."""
    import pymysql
    from sqlalchemy.engine import make_url

    u = make_url(url)
    try:
        conn = pymysql.connect(
            host=u.host, port=u.port or 3306, user=u.username, password=u.password or ""
        )
    except pymysql.err.OperationalError as e:
        raise SystemExit(
            "\nNo se pudo conectar a MySQL: %s\n"
            "Abre el Panel de XAMPP y presiona Start en MySQL. "
            "Si tiene contraseña o usa otro puerto, ajusta DB_CLAVE / DB_PUERTO en app.py.\n" % e
        )
    with conn.cursor() as cur:
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{u.database}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    conn.close()


URL_DB = obtener_url_db()
crear_base_si_no_existe(URL_DB)
app.config["SQLALCHEMY_DATABASE_URI"] = URL_DB
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Mensaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False)
    texto = db.Column(db.String(300), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)


@app.route("/")
def inicio():
    mensajes = Mensaje.query.order_by(Mensaje.fecha.desc()).all()
    return render_template("index.html", mensajes=mensajes)


@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form.get("nombre", "").strip()
    texto = request.form.get("texto", "").strip()
    if not nombre or not texto:
        flash("Escribe tu nombre y un mensaje.", "error")
    else:
        db.session.add(Mensaje(nombre=nombre, texto=texto))
        db.session.commit()
        flash("Mensaje guardado en la base de datos.", "ok")
    return redirect(url_for("inicio"))


@app.route("/borrar/<int:id>", methods=["POST"])
def borrar(id):
    m = db.get_or_404(Mensaje, id)
    db.session.delete(m)
    db.session.commit()
    flash("Mensaje eliminado.", "ok")
    return redirect(url_for("inicio"))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5050)
