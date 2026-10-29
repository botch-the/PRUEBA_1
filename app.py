from datetime import datetime
import os
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "a8aaeb66a3dda5acf7eef75f7b2ad358ce34c24c9b83e2f65e18fdb951bd61a9",
)


def obtener_url_db():
  # 1. Buscar si Railway provee DATABASE_URL y asegurar el formato correcto
  database_url = os.environ.get("DATABASE_URL")
  if database_url:
    # Limpiar espacios en blanco por si acaso
    database_url = database_url.strip()
    # Si viene con el protocolo viejo, lo actualizamos para pymysql
    if database_url.startswith("mysql://"):
      database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)
    elif not database_url.startswith("mysql+pymysql://"):
      database_url = f"mysql+pymysql://{database_url}"
    return database_url

  # 2. Intentar con las variables independientes de Railway
  db_host = os.environ.get("MYSQLHOST")
  db_user = os.environ.get("MYSQLUSER")
  db_password = os.environ.get("MYSQLPASSWORD")
  db_port = os.environ.get("MYSQLPORT", "3306")
  db_name = os.environ.get("MYSQLDATABASE")

  if db_host and db_user and db_name:
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

  # 3. Entorno local por defecto (XAMPP)
  return "mysql+pymysql://root:@localhost:3306/prueba_db"


URL_DB = obtener_url_db()

# Configuración de SQLAlchemy
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


if __name__ == '__main__':
    app.run(port=5001) # O prueba con 8080