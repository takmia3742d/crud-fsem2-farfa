from flask import Flask, request, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)

def get_db():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            edad INTEGER
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/usuarios", methods=["GET"])
def get_usuarios():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, email, edad FROM usuarios ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    usuarios = [{"id": r[0], "nombre": r[1], "email": r[2], "edad": r[3]} for r in rows]
    return jsonify(usuarios)

@app.route("/usuarios", methods=["POST"])
def create_usuario():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usuarios (nombre, email, edad) VALUES (%s, %s, %s) RETURNING id",
        (data["nombre"], data["email"], data.get("edad"))
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, **data}), 201

@app.route("/usuarios/<int:id>", methods=["PUT"])
def update_usuario(id):
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE usuarios SET nombre=%s, email=%s, edad=%s WHERE id=%s",
        (data["nombre"], data["email"], data.get("edad"), id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": id, **data})

@app.route("/usuarios/<int:id>", methods=["DELETE"])
def delete_usuario(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "Usuario eliminado"})

# Crear tabla al iniciar
with app.app_context():
    pass  # init_db() se llama abajo

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

# Inicializar al arrancar en Render
try:
    init_db()
except:
    pass
