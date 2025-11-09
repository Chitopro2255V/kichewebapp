import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
from datetime import datetime
import sqlite3

class AprendizajeMayaKiche:
    def __init__(self, root):
        self.root = root
        self.root.title("Aprende Maya K'iche'")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a73e8')
        
        # Conectar a la base de datos
        self.conectar_db()
        
        # Variables de estado
        self.usuario_actual = None
        self.leccion_actual = None
        self.puntos = 0
        self.vidas = 3
        self.palabras_preguntadas = set()
        
        # Cargar datos de lecciones
        self.cargar_lecciones()
        
        # Crear interfaz
        self.crear_interfaz()
        
    def conectar_db(self):
        """Conectar a la base de datos SQLite"""
        self.conn = sqlite3.connect('maya_kiche.db')
        self.c = self.conn.cursor()
        
        # Crear tablas si no existen
        self.c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                         (id INTEGER PRIMARY KEY, nombre TEXT, puntos INTEGER, leccion_actual INTEGER)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS progreso
                         (usuario_id INTEGER, leccion_id INTEGER, completada BOOLEAN, 
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
    
    def crear_interfaz(self):
        """Crear la interfaz principal de la aplicación"""
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='#1a73e8')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar pantalla de inicio
        self.mostrar_pantalla_inicio()
    
    def mostrar_pantalla_inicio(self):
        """Mostrar pantalla de inicio con opciones"""
        self.limpiar_pantalla()
        
        # Título
        titulo = tk.Label(self.main_frame, text="Aprende Maya K'iche'", 
                         font=('Arial', 24, 'bold'), fg='white', bg='#1a73e8')
        titulo.pack(pady=30)
        
        # Subtítulo
        subtitulo = tk.Label(self.main_frame, text="Sumérgete en la lengua y cultura Maya K'iche'", 
                            font=('Arial', 14), fg='white', bg='#1a73e8')
        subtitulo.pack(pady=10)
        
        # Botones de opciones
        frame_botones = tk.Frame(self.main_frame, bg='#1a73e8')
        frame_botones.pack(pady=50)
        
        btn_nuevo_usuario = tk.Button(frame_botones, text="Nuevo Usuario", 
                                     font=('Arial', 14), width=20, height=2,
                                     command=self.registrar_usuario)
        btn_nuevo_usuario.pack(pady=10)
        
        btn_usuario_existente = tk.Button(frame_botones, text="Usuario Existente", 
                                         font=('Arial', 14), width=20, height=2,
                                         command=self.seleccionar_usuario)
        btn_usuario_existente.pack(pady=10)
        
        btn_lecciones = tk.Button(frame_botones, text="Lecciones", 
                                 font=('Arial', 14), width=20, height=2,
                                 command=self.mostrar_lecciones)
        btn_lecciones.pack(pady=10)
    
    def registrar_usuario(self):
        """Registrar un nuevo usuario"""
        self.limpiar_pantalla()
        
        frame_registro = tk.Frame(self.main_frame, bg='white', padx=20, pady=20)
        frame_registro.pack(expand=True)
        
        tk.Label(frame_registro, text="Nombre de usuario:", 
                font=('Arial', 14), bg='white').pack(pady=10)
        
        self.entry_usuario = tk.Entry(frame_registro, font=('Arial', 14), width=20)
        self.entry_usuario.pack(pady=10)
        
        btn_guardar = tk.Button(frame_registro, text="Guardar", 
                               font=('Arial', 12), command=self.guardar_usuario)
        btn_guardar.pack(pady=10)
        
        btn_volver = tk.Button(frame_registro, text="Volver", 
                              font=('Arial', 12), command=self.mostrar_pantalla_inicio)
        btn_volver.pack(pady=10)
    
    def guardar_usuario(self):
        """Guardar nuevo usuario en la base de datos"""
        nombre = self.entry_usuario.get().strip()
        
        if nombre:
            # Verificar si el usuario ya existe
            self.c.execute("SELECT id FROM usuarios WHERE nombre = ?", (nombre,))
            existe = self.c.fetchone()
            
            if existe:
                messagebox.showerror("Error", "Este nombre de usuario ya existe")
            else:
                # Insertar nuevo usuario
                self.c.execute("INSERT INTO usuarios (nombre, puntos, leccion_actual) VALUES (?, ?, ?)", 
                              (nombre, 0, 1))
                self.conn.commit()
                
                self.usuario_actual = nombre
                messagebox.showinfo("Éxito", f"Usuario {nombre} creado correctamente")
                self.mostrar_lecciones()
        else:
            messagebox.showerror("Error", "Por favor ingresa un nombre de usuario")
    
    def seleccionar_usuario(self):
        """Seleccionar usuario existente"""
        self.limpiar_pantalla()
        
        frame_seleccion = tk.Frame(self.main_frame, bg='white', padx=20, pady=20)
        frame_seleccion.pack(expand=True)
        
        tk.Label(frame_seleccion, text="Selecciona tu usuario:", 
                font=('Arial', 14), bg='white').pack(pady=10)
        
        # Obtener lista de usuarios
        self.c.execute("SELECT nombre FROM usuarios")
        usuarios = [fila[0] for fila in self.c.fetchall()]
        
        if usuarios:
            self.combo_usuarios = ttk.Combobox(frame_seleccion, values=usuarios, 
                                              font=('Arial', 14), state='readonly')
            self.combo_usuarios.pack(pady=10)
            
            btn_seleccionar = tk.Button(frame_seleccion, text="Seleccionar", 
                                       font=('Arial', 12), command=self.cargar_usuario)
            btn_seleccionar.pack(pady=10)
        else:
            tk.Label(frame_seleccion, text="No hay usuarios registrados", 
                    font=('Arial', 12), bg='white').pack(pady=10)
        
        btn_volver = tk.Button(frame_seleccion, text="Volver", 
                              font=('Arial', 12), command=self.mostrar_pantalla_inicio)
        btn_volver.pack(pady=10)
    
    def cargar_usuario(self):
        """Cargar usuario seleccionado"""
        nombre = self.combo_usuarios.get()
        
        if nombre:
            self.usuario_actual = nombre
            messagebox.showinfo("Bienvenido", f"Hola {nombre}!")
            self.mostrar_lecciones()
        else:
            messagebox.showerror("Error", "Por favor selecciona un usuario")
    
    def mostrar_lecciones(self):
        """Mostrar lista de lecciones disponibles"""
        self.limpiar_pantalla()
        
        # Título
        titulo = tk.Label(self.main_frame, text="Lecciones de Maya K'iche'", 
                         font=('Arial', 20, 'bold'), fg='white', bg='#1a73e8')
        titulo.pack(pady=20)
        
        # Frame para lecciones
        frame_lecciones = tk.Frame(self.main_frame, bg='white')
        frame_lecciones.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Crear notebook (pestañas) para diferentes niveles
        notebook = ttk.Notebook(frame_lecciones)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña Básico
        frame_basico = ttk.Frame(notebook)
        notebook.add(frame_basico, text="Básico")
        self.crear_lista_lecciones(frame_basico, "basico")
        
        # Pestaña Intermedio
        frame_intermedio = ttk.Frame(notebook)
        notebook.add(frame_intermedio, text="Intermedio")
        self.crear_lista_lecciones(frame_intermedio, "intermedio")
        
        # Pestaña Avanzado
        frame_avanzado = ttk.Frame(notebook)
        notebook.add(frame_avanzado, text="Avanzado")
        self.crear_lista_lecciones(frame_avanzado, "avanzado")
        
        # Botón volver
        btn_volver = tk.Button(self.main_frame, text="Volver al Inicio", 
                              font=('Arial', 12), command=self.mostrar_pantalla_inicio)
        btn_volver.pack(pady=10)
    
    def crear_lista_lecciones(self, parent, nivel):
        """Crear lista de lecciones para un nivel específico"""
        # Obtener lecciones del nivel
        lecciones_nivel = self.lecciones.get(nivel, [])
        
        # Frame con scrollbar
        frame_contenedor = tk.Frame(parent)
        frame_contenedor.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(frame_contenedor)
        scrollbar = ttk.Scrollbar(frame_contenedor, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar lecciones
        for leccion in lecciones_nivel:
            frame_leccion = tk.Frame(scrollable_frame, relief=tk.RAISED, borderwidth=1, padx=10, pady=10)
            frame_leccion.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(frame_leccion, text=leccion["titulo"], 
                    font=('Arial', 14, 'bold')).pack(anchor=tk.W)
            
            tk.Label(frame_leccion, text=f"Tipo: {leccion['tipo']} | Palabras: {len(leccion['contenido'])}", 
                    font=('Arial', 10)).pack(anchor=tk.W)
            
            btn_iniciar = tk.Button(frame_leccion, text="Iniciar Lección", 
                                   font=('Arial', 10), 
                                   command=lambda l=leccion: self.iniciar_leccion(l))
            btn_iniciar.pack(anchor=tk.E)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def iniciar_leccion(self, leccion):
        """Iniciar una lección específica"""
        self.leccion_actual = leccion
        self.puntos = 0
        self.vidas = 3
        self.palabras_preguntadas = set()

        self.mostrar_ejercicio()
    
    def mostrar_ejercicio(self):
        """Mostrar un ejercicio de la lección actual"""
        self.limpiar_pantalla()

        # Obtener palabra aleatoria de la lección que no haya sido preguntada
        contenido = self.leccion_actual["contenido"]
        palabras_disponibles = [p for p in contenido if p["espanol"] not in self.palabras_preguntadas]

        if not palabras_disponibles:
            # Si todas las palabras han sido preguntadas, reiniciar el set
            self.palabras_preguntadas = set()
            palabras_disponibles = contenido

        palabra = random.choice(palabras_disponibles)
        self.palabras_preguntadas.add(palabra["espanol"])
        
        # Frame principal del ejercicio
        frame_ejercicio = tk.Frame(self.main_frame, bg='white', padx=20, pady=20)
        frame_ejercicio.pack(fill=tk.BOTH, expand=True)
        
        # Información de progreso
        frame_info = tk.Frame(frame_ejercicio, bg='white')
        frame_info.pack(fill=tk.X, pady=10)
        
        tk.Label(frame_info, text=f"Puntos: {self.puntos}", 
                font=('Arial', 12), bg='white').pack(side=tk.LEFT)
        
        tk.Label(frame_info, text=f"Vidas: {self.vidas}", 
                font=('Arial', 12), bg='white').pack(side=tk.RIGHT)
        
        # Pregunta
        frame_pregunta = tk.Frame(frame_ejercicio, bg='white')
        frame_pregunta.pack(pady=20)
        
        tk.Label(frame_pregunta, text="¿Cómo se dice en Maya K'iche'?", 
                font=('Arial', 16, 'bold'), bg='white').pack()
        
        tk.Label(frame_pregunta, text=palabra["espanol"], 
                font=('Arial', 20, 'bold'), bg='white', fg='#1a73e8').pack(pady=10)
        
        # Opciones de respuesta
        frame_opciones = tk.Frame(frame_ejercicio, bg='white')
        frame_opciones.pack(pady=20)
        
        # Obtener opciones incorrectas
        opciones_incorrectas = []
        contenido = self.leccion_actual["contenido"]
        
        while len(opciones_incorrectas) < 3:
            opcion = random.choice(contenido)
            if opcion["maya"] != palabra["maya"] and opcion["maya"] not in opciones_incorrectas:
                opciones_incorrectas.append(opcion["maya"])
        
        # Mezclar opciones
        opciones = [palabra["maya"]] + opciones_incorrectas
        random.shuffle(opciones)
        
        # Crear botones de opciones
        for opcion in opciones:
            btn = tk.Button(frame_opciones, text=opcion, 
                           font=('Arial', 14), width=20, height=2,
                           command=lambda o=opcion: self.verificar_respuesta(o, palabra["maya"]))
            btn.pack(pady=5)
        
        # Botón para saltar pregunta
        btn_saltar = tk.Button(frame_ejercicio, text="Saltar", 
                              font=('Arial', 12), command=self.mostrar_ejercicio)
        btn_saltar.pack(pady=10)
    
    def verificar_respuesta(self, respuesta, correcta):
        """Verificar si la respuesta es correcta"""
        if respuesta == correcta:
            self.puntos += 10
            messagebox.showinfo("Correcto", "¡Respuesta correcta! +10 puntos")
            if self.puntos >= 100:
                messagebox.showinfo("¡Felicidades!", f"Has completado la lección con {self.puntos} puntos!")
                self.mostrar_lecciones()
            else:
                self.mostrar_ejercicio()
        else:
            self.vidas -= 1
            if self.vidas <= 0:
                messagebox.showinfo("Fin", f"Juego terminado. Puntos finales: {self.puntos}")
                self.mostrar_lecciones()
            else:
                messagebox.showerror("Incorrecto", f"Respuesta incorrecta. Te quedan {self.vidas} vidas")
                self.mostrar_ejercicio()
    
    def limpiar_pantalla(self):
        """Limpiar todos los widgets de la pantalla actual"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def __del__(self):
        """Cerrar conexión a la base de datos al destruir la aplicación"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = AprendizajeMayaKiche(root)
    root.mainloop()

if __name__ == "__main__":
    main()