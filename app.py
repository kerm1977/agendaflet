import flet as ft
import sqlite3
import hashlib
import re

DATABASE_NAME = "users.db"
LOGGED_IN_USER = None # Variable global para simular el usuario logueado

# --- NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS ---
# Definición de las listas de opciones para los Dropdowns
ACTIVIDADES_CHOICES = [
    ft.dropdown.Option(''), # Opción vacía por defecto
    ft.dropdown.Option('La Tribu'),
    ft.dropdown.Option('Senderista'),
    ft.dropdown.Option('Enfermería'),
    ft.dropdown.Option('Cocina'),
    ft.dropdown.Option('Confección y Diseño'),
    ft.dropdown.Option('Restaurante'),
    ft.dropdown.Option('Transporte Terrestre'),
    ft.dropdown.Option('Transporte Acuatico'),
    ft.dropdown.Option('Transporte Aereo'),
    ft.dropdown.Option('Migración'),
    ft.dropdown.Option('Parque Nacional'),
    ft.dropdown.Option('Refugio Silvestre'),
    ft.dropdown.Option('Centro de Atracción'),
    ft.dropdown.Option('Lugar para Caminata'),
    ft.dropdown.Option('Acarreo'),
    ft.dropdown.Option('Oficina de trámite'),
    ft.dropdown.Option('Primeros Auxilios'),
    ft.dropdown.Option('Farmacia'),
    ft.dropdown.Option('Taller'),
    ft.dropdown.Option('Abobado'),
    ft.dropdown.Option('Mensajero'),
    ft.dropdown.Option('Tienda'),
    ft.dropdown.Option('Polizas'),
    ft.dropdown.Option('Aerolínea'),
    ft.dropdown.Option('Guía'),
    ft.dropdown.Option('Banco'),
    ft.dropdown.Option('Otros')
]

CAPACIDAD_PERSONA_CHOICES = [
    ft.dropdown.Option(''), # Opción vacía por defecto
    ft.dropdown.Option('Rápido'),
    ft.dropdown.Option('Intermedio'),
    ft.dropdown.Option('Básico'),
    ft.dropdown.Option('Iniciante')
]

PARTICIPACION_CHOICES = [
    ft.dropdown.Option(''), # Opción vacía por defecto
    ft.dropdown.Option('Solo de La Tribu'),
    ft.dropdown.Option('constante'),
    ft.dropdown.Option('inconstante'),
    ft.dropdown.Option('El Camino de Costa Rica'),
    ft.dropdown.Option('Parques Nacionales'),
    ft.dropdown.Option('Paseo | Recreativo'),
    ft.dropdown.Option('Revisar/Eliminar')
]
# --- FIN NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS ---


def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            p_apellido TEXT NOT NULL,
            s_apellido TEXT,
            usuario TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefono TEXT,
            password_hash TEXT NOT NULL
        )
    ''')
    # --- NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            primer_apellido TEXT NOT NULL,
            segundo_apellido TEXT,
            telefono TEXT,
            movil TEXT,
            email TEXT,
            direccion TEXT,
            actividad TEXT,
            nota TEXT,
            empresa TEXT,
            sitio_web TEXT,
            capacidad_persona TEXT,
            participacion TEXT
        )
    ''')
    # --- FIN NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS ---
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user_db(nombre, p_apellido, s_apellido, usuario, email, telefono, password_hash):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nombre, p_apellido, s_apellido, usuario, email, telefono, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (nombre, p_apellido, s_apellido, usuario, email, telefono, password_hash))
        conn.commit()
        return True, "Registro exitoso."
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: usuarios.usuario" in str(e):
            return False, "Error: El nombre de usuario ya existe."
        elif "UNIQUE constraint failed: usuarios.email" in str(e):
            return False, "Error: El correo electrónico ya está registrado."
        return False, f"Error en el registro: {e}"
    finally:
        conn.close()

def authenticate_user_db(identifier, password_hash):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, nombre FROM usuarios WHERE (usuario = ? OR email = ?) AND password_hash = ?",
                   (identifier, identifier, password_hash))
    user = cursor.fetchone()
    conn.close()
    if user:
        return True, user[0] # Retorna True y el nombre de usuario (el campo 'usuario')
    return False, None

def is_valid_email(email):
    # Regex básica para validar email
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# --- NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS ---
def add_contact_db(contact_data):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO contactos (
                nombre, primer_apellido, segundo_apellido, telefono, movil, email,
                direccion, actividad, nota, empresa, sitio_web, capacidad_persona, participacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contact_data['nombre'],
            contact_data['primer_apellido'],
            contact_data['segundo_apellido'],
            contact_data['telefono'],
            contact_data['movil'],
            contact_data['email'],
            contact_data['direccion'],
            contact_data['actividad'],
            contact_data['nota'],
            contact_data['empresa'],
            contact_data['sitio_web'],
            contact_data['capacidad_persona'],
            contact_data['participacion']
        ))
        conn.commit()
        return True, "Contacto guardado exitosamente."
    except Exception as e:
        return False, f"Error al guardar contacto: {e}"
    finally:
        conn.close()

def get_all_contacts_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Asegúrate de seleccionar todas las columnas en el orden correcto
    # (id, nombre, primer_apellido, segundo_apellido, telefono, movil, email, direccion, actividad, nota, empresa, sitio_web, capacidad_persona, participacion)
    cursor.execute("SELECT * FROM contactos ORDER BY nombre, primer_apellido")
    contacts = cursor.fetchall()
    conn.close()
    return contacts

def get_contact_by_id_db(contact_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contactos WHERE id = ?", (contact_id,))
    contact = cursor.fetchone()
    conn.close()
    return contact

# --- MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - Funciones DB ---
def delete_contact_db(contact_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM contactos WHERE id = ?", (contact_id,))
        conn.commit()
        return True, "Contacto eliminado exitosamente."
    except Exception as e:
        return False, f"Error al eliminar contacto: {e}"
    finally:
        conn.close()

def update_contact_db(contact_id, contact_data):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE contactos SET
                nombre = ?, primer_apellido = ?, segundo_apellido = ?, telefono = ?,
                movil = ?, email = ?, direccion = ?, actividad = ?, nota = ?,
                empresa = ?, sitio_web = ?, capacidad_persona = ?, participacion = ?
            WHERE id = ?
        ''', (
            contact_data['nombre'],
            contact_data['primer_apellido'],
            contact_data['segundo_apellido'],
            contact_data['telefono'],
            contact_data['movil'],
            contact_data['email'],
            contact_data['direccion'],
            contact_data['actividad'],
            contact_data['nota'],
            contact_data['empresa'],
            contact_data['sitio_web'],
            contact_data['capacidad_persona'],
            contact_data['participacion'],
            contact_id
        ))
        conn.commit()
        return True, "Contacto actualizado exitosamente."
    except Exception as e:
        return False, f"Error al actualizar contacto: {e}"
    finally:
        conn.close()
# --- FIN MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - Funciones DB ---
# --- FIN NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS ---


def main(page: ft.Page):
    page.title = "App de Autenticación Flet"
    page.window_width = 400 # Ancho para simular móvil
    page.window_height = 700

    init_db()

    def logout_user(e):
        global LOGGED_IN_USER
        LOGGED_IN_USER = None
        username_email_input.value = ""
        password_input.value = ""
        login_message_text.value = "Sesión cerrada."
        login_message_text.color = ft.Colors.BLACK54
        page.update()
        page.go("/login") # Redirigir al login después de cerrar sesión

    # Componente del Footer (creado una vez para reutilizarlo)
    footer_text_widget = ft.Container(
        content=ft.Row(
            [
                ft.Text("HECHO CON", color=ft.Colors.ORANGE_700, size=12, weight=ft.FontWeight.BOLD),
                ft.Icon(name=ft.Icons.FAVORITE, color=ft.Colors.ORANGE_700, size=12), # Corazón
                ft.Text("LA TRIBU DE LOS LIBRES", color=ft.Colors.ORANGE_700, size=12, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER, # Centrar el contenido del Row
            spacing=3, # Espacio entre los elementos
        ),
        alignment=ft.alignment.bottom_center, # Alinear el contenedor al fondo y al centro
        padding=ft.padding.only(bottom=10), # Pequeño padding desde el borde inferior
    )


    # --- Vistas ---

    # 1. Home View
    def home_view():
        app_bar_actions = []
        if LOGGED_IN_USER:
            app_bar_actions.append(ft.Text(f"{LOGGED_IN_USER}", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD))
            app_bar_actions.append(
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_color=ft.Colors.WHITE,
                    icon_size=24,
                    tooltip="Cerrar Sesión",
                    on_click=logout_user,
                )
            )
            # --- MODIFICACIÓN DE ICONO: Agenda de Contactos ahora va a la lista ---
            app_bar_actions.append(
                ft.IconButton(
                    icon=ft.Icons.CONTACTS, # Icono para la agenda
                    icon_color=ft.Colors.WHITE,
                    icon_size=24,
                    tooltip="Ver Contactos",
                    on_click=lambda e: page.go("/contacts_list"), # IR A LA LISTA DE CONTACTOS
                )
            )
            # --- FIN MODIFICACIÓN DE ICONO ---
        else:
            app_bar_actions.append(
                ft.IconButton(
                    icon=ft.Icons.ACCOUNT_CIRCLE,
                    icon_size=30,
                    tooltip="Acceder/Iniciar Sesión",
                    on_click=lambda e: page.go("/login"),
                )
            )

        return ft.View(
            "/home",
            [
                ft.AppBar(
                    title=ft.Text(""),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    actions=app_bar_actions
                ),
                ft.Column( # Contenedor principal de la vista Home
                    [
                        ft.Container(expand=True), # Este Container "empuja" el contenido hacia arriba y el footer hacia abajo
                        footer_text_widget, # El footer
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True # La columna ocupa todo el espacio vertical disponible
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # Distribuye los elementos (AppBar, Column principal) en el View
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # 2. Login View (sin cambios)
    username_email_input = ft.TextField(
        label="Usuario o Email",
        hint_text="Ingresa tu usuario o correo",
        expand=True,
    )
    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        expand=True,
    )
    remember_me_checkbox = ft.Checkbox(label="Recordar contraseña")
    login_message_text = ft.Text("", color=ft.Colors.RED_500)

    def login_user(e):
        global LOGGED_IN_USER
        identifier = username_email_input.value.strip()
        password = password_input.value.strip()

        if not identifier or not password:
            login_message_text.value = "Por favor, ingresa tu usuario/email y contraseña."
            login_message_text.color = ft.Colors.RED_500
            page.update()
            return

        hashed_password = hash_password(password)
        success, user_name = authenticate_user_db(identifier, hashed_password)

        if success:
            LOGGED_IN_USER = user_name
            login_message_text.value = "Inicio de sesión exitoso!"
            login_message_text.color = ft.Colors.GREEN_500
            username_email_input.value = ""
            password_input.value = ""
            page.update()
            page.go("/home")
        else:
            login_message_text.value = "Usuario o contraseña incorrectos."
            login_message_text.color = ft.Colors.RED_500
            page.update()

    def login_view():
        return ft.View(
            "/login",
            [
                ft.AppBar(
                    title=ft.Text("Iniciar Sesión"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/home"))
                ),
                ft.Column( # Contenedor principal de la vista Login
                    [
                        ft.Container(expand=True), # Espacio flexible arriba para centrar
                        ft.Column( # Columna que contiene los elementos del formulario
                            [
                                ft.Text("Inicia Sesión en tu Cuenta", size=24, weight=ft.FontWeight.BOLD),
                                ft.ResponsiveRow(
                                    [ft.Column([username_email_input], col={"xs": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.ResponsiveRow(
                                    [ft.Column([password_input], col={"xs": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.ResponsiveRow(
                                    [ft.Column([remember_me_checkbox], col={"xs": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                login_message_text,
                                ft.ResponsiveRow(
                                    [ft.Column([ft.ElevatedButton("Iniciar Sesión", on_click=login_user, expand=True)], col={"xs": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.ResponsiveRow(
                                    [ft.Column([ft.TextButton("¿No tienes cuenta? Regístrate aquí.", on_click=lambda e: page.go("/register"))], col={"xs": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        ft.Container(expand=True), # Espacio flexible abajo para centrar
                        footer_text_widget, # El footer
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True, # La columna principal debe expandirse para que el centrado funcione
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # Distribuye los elementos (AppBar, Column principal) en el View
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # 3. Register View (sin cambios)
    reg_nombre_input = ft.TextField(label="Nombre", expand=True)
    reg_p_apellido_input = ft.TextField(label="Primer Apellido", expand=True)
    reg_s_apellido_input = ft.TextField(label="Segundo Apellido (Opcional)", expand=True)
    reg_usuario_input = ft.TextField(label="Nombre de Usuario", expand=True)
    reg_mail_input = ft.TextField(label="Correo Electrónico", expand=True)
    reg_telefono_input = ft.TextField(label="Teléfono (Opcional)", expand=True)
    reg_password_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, expand=True)
    reg_confirm_password_input = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True, expand=True)
    register_message_text = ft.Text("", color=ft.Colors.RED_500)

    def register_user(e):
        nombre = reg_nombre_input.value.strip()
        p_apellido = reg_p_apellido_input.value.strip()
        s_apellido = reg_s_apellido_input.value.strip()
        usuario = reg_usuario_input.value.strip()
        email = reg_mail_input.value.strip()
        telefono = reg_telefono_input.value.strip()
        password = reg_password_input.value.strip()
        confirm_password = reg_confirm_password_input.value.strip()

        # Validaciones
        if not all([nombre, p_apellido, usuario, email, password, confirm_password]):
            register_message_text.value = "Por favor, completa todos los campos obligatorios."
            register_message_text.color = ft.Colors.RED_500
            page.update()
            return
        
        if not is_valid_email(email):
            register_message_text.value = "Formato de correo electrónico inválido."
            register_message_text.color = ft.Colors.RED_500
            page.update()
            return

        if password != confirm_password:
            register_message_text.value = "Las contraseñas no coinciden."
            register_message_text.color = ft.Colors.RED_500
            page.update()
            return
        
        if len(password) < 6:
            register_message_text.value = "La contraseña debe tener al menos 6 caracteres."
            register_message_text.color = ft.Colors.RED_500
            page.update()
            return

        hashed_password = hash_password(password)
        success, message = register_user_db(nombre, p_apellido, s_apellido, usuario, email, telefono, hashed_password)

        if success:
            register_message_text.value = "Registro exitoso. ¡Ahora puedes iniciar sesión!"
            register_message_text.color = ft.Colors.GREEN_500
            reg_nombre_input.value = ""
            reg_p_apellido_input.value = ""
            reg_s_apellido_input.value = ""
            reg_usuario_input.value = ""
            reg_mail_input.value = ""
            reg_telefono_input.value = ""
            reg_password_input.value = ""
            reg_confirm_password_input.value = ""
            page.update()
            page.go("/login")
        else:
            register_message_text.value = message
            register_message_text.color = ft.Colors.RED_500
            page.update()


    def register_view():
        return ft.View(
            "/register",
            [
                ft.AppBar(
                    title=ft.Text("Registrarse"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/login"))
                ),
                ft.Column( # Contenedor principal de la vista Register
                    [
                        ft.Container(expand=True), # Espacio flexible arriba para centrar
                        ft.Column( # Columna que contiene los elementos del formulario
                            [
                                ft.Text("Crea una Nueva Cuenta", size=24, weight=ft.FontWeight.BOLD),
                                # ResponsiveRows para centrar y ajustar en móvil
                                ft.ResponsiveRow([ft.Column([reg_nombre_input], col={"xs":12, "md":6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                ft.ResponsiveRow([ft.Column([reg_p_apellido_input], col={"xs":12, "md":6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                ft.ResponsiveRow([ft.Column([reg_s_apellido_input], col={"xs":12, "md":6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                ft.ResponsiveRow([ft.Column([reg_usuario_input], col={"xs":12, "md":6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                ft.ResponsiveRow([ft.Column([reg_mail_input], col={"xs":12, "md":6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                ft.ResponsiveRow([ft.Column([reg_telefono_input], col={"xs":12, "md":6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                ft.ResponsiveRow([ft.Column([reg_password_input], col={"xs":12, "md":6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                ft.ResponsiveRow([ft.Column([reg_confirm_password_input], col={"xs":12, "md":6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER),
                                register_message_text,
                                ft.ResponsiveRow(
                                    [ft.Column([ft.ElevatedButton("Registrarse", on_click=register_user, expand=True)], col={"xs": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.ResponsiveRow(
                                    [ft.Column([ft.TextButton("¿Ya tienes cuenta? Inicia Sesión.", on_click=lambda e: page.go("/login"))], col={"xs": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                            scroll=ft.ScrollMode.ADAPTIVE,
                        ),
                        ft.Container(expand=True), # Espacio flexible abajo para centrar
                        footer_text_widget, # El footer
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True, # La columna principal debe expandirse para que el centrado funcione
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # Distribuye los elementos (AppBar, Column principal) en el View
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # --- NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS - FORMULARIO DE AÑADIR ---
    # Campos de entrada para el formulario de contacto (se mantienen para la vista de añadir y editar)
    contact_nombre_input = ft.TextField(label="Nombre", expand=True)
    contact_primer_apellido_input = ft.TextField(label="Primer Apellido", expand=True)
    contact_segundo_apellido_input = ft.TextField(label="Segundo Apellido (Opcional)", expand=True)
    contact_telefono_input = ft.TextField(label="Teléfono", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9+\-\(\)\s]", replacement_string=""), expand=True)
    contact_movil_input = ft.TextField(label="Móvil", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9+\-\(\)\s]", replacement_string=""), expand=True)
    contact_email_input = ft.TextField(label="Correo Electrónico", expand=True)
    contact_direccion_input = ft.TextField(label="Dirección", multiline=True, min_lines=2, max_lines=5, expand=True)
    
    contact_actividad_dropdown = ft.Dropdown(
        label="Actividad",
        options=ACTIVIDADES_CHOICES,
        expand=True,
    )
    contact_nota_input = ft.TextField(label="Nota", multiline=True, min_lines=2, max_lines=5, expand=True)
    contact_empresa_input = ft.TextField(label="Empresa", expand=True)
    contact_sitio_web_input = ft.TextField(label="Sitio Web", expand=True)
    
    contact_capacidad_persona_dropdown = ft.Dropdown(
        label="Capacidad de Persona",
        options=CAPACIDAD_PERSONA_CHOICES,
        expand=True,
    )
    contact_participacion_dropdown = ft.Dropdown(
        label="Participación",
        options=PARTICIPACION_CHOICES,
        expand=True,
    )
    add_contact_message_text = ft.Text("", color=ft.Colors.RED_500)
    edit_contact_message_text = ft.Text("", color=ft.Colors.RED_500)


    def save_contact(e):
        # Validar campos obligatorios
        if not all([contact_nombre_input.value, contact_primer_apellido_input.value]):
            add_contact_message_text.value = "Nombre y Primer Apellido son obligatorios."
            add_contact_message_text.color = ft.Colors.RED_500
            page.update()
            return
        
        # Validar formato de email si se proporciona
        if contact_email_input.value and not is_valid_email(contact_email_input.value):
            add_contact_message_text.value = "Formato de correo electrónico inválido."
            add_contact_message_text.color = ft.Colors.RED_500
            page.update()
            return

        contact_data = {
            'nombre': contact_nombre_input.value.strip(),
            'primer_apellido': contact_primer_apellido_input.value.strip(),
            'segundo_apellido': contact_segundo_apellido_input.value.strip(),
            'telefono': contact_telefono_input.value.strip(),
            'movil': contact_movil_input.value.strip(),
            'email': contact_email_input.value.strip(),
            'direccion': contact_direccion_input.value.strip(),
            'actividad': contact_actividad_dropdown.value if contact_actividad_dropdown.value else '',
            'nota': contact_nota_input.value.strip(),
            'empresa': contact_empresa_input.value.strip(),
            'sitio_web': contact_sitio_web_input.value.strip(),
            'capacidad_persona': contact_capacidad_persona_dropdown.value if contact_capacidad_persona_dropdown.value else '',
            'participacion': contact_participacion_dropdown.value if contact_participacion_dropdown.value else ''
        }

        success, message = add_contact_db(contact_data)

        if success:
            add_contact_message_text.value = message
            add_contact_message_text.color = ft.Colors.GREEN_500
            # Limpiar campos después de guardar
            contact_nombre_input.value = ""
            contact_primer_apellido_input.value = ""
            contact_segundo_apellido_input.value = ""
            contact_telefono_input.value = ""
            contact_movil_input.value = ""
            contact_email_input.value = ""
            contact_direccion_input.value = ""
            contact_actividad_dropdown.value = "" # Restablecer Dropdown
            contact_nota_input.value = ""
            contact_empresa_input.value = ""
            contact_sitio_web_input.value = ""
            contact_capacidad_persona_dropdown.value = "" # Restablecer Dropdown
            contact_participacion_dropdown.value = "" # Restablecer Dropdown
            page.update()
            # Opcional: Redirigir a la lista de contactos después de añadir
            # page.go("/contacts_list") 
        else:
            add_contact_message_text.value = message
            add_contact_message_text.color = ft.Colors.RED_500
            page.update()

    def add_contact_view():
        # Asegurarse de limpiar los campos al entrar a la vista de añadir
        contact_nombre_input.value = ""
        contact_primer_apellido_input.value = ""
        contact_segundo_apellido_input.value = ""
        contact_telefono_input.value = ""
        contact_movil_input.value = ""
        contact_email_input.value = ""
        contact_direccion_input.value = ""
        contact_actividad_dropdown.value = ""
        contact_nota_input.value = ""
        contact_empresa_input.value = ""
        contact_sitio_web_input.value = ""
        contact_capacidad_persona_dropdown.value = ""
        contact_participacion_dropdown.value = ""
        add_contact_message_text.value = ""
        page.update() # Asegurar que los cambios se reflejen

        return ft.View(
            "/add_contact",
            [
                ft.AppBar(
                    title=ft.Text("Agregar Nuevo Contacto"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/contacts_list")) # Volver a la lista
                ),
                ft.Column( # Contenedor principal de la vista de añadir contacto
                    [
                        ft.Text("Datos del Contacto", size=24, weight=ft.FontWeight.BOLD),
                        ft.ResponsiveRow([ft.Column([contact_nombre_input], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_primer_apellido_input], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_segundo_apellido_input], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([
                            ft.Column([contact_telefono_input], col={"xs": 12, "md": 6}),
                            ft.Column([contact_movil_input], col={"xs": 12, "md": 6}),
                        ]),
                        ft.ResponsiveRow([ft.Column([contact_email_input], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_direccion_input], col={"xs": 12, "md": 12})]), # Dirección puede ser más ancha
                        ft.ResponsiveRow([ft.Column([contact_actividad_dropdown], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_nota_input], col={"xs": 12, "md": 12})]), # Nota también puede ser más ancha
                        ft.ResponsiveRow([
                            ft.Column([contact_empresa_input], col={"xs": 12, "md": 6}),
                            ft.Column([contact_sitio_web_input], col={"xs": 12, "md": 6}),
                        ]),
                        ft.ResponsiveRow([ft.Column([contact_capacidad_persona_dropdown], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_participacion_dropdown], col={"xs": 12, "md": 6})]),
                        add_contact_message_text,
                        ft.ResponsiveRow(
                            [ft.Column([ft.ElevatedButton("Guardar Contacto", on_click=save_contact, expand=True)], col={"xs": 12, "md": 6})],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Container(height=20),
                        footer_text_widget,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                    spacing=10
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # --- NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS - LISTA DE CONTACTOS ---
    def contacts_list_view():
        contacts = get_all_contacts_db() # Obtener todos los contactos de la DB

        contact_items = []
        if not contacts:
            contact_items.append(
                ft.Text("No hay contactos aún. ¡Agrega uno!", italic=True, color=ft.Colors.BLACK54)
            )
        else:
            for contact in contacts:
                contact_id = contact[0] # ID del contacto
                nombre_completo = f"{contact[1]} {contact[2]}" # Nombre y primer apellido
                if contact[3]: # Segundo apellido
                    nombre_completo += f" {contact[3]}"
                
                movil_text = f"Móvil: {contact[5]}" if contact[5] else "Móvil: N/A"

                contact_items.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column(
                                [
                                    ft.Text(nombre_completo, size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(movil_text, size=14, color=ft.Colors.GREY_700),
                                    ft.Divider(height=5, color=ft.Colors.GREY_300), # Separador visual
                                    ft.TextButton(
                                        "Ver Más",
                                        on_click=lambda e, cid=contact_id: page.go(f"/contact_detail/{cid}"),
                                        style=ft.ButtonStyle(color=ft.Colors.ORANGE_600)
                                    )
                                ],
                                spacing=5
                            ),
                        ),
                        margin=ft.margin.symmetric(vertical=5, horizontal=10)
                    )
                )

        return ft.View(
            "/contacts_list",
            [
                ft.AppBar(
                    title=ft.Text("Lista de Contactos"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/home")),
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.PERSON_ADD,
                            icon_color=ft.Colors.WHITE,
                            icon_size=24,
                            tooltip="Agregar Nuevo Contacto",
                            on_click=lambda e: page.go("/add_contact"),
                        )
                    ]
                ),
                ft.Column(
                    [
                        ft.ListView(
                            controls=contact_items,
                            expand=True,
                            padding=10,
                            spacing=10,
                        ),
                        footer_text_widget,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    # --- FIN NUEVA FUNCIONALIDAD: AGENDA DE CONTACTOS - LISTA DE CONTACTOS ---

    # --- NUEVA VISTA: DETALLE DE CONTACTO ---
    def contact_detail_view(contact_id):
        contact = get_contact_by_id_db(contact_id) # Obtener el contacto por su ID

        if not contact:
            # Manejar caso de contacto no encontrado
            return ft.View(
                f"/contact_detail/{contact_id}",
                [
                    ft.AppBar(
                        title=ft.Text("Contacto No Encontrado"),
                        center_title=True,
                        bgcolor=ft.Colors.ORANGE_700,
                        color=ft.Colors.WHITE,
                        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/contacts_list"))
                    ),
                    ft.Column(
                        [
                            ft.Container(expand=True),
                            ft.Text("El contacto solicitado no pudo ser encontrado.", size=16, color=ft.Colors.RED_500),
                            ft.Container(expand=True),
                            footer_text_widget,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER, # Esto es para el *contenido* de la Column si no hay `expand`
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True
                    )
                ]
            )

        # Mapeo de índices a nombres para facilitar la lectura
        # id (0), nombre (1), primer_apellido (2), segundo_apellido (3),
        # telefono (4), movil (5), email (6), direccion (7), actividad (8),
        # nota (9), empresa (10), sitio_web (11), capacidad_persona (12), participacion (13)

        # Construir el nombre completo para el título de la AppBar
        nombre_completo_titulo = f"{contact[1]} {contact[2]}"
        if contact[3]:
            nombre_completo_titulo += f" {contact[3]}"
        
        # Lista para almacenar todos los detalles del contacto para la tarjeta
        all_contact_details = []

        # Añadir cada campo si tiene valor, con iconos
        if contact[4]: # Telefono
            all_contact_details.append(ft.Text(f"📞 Teléfono: {contact[4]}", size=14, color=ft.Colors.BLACK87))
        if contact[5]: # Movil
            all_contact_details.append(ft.Text(f"📱 Móvil: {contact[5]}", size=14, color=ft.Colors.BLACK87))
        if contact[6]: # Email
            all_contact_details.append(ft.Text(f"📧 Email: {contact[6]}", size=14, color=ft.Colors.BLACK87))
        if contact[7]: # Dirección
            all_contact_details.append(ft.Text(f"📍 Dirección: {contact[7]}", size=14, color=ft.Colors.BLACK87))
        if contact[8]: # Actividad
            all_contact_details.append(ft.Text(f"⚙️ Actividad: {contact[8]}", size=14, color=ft.Colors.BLACK87))
        if contact[9]: # Nota
            all_contact_details.append(ft.Text(f"📝 Nota: {contact[9]}", size=14, color=ft.Colors.BLACK87))
        if contact[10]: # Empresa
            all_contact_details.append(ft.Text(f"🏢 Empresa: {contact[10]}", size=14, color=ft.Colors.BLACK87))
        if contact[11]: # Sitio Web
            all_contact_details.append(ft.Text(f"🌐 Sitio Web: {contact[11]}", size=14, color=ft.Colors.BLACK87))
        if contact[12]: # Capacidad de Persona
            all_contact_details.append(ft.Text(f"🏃 Capacidad: {contact[12]}", size=14, color=ft.Colors.BLACK87))
        if contact[13]: # Participación
            all_contact_details.append(ft.Text(f"🤝 Participación: {contact[13]}", size=14, color=ft.Colors.BLACK87))

        # --- MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - Diálogo de confirmación ---
        def confirm_delete_dialog(e):
            def delete_confirmed(e):
                success, message = delete_contact_db(contact_id)
                page.close(confirm_dialog) # Cerrar el diálogo
                if success:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(message, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREEN_600,
                        open=True
                    )
                    page.update()
                    page.go("/contacts_list") # Volver a la lista después de borrar
                else:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(message, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.RED_600,
                        open=True
                    )
                    page.update()

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar Eliminación"),
                content=ft.Text(f"¿Estás seguro de que deseas eliminar a {nombre_completo_titulo}? Esta acción no se puede deshacer."),
                actions=[
                    ft.TextButton("Sí, Eliminar", on_click=delete_confirmed, style=ft.ButtonStyle(color=ft.Colors.RED_500)),
                    ft.TextButton("Cancelar", on_click=lambda e: page.close(confirm_dialog)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()
        # --- FIN MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - Diálogo de confirmación ---

        return ft.View(
            f"/contact_detail/{contact_id}",
            [
                ft.AppBar(
                    title=ft.Text(nombre_completo_titulo),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/contacts_list")),
                    # --- MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - Botones en AppBar ---
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=ft.Colors.WHITE,
                            tooltip="Editar Contacto",
                            on_click=lambda e: page.go(f"/edit_contact/{contact_id}") # Navegar a la vista de edición
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_200, # Un rojo suave para que no sea tan brusco en la AppBar
                            tooltip="Eliminar Contacto",
                            on_click=confirm_delete_dialog # Llamar al diálogo de confirmación
                        ),
                    ]
                    # --- FIN MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - Botones en AppBar ---
                ),
                ft.Column(
                    [
                        ft.Container(expand=True), # Espacio flexible arriba
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column(
                                    [
                                        ft.Text("Detalles del Contacto", size=22, weight=ft.FontWeight.BOLD),
                                        ft.Divider(height=10, color=ft.Colors.ORANGE_200),
                                        *all_contact_details, # Desempaqueta todos los detalles
                                    ],
                                    spacing=8
                                )
                            ),
                            elevation=4,
                            margin=ft.margin.all(20), # Margen alrededor de la tarjeta para centrarla
                        ),
                        ft.Container(expand=True), # Espacio flexible abajo
                        footer_text_widget,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    scroll=ft.ScrollMode.ADAPTIVE # Por si los detalles son muchos en una pantalla pequeña
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # Esto es para el View, NO para la Column interna
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    # --- FIN NUEVA VISTA: DETALLE DE CONTACTO ---

    # --- MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - VISTA DE EDICIÓN ---
    def edit_contact_view(contact_id):
        contact = get_contact_by_id_db(contact_id)

        if not contact:
            return ft.View(
                f"/edit_contact/{contact_id}",
                [
                    ft.AppBar(title=ft.Text("Contacto No Encontrado"), bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE,
                              leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/contacts_list"))),
                    ft.Text("El contacto solicitado para edición no pudo ser encontrado.", color=ft.Colors.RED_500)
                ]
            )
        
        # Pre-llenar los campos con los datos existentes del contacto
        # id (0), nombre (1), primer_apellido (2), segundo_apellido (3),
        # telefono (4), movil (5), email (6), direccion (7), actividad (8),
        # nota (9), empresa (10), sitio_web (11), capacidad_persona (12), participacion (13)
        contact_nombre_input.value = contact[1]
        contact_primer_apellido_input.value = contact[2]
        contact_segundo_apellido_input.value = contact[3]
        contact_telefono_input.value = contact[4]
        contact_movil_input.value = contact[5]
        contact_email_input.value = contact[6]
        contact_direccion_input.value = contact[7]
        contact_actividad_dropdown.value = contact[8]
        contact_nota_input.value = contact[9]
        contact_empresa_input.value = contact[10]
        contact_sitio_web_input.value = contact[11]
        contact_capacidad_persona_dropdown.value = contact[12]
        contact_participacion_dropdown.value = contact[13]
        edit_contact_message_text.value = "" # Limpiar mensajes previos
        page.update() # Asegurar que los campos se actualicen en la UI

        def update_existing_contact(e):
            # Validar campos obligatorios
            if not all([contact_nombre_input.value, contact_primer_apellido_input.value]):
                edit_contact_message_text.value = "Nombre y Primer Apellido son obligatorios."
                edit_contact_message_text.color = ft.Colors.RED_500
                page.update()
                return
            
            # Validar formato de email si se proporciona
            if contact_email_input.value and not is_valid_email(contact_email_input.value):
                edit_contact_message_text.value = "Formato de correo electrónico inválido."
                edit_contact_message_text.color = ft.Colors.RED_500
                page.update()
                return

            updated_data = {
                'nombre': contact_nombre_input.value.strip(),
                'primer_apellido': contact_primer_apellido_input.value.strip(),
                'segundo_apellido': contact_segundo_apellido_input.value.strip(),
                'telefono': contact_telefono_input.value.strip(),
                'movil': contact_movil_input.value.strip(),
                'email': contact_email_input.value.strip(),
                'direccion': contact_direccion_input.value.strip(),
                'actividad': contact_actividad_dropdown.value if contact_actividad_dropdown.value else '',
                'nota': contact_nota_input.value.strip(),
                'empresa': contact_empresa_input.value.strip(),
                'sitio_web': contact_sitio_web_input.value.strip(),
                'capacidad_persona': contact_capacidad_persona_dropdown.value if contact_capacidad_persona_dropdown.value else '',
                'participacion': contact_participacion_dropdown.value if contact_participacion_dropdown.value else ''
            }

            success, message = update_contact_db(contact_id, updated_data)

            if success:
                edit_contact_message_text.value = message
                edit_contact_message_text.color = ft.Colors.GREEN_500
                page.update()
                # Opcional: Redirigir de nuevo a la vista de detalle o a la lista
                page.go(f"/contact_detail/{contact_id}") 
            else:
                edit_contact_message_text.value = message
                edit_contact_message_text.color = ft.Colors.RED_500
                page.update()

        return ft.View(
            f"/edit_contact/{contact_id}",
            [
                ft.AppBar(
                    title=ft.Text(f"Editar Contacto: {contact[1]} {contact[2]}"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go(f"/contact_detail/{contact_id}"))
                ),
                ft.Column( # Contenedor principal de la vista de editar contacto
                    [
                        ft.Text("Modificar Datos del Contacto", size=24, weight=ft.FontWeight.BOLD),
                        ft.ResponsiveRow([ft.Column([contact_nombre_input], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_primer_apellido_input], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_segundo_apellido_input], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([
                            ft.Column([contact_telefono_input], col={"xs": 12, "md": 6}),
                            ft.Column([contact_movil_input], col={"xs": 12, "md": 6}),
                        ]),
                        ft.ResponsiveRow([ft.Column([contact_email_input], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_direccion_input], col={"xs": 12, "md": 12})]),
                        ft.ResponsiveRow([ft.Column([contact_actividad_dropdown], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_nota_input], col={"xs": 12, "md": 12})]),
                        ft.ResponsiveRow([
                            ft.Column([contact_empresa_input], col={"xs": 12, "md": 6}),
                            ft.Column([contact_sitio_web_input], col={"xs": 12, "md": 6}),
                        ]),
                        ft.ResponsiveRow([ft.Column([contact_capacidad_persona_dropdown], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_participacion_dropdown], col={"xs": 12, "md": 6})]),
                        edit_contact_message_text,
                        ft.ResponsiveRow(
                            [ft.Column([ft.ElevatedButton("Actualizar Contacto", on_click=update_existing_contact, expand=True)], col={"xs": 12, "md": 6})],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Container(height=20),
                        footer_text_widget,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                    spacing=10
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    # --- FIN MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - VISTA DE EDICIÓN ---


    # --- Manejo de Rutas ---
    def route_change(route):
        page.views.clear()
        # Manejo de rutas estáticas
        if page.route == "/home":
            page.views.append(home_view())
        elif page.route == "/login":
            page.views.append(login_view())
        elif page.route == "/register":
            page.views.append(register_view())
        elif page.route == "/add_contact":
            page.views.append(add_contact_view())
        elif page.route == "/contacts_list":
            page.views.append(contacts_list_view())
        # --- Manejo de ruta dinámica para detalles de contacto ---
        elif page.route.startswith("/contact_detail/"):
            # Extraer el ID del contacto de la ruta
            parts = page.route.split("/")
            try:
                contact_id = int(parts[-1]) # El ID es el último segmento de la URL
                page.views.append(contact_detail_view(contact_id))
            except ValueError:
                # Manejar caso de ID no válido (ej. /contact_detail/abc)
                page.views.append(
                    ft.View(
                        "/error",
                        [
                            ft.AppBar(title=ft.Text("Error"), bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE),
                            ft.Text("ID de contacto no válido.", color=ft.Colors.RED_500),
                            ft.ElevatedButton("Volver a Contactos", on_click=lambda e: page.go("/contacts_list"))
                        ]
                    )
                )
        # --- MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - Manejo de ruta de edición ---
        elif page.route.startswith("/edit_contact/"):
            parts = page.route.split("/")
            try:
                contact_id = int(parts[-1])
                page.views.append(edit_contact_view(contact_id))
            except ValueError:
                page.views.append(
                    ft.View(
                        "/error",
                        [
                            ft.AppBar(title=ft.Text("Error"), bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE),
                            ft.Text("ID de contacto no válido para edición.", color=ft.Colors.RED_500),
                            ft.ElevatedButton("Volver a Contactos", on_click=lambda e: page.go("/contacts_list"))
                        ]
                    )
                )
        # --- FIN MODIFICACIÓN: BORRAR Y EDITAR CONTACTO - Manejo de ruta de edición ---
        else: # Ruta por defecto
            page.views.append(home_view())
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route) # Iniciar la aplicación en la ruta actual (por defecto /home)

# Ejecutar la aplicación
if __name__ == "__main__":
    ft.app(target=main)