import flet as ft
import sqlite3
import hashlib
import re
import time 

DATABASE_NAME = "users.db"
LOGGED_IN_USER = None 

ACTIVIDADES_CHOICES = [
    ft.dropdown.Option(''), 
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
    ft.dropdown.Option(''), 
    ft.dropdown.Option('Rápido'),
    ft.dropdown.Option('Intermedio'),
    ft.dropdown.Option('Básico'),
    ft.dropdown.Option('Iniciante')
]

PARTICIPACION_CHOICES = [
    ft.dropdown.Option(''), 
    ft.dropdown.Option('Solo de La Tribu'),
    ft.dropdown.Option('constante'),
    ft.dropdown.Option('inconstante'),
    ft.dropdown.Option('El Camino de Costa Rica'),
    ft.dropdown.Option('Parques Nacionales'),
    ft.dropdown.Option('Paseo | Recreativo'),
    ft.dropdown.Option('Revisar/Eliminar')
]

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
    ### CAMBIO IMPORTANTE: Nueva tabla para configuraciones de la aplicación (incluye "Recordar contraseña")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

### CAMBIO IMPORTANTE: Nuevas funciones para interactuar con la tabla app_settings
def get_setting_db(key):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_setting_db(key, value):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # INSERT OR REPLACE inserta si no existe, o actualiza si la clave ya existe
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def delete_setting_db(key):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM app_settings WHERE key = ?", (key,))
    conn.commit()
    conn.close()

### CAMBIO IMPORTANTE: Nueva función para obtener el hash de la contraseña de un usuario
def get_hashed_password_db(identifier):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM usuarios WHERE usuario = ? OR email = ?", (identifier, identifier))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
### FIN CAMBIO IMPORTANTE

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
        return True, user[0] 
    return False, None

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

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

def delete_contact_db(contact_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    print(f"DEBUG: Intentando eliminar contacto con ID: {contact_id}") 
    try:
        cursor.execute("DELETE FROM contactos WHERE id = ?", (contact_id,))
        conn.commit()
        print(f"DEBUG: Commit realizado para ID: {contact_id}. Filas afectadas: {cursor.rowcount}") 
        if cursor.rowcount > 0:
            return True, "Contacto eliminado exitosamente."
        else:
            return False, "Contacto no encontrado para eliminar." 
    except Exception as e:
        print(f"ERROR: Error al eliminar contacto con ID {contact_id}: {e}") 
        return False, f"Error al eliminar contacto: {e}"
    finally:
        conn.close()
        print(f"DEBUG: Conexión a la DB cerrada.") 

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

def main(page: ft.Page):
    page.title = "App de Autenticación Flet"
    page.window_width = 400 
    page.window_height = 700

    init_db()

    confirm_dialog_global = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Eliminación"),
        content=ft.Text(""), 
        actions=[
            ft.TextButton("Sí, Eliminar", style=ft.ButtonStyle(color=ft.Colors.RED_500)), 
            ft.TextButton("Cancelar"), 
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(confirm_dialog_global) 

    def logout_user(e):
        global LOGGED_IN_USER
        LOGGED_IN_USER = None
        username_email_input.value = ""
        password_input.value = ""
        login_message_text.value = "Sesión cerrada."
        login_message_text.color = ft.Colors.BLACK54
        
        ### CAMBIO IMPORTANTE: Eliminar de la DB al cerrar sesión
        print("DEBUG: Deseleccionando 'Recordar contraseña' y eliminando de DB al cerrar sesión.")
        delete_setting_db("saved_username_email") 
        set_setting_db("remember_me_checkbox", "False") # Asegurarse de que el estado del checkbox también se guarde como False
        remember_me_checkbox.value = False 
        page.update() 
        page.go("/login") 

    footer_text_widget = ft.Container(
        content=ft.Row(
            [
                ft.Text("HECHO CON", color=ft.Colors.ORANGE_700, size=12, weight=ft.FontWeight.BOLD),
                ft.Icon(name=ft.Icons.FAVORITE, color=ft.Colors.ORANGE_700, size=12), 
                ft.Text("LA TRIBU DE LOS LIBRES", color=ft.Colors.ORANGE_700, size=12, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER, 
            spacing=3, 
        ),
        alignment=ft.alignment.bottom_center, 
        padding=ft.padding.only(bottom=10), 
    )

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
            app_bar_actions.append(
                ft.IconButton(
                    icon=ft.Icons.CONTACTS, 
                    icon_color=ft.Colors.WHITE,
                    icon_size=24,
                    tooltip="Ver Contactos",
                    on_click=lambda e: page.go("/contacts_list"), 
                )
            )
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
                ft.Column( 
                    [
                        ft.Container(expand=True), 
                        footer_text_widget, 
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True 
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # Definimos los TextField y Checkbox ANTES de la función login_view
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

    ### CAMBIO IMPORTANTE: Cargar el valor guardado al inicio de la aplicación desde SQLite
    saved_username_email_from_db = get_setting_db("saved_username_email")
    # Se guarda el estado del checkbox como string "True" o "False"
    remember_me_checked_from_db = get_setting_db("remember_me_checkbox") 
    
    print(f"DEBUG: Valor recuperado de DB al inicio: '{saved_username_email_from_db}'")
    print(f"DEBUG: Checkbox estado recuperado de DB al inicio: '{remember_me_checked_from_db}'")

    # Auto-login logic
    if saved_username_email_from_db and remember_me_checked_from_db == "True":
        username_email_input.value = saved_username_email_from_db
        remember_me_checkbox.value = True 
        print("DEBUG: username_email_input.value y remember_me_checkbox.value establecidos desde DB.")

        # Attempt to auto-authenticate
        hashed_password_for_auto_login = get_hashed_password_db(saved_username_email_from_db)
        if hashed_password_for_auto_login:
            success, user_name = authenticate_user_db(saved_username_email_from_db, hashed_password_for_auto_login)
            if success:
                global LOGGED_IN_USER
                LOGGED_IN_USER = user_name
                print(f"DEBUG: Auto-inicio de sesión exitoso para: {user_name}")
                # ### CAMBIO IMPORTANTE: Establecer la ruta de la página en lugar de hacer page.go() y return
                page.route = "/home" 
            else:
                print("DEBUG: Auto-inicio de sesión fallido (credenciales no válidas).")
                # Si falla el auto-login, la ruta seguirá siendo la predeterminada (login)
        else:
            print("DEBUG: No se encontró hash de contraseña para auto-inicio de sesión.")
            # Si no hay hash, la ruta seguirá siendo la predeterminada (login)
    else:
        # Asegurarse de que estén vacíos/desmarcados si no hay datos guardados o el checkbox no estaba marcado
        username_email_input.value = "" 
        remember_me_checkbox.value = False 
        print("DEBUG: No se encontró un valor guardado o checkbox desmarcado en DB.")


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

        print(f"DEBUG: remember_me_checkbox.value en login_user (antes de guardar): {remember_me_checkbox.value}") 

        if success:
            LOGGED_IN_USER = user_name
            login_message_text.value = "Inicio de sesión exitoso!"
            login_message_text.color = ft.Colors.GREEN_500
            
            ### CAMBIO IMPORTANTE: Guardar o eliminar el valor basado en el checkbox en SQLite
            if remember_me_checkbox.value:
                set_setting_db("saved_username_email", identifier)
                set_setting_db("remember_me_checkbox", "True") # Guardar como string "True"
                print(f"DEBUG: '{identifier}' y 'True' guardados en DB.")
            else:
                # Si el checkbox no está marcado, eliminamos el usuario guardado y marcamos el checkbox como False
                delete_setting_db("saved_username_email")
                set_setting_db("remember_me_checkbox", "False") # Guardar como string "False"
                print("DEBUG: Valor eliminado de DB (checkbox desmarcado).")

            # Limpiamos solo la contraseña, el usuario/email se mantiene si es recordado
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
                ft.Column( 
                    [
                        ft.Container(expand=True), 
                        ft.Column( 
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
                                    [ft.Column([ft.TextButton("¿No tienes cuenta? Regístrate aquí.", on_click=lambda e: page.go("/register"))], col={"xs": 12, "md": 6}, horizontal_alignment=ft.MainAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        ft.Container(expand=True), 
                        footer_text_widget, 
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True, 
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

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
                ft.Column( 
                    [
                        ft.Container(expand=True), 
                        ft.Column( 
                            [
                                ft.Text("Crea una Nueva Cuenta", size=24, weight=ft.FontWeight.BOLD),
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
                                    [ft.Column([ft.TextButton("¿Ya tienes cuenta? Inicia Sesión.", on_click=lambda e: page.go("/login"))], col={"xs": 12, "md": 6}, horizontal_alignment=ft.MainAxisAlignment.CENTER)],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                            scroll=ft.ScrollMode.ADAPTIVE,
                        ),
                        ft.Container(expand=True), 
                        footer_text_widget, 
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True, 
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

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
        if not all([contact_nombre_input.value, contact_primer_apellido_input.value]):
            add_contact_message_text.value = "Nombre y Primer Apellido son obligatorios."
            add_contact_message_text.color = ft.Colors.RED_500
            page.update()
            return
        
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
            page.update()
        else:
            add_contact_message_text.value = message
            add_contact_message_text.color = ft.Colors.RED_500
            page.update()

    def add_contact_view():
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
        page.update() 

        return ft.View(
            "/add_contact",
            [
                ft.AppBar(
                    title=ft.Text("Agregar Nuevo Contacto"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/contacts_list")) 
                ),
                ft.Column( 
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
                        ft.ResponsiveRow([ft.Column([contact_direccion_input], col={"xs": 12, "md": 12})]), 
                        ft.ResponsiveRow([ft.Column([contact_actividad_dropdown], col={"xs": 12, "md": 6})]),
                        ft.ResponsiveRow([ft.Column([contact_nota_input], col={"xs": 12, "md": 12})]), 
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

    def contacts_list_view():
        contacts = get_all_contacts_db() 

        contact_items = []
        if not contacts:
            contact_items.append(
                ft.Text("No hay contactos aún. ¡Agrega uno!", italic=True, color=ft.Colors.BLACK54)
            )
        else:
            for contact in contacts:
                contact_id = contact[0] 
                nombre_completo = f"{contact[1]} {contact[2]}" 
                if contact[3]: 
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
                                    ft.Divider(height=5, color=ft.Colors.GREY_300), 
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

    def close_confirm_dialog(e_dialog): 
        confirm_dialog_global.open = False
        page.update()

    def contact_detail_view(contact_id):
        contact = get_contact_by_id_db(contact_id)

        if not contact:
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
                        alignment=ft.MainAxisAlignment.CENTER, 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True
                    )
                ]
            )

        nombre_completo_titulo = f"{contact[1]} {contact[2]}"
        if contact[3]:
            nombre_completo_titulo += f" {contact[3]}"
        
        all_contact_details = []

        if contact[4]: 
            all_contact_details.append(ft.Text(f"📞 Teléfono: {contact[4]}", size=14, color=ft.Colors.BLACK87))
        if contact[5]: 
            all_contact_details.append(ft.Text(f"📱 Móvil: {contact[5]}", size=14, color=ft.Colors.BLACK87))
        if contact[6]: 
            all_contact_details.append(ft.Text(f"📧 Email: {contact[6]}", size=14, color=ft.Colors.BLACK87))
        if contact[7]: 
            all_contact_details.append(ft.Text(f"📍 Dirección: {contact[7]}", size=14, color=ft.Colors.BLACK87))
        if contact[8]: 
            all_contact_details.append(ft.Text(f"⚙️ Actividad: {contact[8]}", size=14, color=ft.Colors.BLACK87))
        if contact[9]: 
            all_contact_details.append(ft.Text(f"📝 Nota: {contact[9]}", size=14, color=ft.Colors.BLACK87))
        if contact[10]: 
            all_contact_details.append(ft.Text(f"🏢 Empresa: {contact[10]}", size=14, color=ft.Colors.BLACK87))
        if contact[11]: 
            all_contact_details.append(ft.Text(f"🌐 Sitio Web: {contact[11]}", size=14, color=ft.Colors.BLACK87))
        if contact[12]: 
            all_contact_details.append(ft.Text(f"🏃 Capacidad: {contact[12]}", size=14, color=ft.Colors.BLACK87))
        if contact[13]: 
            all_contact_details.append(ft.Text(f"🤝 Participación: {contact[13]}", size=14, color=ft.Colors.BLACK87))

        def confirm_delete_dialog_handler(e):
            print(f"DEBUG: confirm_delete_dialog_handler llamado para ID: {contact_id}") 
            
            def delete_confirmed(e_dialog): 
                print(f"DEBUG: delete_confirmed llamado para ID: {contact_id}") 
                confirm_dialog_global.open = False 
                page.update() 

                success, message = delete_contact_db(contact_id) 

                page.snack_bar = ft.SnackBar(
                    ft.Text(message, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_600 if success else ft.Colors.RED_600,
                    open=True
                )
                page.update() 

                if success:
                    time.sleep(0.3) 
                    page.go("/contacts_list") 

            confirm_dialog_global.content.value = f"¿Estás seguro de que deseas eliminar a {nombre_completo_titulo}? Esta acción no se puede deshacer."
            confirm_dialog_global.actions[0].on_click = delete_confirmed 
            confirm_dialog_global.actions[1].on_click = close_confirm_dialog
            
            confirm_dialog_global.open = True
            page.update() 

        return ft.View(
            f"/contact_detail/{contact_id}",
            [
                ft.AppBar(
                    title=ft.Text(nombre_completo_titulo),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/contacts_list")),
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=ft.Colors.WHITE,
                            tooltip="Editar Contacto",
                            on_click=lambda e: page.go(f"/edit_contact/{contact_id}") 
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_200, 
                            tooltip="Eliminar Contacto",
                            on_click=confirm_delete_dialog_handler 
                        ),
                    ]
                ),
                ft.Column(
                    [
                        ft.Container(expand=True), 
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column(
                                    [
                                        ft.Text("Detalles del Contacto", size=22, weight=ft.FontWeight.BOLD),
                                        ft.Divider(height=10, color=ft.Colors.ORANGE_200),
                                        *all_contact_details, 
                                    ],
                                    spacing=8
                                )
                            ),
                            elevation=4,
                            margin=ft.margin.all(20), 
                        ),
                        ft.Container(expand=True), 
                        footer_text_widget,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    scroll=ft.ScrollMode.ADAPTIVE 
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def edit_contact_view(contact_id):
        contact = get_contact_by_id_db(contact_id)

        if not contact:
            return ft.View(
                f"/edit_contact/{contact_id}",
                [
                    ft.AppBar(title=ft.Text("Contacto No Encontrado"), bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE,
                              leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/contacts_list"))),
                    ft.Text("ID de contacto no válido para edición.", color=ft.Colors.RED_500)
                ]
            )
        
        contact_nombre_input.value = contact[1]
        contact_primer_apellido_input.value = contact[2]
        contact_segundo_apellido_input.value = contact[3] if contact[3] else "" 
        contact_telefono_input.value = contact[4] if contact[4] else ""
        contact_movil_input.value = contact[5] if contact[5] else ""
        contact_email_input.value = contact[6] if contact[6] else ""
        contact_direccion_input.value = contact[7] if contact[7] else ""
        contact_actividad_dropdown.value = contact[8] if contact[8] else ""
        contact_nota_input.value = contact[9] if contact[9] else ""
        contact_empresa_input.value = contact[10] if contact[10] else ""
        contact_sitio_web_input.value = contact[11] if contact[11] else ""
        contact_capacidad_persona_dropdown.value = contact[12] if contact[12] else ""
        contact_participacion_dropdown.value = contact[13] if contact[13] else ""
        edit_contact_message_text.value = "" 
        page.update() 

        def update_existing_contact(e):
            if not all([contact_nombre_input.value, contact_primer_apellido_input.value]):
                edit_contact_message_text.value = "Nombre y Primer Apellido son obligatorios."
                edit_contact_message_text.color = ft.Colors.RED_500
                page.update()
                return
            
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
                ft.Column( 
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

    def route_change(route):
        page.views.clear()
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
        elif page.route.startswith("/contact_detail/"):
            parts = page.route.split("/")
            try:
                contact_id = int(parts[-1])
                page.views.append(contact_detail_view(contact_id))
            except ValueError:
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
        else: 
            page.views.append(home_view())
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route) 

if __name__ == "__main__":
    ft.app(target=main)