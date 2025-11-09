from flask import Flask, render_template, request, session, redirect, url_for, flash
import json
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura

class AprendizajeMayaKicheWeb:
    def __init__(self):
        # Conectar a la base de datos
        self.conectar_db()

        # Cargar datos de lecciones
        self.cargar_lecciones()

    def conectar_db(self):
        """Conectar a la base de datos SQLite"""
        self.conn = sqlite3.connect('maya_kiche.db', check_same_thread=False)
        self.c = self.conn.cursor()

        # Crear tablas si no existen
        self.c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                         (id INTEGER PRIMARY KEY, nombre TEXT UNIQUE, puntos INTEGER DEFAULT 0, leccion_actual INTEGER DEFAULT 1)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS progreso
                         (usuario_id INTEGER, leccion_id INTEGER, completada BOOLEAN DEFAULT FALSE,
                         fecha_completado DATE, FOREIGN KEY(usuario_id) REFERENCES usuarios(id))''')

        self.conn.commit()

    def cargar_lecciones(self):
        """Cargar lecciones desde archivo JSON o crear datos de ejemplo"""
        try:
            with open('lecciones_maya_kiche.json', 'r', encoding='utf-8') as f:
                self.lecciones = json.load(f)
        except FileNotFoundError:
            # Crear datos de ejemplo si el archivo no existe
            self.lecciones = {
                "basico": [
                    {
                        "id": 1,
                        "titulo": "Saludos Básicos",
                        "tipo": "vocabulario",
                        "contenido": [
                            {"maya": "Saqarik", "espanol": "Buenos días", "imagen": "sol.png"},
                            {"maya": "Xqa q'ij", "espanol": "Buenas tardes", "imagen": "tarde.png"},
                            {"maya": "Xokaq'ab'", "espanol": "Buenas noches", "imagen": "noche.png"},
                            {"maya": "Utz awach?", "espanol": "¿Cómo estás?", "imagen": "saludo.png"},
                            {"maya": "Utz tinimit", "espanol": "Estoy bien", "imagen": "bien.png"}
                        ]
                    },
                    {
                        "id": 2,
                        "titulo": "Números 1-10",
                        "tipo": "numeros",
                        "contenido": [
                            {"maya": "Jun", "espanol": "Uno", "imagen": "1.png"},
                            {"maya": "Kieb'", "espanol": "Dos", "imagen": "2.png"},
                            {"maya": "Oxib'", "espanol": "Tres", "imagen": "3.png"},
                            {"maya": "Kajib'", "espanol": "Cuatro", "imagen": "4.png"},
                            {"maya": "Job'", "espanol": "Cinco", "imagen": "5.png"}
                        ]
                    }
                ],
                "intermedio": [
                    {
                        "id": 3,
                        "titulo": "Familia",
                        "tipo": "vocabulario",
                        "contenido": [
                            {"maya": "Na", "espanol": "Madre", "imagen": "madre.png"},
                            {"maya": "Te", "espanol": "Padre", "imagen": "padre.png"},
                            {"maya": "Ali", "espanol": "Hijo/Hija", "imagen": "hijo.png"},
                            {"maya": "Achijab'", "espanol": "Hermano", "imagen": "hermano.png"}
                        ]
                    }
                ]
            }

            # Guardar datos de ejemplo
            with open('lecciones_maya_kiche.json', 'w', encoding='utf-8') as f:
                json.dump(self.lecciones, f, ensure_ascii=False, indent=2)

# Instancia global de la aplicación
app_maya = AprendizajeMayaKicheWeb()

@app.route('/')
def index():
    """Página de inicio"""
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevo usuario"""
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()

        if nombre:
            try:
                app_maya.c.execute("INSERT INTO usuarios (nombre) VALUES (?)", (nombre,))
                app_maya.conn.commit()
                session['usuario_id'] = app_maya.c.lastrowid
                session['usuario_nombre'] = nombre
                flash(f"Usuario {nombre} creado correctamente", "success")
                return redirect(url_for('lecciones'))
            except sqlite3.IntegrityError:
                flash("Este nombre de usuario ya existe", "error")
        else:
            flash("Por favor ingresa un nombre de usuario", "error")

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión de usuario existente"""
    if request.method == 'POST':
        nombre = request.form['nombre']

        app_maya.c.execute("SELECT id, nombre FROM usuarios WHERE nombre = ?", (nombre,))
        usuario = app_maya.c.fetchone()

        if usuario:
            session['usuario_id'] = usuario[0]
            session['usuario_nombre'] = usuario[1]
            flash(f"Hola {usuario[1]}!", "success")
            return redirect(url_for('lecciones'))
        else:
            flash("Usuario no encontrado", "error")

    # Obtener lista de usuarios para el dropdown
    app_maya.c.execute("SELECT nombre FROM usuarios")
    usuarios = [fila[0] for fila in app_maya.c.fetchall()]

    return render_template('login.html', usuarios=usuarios)

@app.route('/lecciones')
def lecciones():
    """Mostrar lista de lecciones disponibles"""
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    return render_template('lecciones.html', lecciones=app_maya.lecciones)

@app.route('/leccion/<int:leccion_id>')
def iniciar_leccion(leccion_id):
    """Iniciar una lección específica"""
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    # Buscar la lección por ID
    leccion = None
    for nivel, lecciones_nivel in app_maya.lecciones.items():
        for l in lecciones_nivel:
            if l['id'] == leccion_id:
                leccion = l
                break
        if leccion:
            break

    if not leccion:
        flash("Lección no encontrada", "error")
        return redirect(url_for('lecciones'))

    # Reiniciar estado de la sesión para la nueva lección
    session['leccion_actual'] = leccion
    session['puntos'] = 0
    session['vidas'] = 3
    session['palabras_preguntadas'] = []

    return redirect(url_for('ejercicio'))

@app.route('/ejercicio', methods=['GET', 'POST'])
def ejercicio():
    """Mostrar un ejercicio de la lección actual"""
    if 'usuario_id' not in session or 'leccion_actual' not in session:
        return redirect(url_for('index'))

    leccion = session['leccion_actual']
    puntos = session.get('puntos', 0)
    vidas = session.get('vidas', 3)
    palabras_preguntadas = session.get('palabras_preguntadas', [])

    if request.method == 'POST':
        respuesta = request.form['respuesta']
        correcta = request.form['correcta']

        if respuesta == correcta:
            puntos += 10
            session['puntos'] = puntos
            flash("¡Respuesta correcta! +10 puntos", "success")

            if puntos >= 100:
                flash(f"¡Felicidades! Has completado la lección con {puntos} puntos!", "success")
                return redirect(url_for('lecciones'))
        else:
            vidas -= 1
            session['vidas'] = vidas

            if vidas <= 0:
                flash(f"Juego terminado. Puntos finales: {puntos}", "error")
                return redirect(url_for('lecciones'))
            else:
                flash(f"Respuesta incorrecta. Te quedan {vidas} vidas", "error")

    # Obtener palabra aleatoria que no haya sido preguntada
    contenido = leccion["contenido"]
    palabras_disponibles = [p for p in contenido if p["espanol"] not in palabras_preguntadas]

    if not palabras_disponibles:
        # Si todas las palabras han sido preguntadas, reiniciar la lista
        session['palabras_preguntadas'] = []
        palabras_disponibles = contenido

    palabra = random.choice(palabras_disponibles)
    palabras_preguntadas.append(palabra["espanol"])
    session['palabras_preguntadas'] = palabras_preguntadas

    # Obtener opciones incorrectas
    opciones_incorrectas = []
    while len(opciones_incorrectas) < 3:
        opcion = random.choice(contenido)
        if opcion["maya"] != palabra["maya"] and opcion["maya"] not in opciones_incorrectas:
            opciones_incorrectas.append(opcion["maya"])

    # Mezclar opciones
    opciones = [palabra["maya"]] + opciones_incorrectas
    random.shuffle(opciones)

    return render_template('ejercicio.html',
                         palabra=palabra,
                         opciones=opciones,
                         puntos=puntos,
                         vidas=vidas)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
