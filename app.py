import flet as ft
import sqlite3
import hashlib
import re # Para validación de email

DATABASE_NAME = "users.db"
LOGGED_IN_USER = None # Variable global para simular el usuario logueado

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
        return True, user[0] # Retorna True y el nombre de usuario
    return False, None

def is_valid_email(email):
    # Regex básica para validar email
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def main(page: ft.Page):
    page.title = "App de Autenticación Flet"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 400 # Ancho para simular móvil
    page.window_height = 700

    init_db()

    # --- Controles Compartidos ---
    app_bar_user_icon = ft.IconButton(
        icon=ft.Icons.ACCOUNT_CIRCLE,
        icon_size=30,
        tooltip="Acceder/Ver perfil",
        on_click=lambda e: page.go("/login"), # Siempre lleva al login por ahora
    )

    # --- Vistas ---

    # 1. Home View
    def home_view():
        return ft.View(
            "/home",
            [
                ft.AppBar(
                    title=ft.Text(""), # Título vacío para una barra más limpia
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    actions=[app_bar_user_icon]
                ),
                ft.Column(
                    [
                        # ELIMINADO: ft.Text(f"¡Hola, {LOGGED_IN_USER if LOGGED_IN_USER else 'Invitado'}!", size=30, weight=ft.FontWeight.BOLD),
                        # ELIMINADO: ft.Text("Esta es la página de inicio.", size=16),
                        # ELIMINADO: ft.ElevatedButton("Ir a Login", on_click=lambda e: page.go("/login"), visible=LOGGED_IN_USER is None),
                        ft.FilledButton("Cerrar Sesión", on_click=logout_user,
                                        visible=LOGGED_IN_USER is not None, # Mostrar si está logueado
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_500)),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # 2. Login View
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
            # Limpiar campos después de un login exitoso
            username_email_input.value = ""
            password_input.value = ""
            page.update()
            page.go("/home")
        else:
            login_message_text.value = "Usuario o contraseña incorrectos."
            login_message_text.color = ft.Colors.RED_500
            page.update()

    def logout_user(e):
        global LOGGED_IN_USER
        LOGGED_IN_USER = None
        username_email_input.value = ""
        password_input.value = ""
        login_message_text.value = "Sesión cerrada."
        login_message_text.color = ft.Colors.BLACK54
        page.update()
        page.go("/login") # Redirigir al login después de cerrar sesión


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
                        ft.Text("Inicia Sesión en tu Cuenta", size=24, weight=ft.FontWeight.BOLD),
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [username_email_input],
                                    col={"xs": 12, "md": 6},
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [password_input],
                                    col={"xs": 12, "md": 6},
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [remember_me_checkbox],
                                    col={"xs": 12, "md": 6},
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        login_message_text,
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [ft.ElevatedButton("Iniciar Sesión", on_click=login_user, expand=True)],
                                    col={"xs": 12, "md": 6},
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [
                                        ft.TextButton(
                                            "¿No tienes cuenta? Regístrate aquí.",
                                            on_click=lambda e: page.go("/register")
                                        )
                                    ],
                                    col={"xs": 12, "md": 6},
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                    spacing=15
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # 3. Register View
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
            # Limpiar campos
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
                            [
                                ft.Column(
                                    [ft.ElevatedButton("Registrarse", on_click=register_user, expand=True)],
                                    col={"xs": 12, "md": 6},
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [
                                        ft.TextButton(
                                            "¿Ya tienes cuenta? Inicia Sesión.",
                                            on_click=lambda e: page.go("/login")
                                        )
                                    ],
                                    col={"xs": 12, "md": 6},
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    spacing=15
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # --- Manejo de Rutas ---
    def route_change(route):
        page.views.clear()
        if page.route == "/home":
            page.views.append(home_view())
        elif page.route == "/login":
            page.views.append(login_view())
        elif page.route == "/register":
            page.views.append(register_view())
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