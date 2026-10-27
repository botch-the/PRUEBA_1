from datetime import datetime
import os
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "a8aaeb66a3dda5acf7eef75f7b2ad358ce34c24c9b83e2f65e18fdb951bd61a9",
)

# Configuración local por defecto (XAMPP)
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "prueba_db"


def obtener_url_db():
  # 1. Intentar usar las variables individuales que provee Railway
  db_host = os.environ.get("MYSQLHOST")
  db_user = os.environ.get("MYSQLUSER")
  db_password = os.environ.get("MYSQLPASSWORD")
  db_port = os.environ.get("MYSQLPORT")
  db_name = os.environ.get("MYSQLDATABASE")

  if db_host and db_user and db_name:
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port or 3306}/{db_name}"

  # 2. Si existe DATABASE_URL general
  url = os.environ.get("DATABASE_URL")
  if url:
    return url.replace("mysql://", "mysql+pymysql://", 1)

  # 3. Por defecto usar entorno local (XAMPP)
  return (
      f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  )


def crear_base_si_no_existe(url):
  """Crea la base de datos en MySQL local si todavía no existe (Solo para XAMPP)."""
  import pymysql
  from sqlalchemy.engine import make_url

  u = make_url(url)

  # Si estamos en producción (Railway), el host no es localhost, así que omitimos esto
  if u.host not in ["localhost", "127.0.0.1"]:
    return

  try:
    conn = pymysql.connect(
        host=u.host, port=u.port or 3306, user=u.username, password=u.password or ""
    )
  except pymysql.err.OperationalError as e:
    raise SystemExit(
        "\nNo se pudo conectar a MySQL local (XAMPP): %s\n"
        "Abre el Panel de XAMPP y presiona Start en MySQL. "
        "Si tiene contraseña o usa otro puerto, ajusta DB_PASSWORD / DB_PORT en"
        " app.py.\n"
        % e
    )
  with conn.cursor() as cur:
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS `{u.database}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
  conn.close()


URL_DB = obtener_url_db()

# Solo intentamos crear la base si estamos en local
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
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)