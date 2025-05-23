import flet as ft
import sqlite3
import hashlib
import re
import time 
import datetime 
import os 

DATABASE_NAME = "users.db"
LOGGED_IN_USER = None 

# --- CHOICES PARA DROPDOWNS ---
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

QUIEN_HACE_COTIZACION_CHOICES = [
    ft.dropdown.Option(''),
    ft.dropdown.Option('Jenny Ceciliano Cordoba'),
    ft.dropdown.Option('Kenneth Ruiz Matamoros')
]

COTIZACION_ACTIVIDAD_CHOICES = [
    ft.dropdown.Option(''),
    ft.dropdown.Option('El Camino de Costa Rica'),
    ft.dropdown.Option('Parques Nacionales'),
    ft.dropdown.Option('Caminata Básica'),
    ft.dropdown.Option('Caminata Intermedia'),
    ft.dropdown.Option('Caminata Avanzada'),
    ft.dropdown.Option('Póliza'),
    ft.dropdown.Option('Productos'),
    ft.dropdown.Option('Servicios')
]

SINPE_CHOICES = [
    ft.dropdown.Option(''),
    ft.dropdown.Option('Jenny Ceciliano Cordoba-8652 9837'),
    ft.dropdown.Option('Kenneth Ruiz Matamoros-86227500'),
    ft.dropdown.Option('Jenny Ceciliano Cordoba-87984232')
]

# --- FUNCIONES DE BASE DE DATOS ---
def init_db():
    conn = None 
    try:
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_cotizacion TEXT UNIQUE NOT NULL, 
                quien_hace_cotizacion TEXT,
                fecha_automatica TEXT,
                dirigido_a TEXT,
                actividad TEXT,
                nombre_item TEXT,
                fecha_actividad TEXT,
                cantidad INTEGER,
                precio REAL,
                sinpe TEXT,
                nota TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        conn.commit()
        cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?)", ("last_quotation_number", "149"))
        conn.commit()
        print("DEBUG: Base de datos inicializada/actualizada correctamente.")
    except Exception as e:
        print(f"ERROR: Error durante la inicialización de la base de datos: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

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
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def delete_setting_db(key):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM app_settings WHERE key = ?", (key,))
    conn.commit()
    conn.close()

def get_hashed_password_db(identifier):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM usuarios WHERE usuario = ? OR email = ?", (identifier, identifier))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

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

def peek_next_quotation_number_db():
    """
    Obtiene el siguiente número de cotización sin incrementarlo en la base de datos.
    Formato: 000150, 000151, etc.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", ("last_quotation_number",))
    result = cursor.fetchone()
    conn.close()
    current_num = int(result[0]) if result and result[0].isdigit() else 149
    return f"{current_num + 1:06d}" 

def increment_and_get_quotation_number_db():
    """
    Incrementa el contador de cotizaciones en la DB y devuelve el nuevo número.
    Formato: 000150, 000151, etc.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", ("last_quotation_number",))
    current_num_str = cursor.fetchone()
    
    current_num = int(current_num_str[0]) if current_num_str and current_num_str[0].isdigit() else 149 
    next_num = current_num + 1
    
    cursor.execute("UPDATE app_settings SET value = ? WHERE key = ?", (str(next_num), "last_quotation_number"))
    conn.commit()
    conn.close()
    return f"{next_num:06d}" 

def add_cotizacion_db(cotizacion_data):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    print(f"DEBUG: Intentando guardar cotización: {cotizacion_data}")
    try:
        cursor.execute('''
            INSERT INTO cotizaciones (
                numero_cotizacion, 
                quien_hace_cotizacion, fecha_automatica, dirigido_a, actividad,
                nombre_item, fecha_actividad, cantidad, precio, sinpe, nota
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cotizacion_data['numero_cotizacion'], 
            cotizacion_data['quien_hace_cotizacion'],
            cotizacion_data['fecha_automatica'],
            cotizacion_data['dirigido_a'],
            cotizacion_data['actividad'],
            cotizacion_data['nombre_item'],
            cotizacion_data['fecha_actividad'],
            cotizacion_data['cantidad'],
            cotizacion_data['precio'],
            cotizacion_data['sinpe'],
            cotizacion_data['nota']
        ))
        conn.commit()
        print("DEBUG: Cotización guardada exitosamente en la DB.")
        return True, "Cotización guardada exitosamente."
    except Exception as e:
        print(f"ERROR: Error al guardar cotización: {e}")
        import traceback
        traceback.print_exc() 
        return False, f"Error al guardar cotización: {e}"
    finally:
        conn.close()
        print("DEBUG: Conexión a la DB cerrada para cotizaciones.")

def get_all_cotizaciones_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cotizaciones ORDER BY fecha_automatica DESC")
    cotizaciones = cursor.fetchall()
    conn.close()
    return cotizaciones

def get_cotizacion_by_id_db(cotizacion_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cotizaciones WHERE id = ?", (cotizacion_id,))
    cotizacion = cursor.fetchone()
    conn.close()
    return cotizacion

def delete_cotizacion_db(cotizacion_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cotizaciones WHERE id = ?", (cotizacion_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return True, "Cotización eliminada exitosamente."
        else:
            return False, "Cotización no encontrada para eliminar."
    except Exception as e:
        return False, f"Error al eliminar cotización: {e}"
    finally:
        conn.close()

def update_cotizacion_db(cotizacion_id, cotizacion_data):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE cotizaciones SET
                numero_cotizacion = ?, 
                quien_hace_cotizacion = ?, fecha_automatica = ?, dirigido_a = ?, actividad = ?,
                nombre_item = ?, fecha_actividad = ?, cantidad = ?, precio = ?, sinpe = ?, nota = ?
            WHERE id = ?
        ''', (
            cotizacion_data['numero_cotizacion'], 
            cotizacion_data['quien_hace_cotizacion'],
            cotizacion_data['fecha_automatica'],
            cotizacion_data['dirigido_a'],
            cotizacion_data['actividad'],
            cotizacion_data['nombre_item'],
            cotizacion_data['fecha_actividad'],
            cotizacion_data['cantidad'],
            cotizacion_data['precio'],
            cotizacion_data['sinpe'],
            cotizacion_data['nota'],
            cotizacion_id
        ))
        conn.commit()
        return True, "Cotización actualizada exitosamente."
    except Exception as e:
        return False, f"Error al actualizar cotización: {e}"
    finally:
        conn.close()

# --- FUNCIONES DE LA APLICACIÓN FLET ---
def main(page: ft.Page):
    global LOGGED_IN_USER 

    page.title = "App de Autenticación Flet"
    page.window_width = 400 
    page.window_height = 700

    # Inicializar la base de datos al inicio de la aplicación
    init_db()

    # Diálogo de confirmación global (para eliminaciones, etc.)
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

    # --- Funciones de Autenticación y Sesión ---
    def logout_user(e):
        global LOGGED_IN_USER
        LOGGED_IN_USER = None
        password_input.value = "" 
        login_message_text.value = "Sesión cerrada."
        login_message_text.color = ft.Colors.BLACK54
        
        print("DEBUG: Deseleccionando 'Recordar contraseña' y eliminando de DB al cerrar sesión.")
        set_setting_db("remember_me_checkbox", "False") 
        remember_me_checkbox.value = False 
        page.update() 
        page.go("/login") 

    # Pie de página común
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

    # --- Controles de Formulario de Cotización (Globales para fácil acceso) ---
    cotizacion_numero_input = ft.TextField( 
        label="Número de Cotización",
        read_only=True,
        expand=True,
    )
    cotizacion_quien_hace_dropdown = ft.Dropdown(
        label="Quien hace cotización",
        options=QUIEN_HACE_COTIZACION_CHOICES,
        expand=True,
    )
    cotizacion_fecha_automatica_input = ft.TextField(
        label="Fecha automática",
        value=datetime.date.today().strftime('%Y-%m-%d'), 
        read_only=True,
        expand=True,
    )
    cotizacion_dirigido_a_input = ft.TextField(
        label="Dirigido al NOMBRE DE USUARIO",
        value="", 
        expand=True,
    )
    cotizacion_actividad_dropdown = ft.Dropdown(
        label="ACTIVIDAD",
        options=COTIZACION_ACTIVIDAD_CHOICES,
        expand=True,
    )
    cotizacion_nombre_item_input = ft.TextField(
        label="Nombre de la Caminata, Producto o Servicio",
        expand=True,
    )
    
    def handle_date_selection(e):
        print(f"DEBUG: DatePicker on_change triggered. Value: {cotizacion_fecha_actividad_picker.value}")
        if cotizacion_fecha_actividad_picker.value:
            cotizacion_fecha_actividad_input.value = cotizacion_fecha_actividad_picker.value.strftime('%Y-%m-%d')
        else:
            cotizacion_fecha_actividad_input.value = ''
        cotizacion_fecha_actividad_picker.open = False 
        page.update()

    def handle_date_dismiss(e):
        print("DEBUG: DatePicker on_dismiss triggered.")
        cotizacion_fecha_actividad_picker.open = False 
        page.update()

    cotizacion_fecha_actividad_picker = ft.DatePicker(
        on_change=handle_date_selection,
        on_dismiss=handle_date_dismiss,
        first_date=datetime.datetime.now(),
        last_date=datetime.datetime(2030, 12, 31),
    )
    page.overlay.append(cotizacion_fecha_actividad_picker)

    cotizacion_fecha_actividad_input = ft.TextField(
        label="Fecha de la actividad",
        read_only=True,
        on_focus=lambda e: page.open(cotizacion_fecha_actividad_picker), 
        expand=True,
    )

    cotizacion_cantidad_input = ft.TextField(
        label="Cantidad", 
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
    )
    cotizacion_precio_input = ft.TextField(
        label="Costo", 
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string=""),
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
    )

    # Nuevo campo para el Total
    cotizacion_total_input = ft.TextField(
        label="Total",
        read_only=True,
        expand=True,
        value="₡0.00" # Valor inicial
    )

    # Función para calcular el total automáticamente
    def update_total(e):
        try:
            cantidad = float(cotizacion_cantidad_input.value or 0)
            precio = float(cotizacion_precio_input.value or 0)
            total = cantidad * precio
            cotizacion_total_input.value = f"₡{total:.2f}"
        except ValueError:
            cotizacion_total_input.value = "Error"
        page.update()

    # Asignar la función update_total a los eventos on_change de Cantidad y Costo
    cotizacion_cantidad_input.on_change = update_total
    cotizacion_precio_input.on_change = update_total

    cotizacion_sinpe_dropdown = ft.Dropdown(
        label="Sinpe",
        options=SINPE_CHOICES,
        expand=True,
    )
    cotizacion_nota_input = ft.TextField(
        label="Nota",
        multiline=True,
        min_lines=2,
        max_lines=5,
        expand=True,
    )

    def save_cotizacion(e):
        print("DEBUG: Iniciando save_cotizacion...")
        
        required_fields = {
            "Quien hace cotización": cotizacion_quien_hace_dropdown.value,
            "Dirigido al NOMBRE DE USUARIO": cotizacion_dirigido_a_input.value,
            "ACTIVIDAD": cotizacion_actividad_dropdown.value,
            "Nombre de la Caminata, Producto o Servicio": cotizacion_nombre_item_input.value,
            "Fecha de la actividad": cotizacion_fecha_actividad_input.value,
            "Cantidad": cotizacion_cantidad_input.value,
            "Costo": cotizacion_precio_input.value,
        }

        missing_fields = [label for label, value in required_fields.items() if not value]

        if missing_fields:
            error_message = "Por favor, completa los siguientes campos obligatorios: " + ", ".join(missing_fields) + "."
            page.snack_bar = ft.SnackBar(
                ft.Text(error_message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_600,
                open=True
            )
            page.update()
            print(f"DEBUG: Campos obligatorios incompletos: {missing_fields}")
            return

        try:
            cantidad = int(cotizacion_cantidad_input.value)
            precio = float(cotizacion_precio_input.value)
        except ValueError as ve:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Cantidad y Costo deben ser números válidos. Error: {ve}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_600,
                open=True
            )
            page.update()
            print(f"ERROR: Error de conversión de tipo: {ve}")
            return

        quotation_number_to_save = increment_and_get_quotation_number_db()

        cotizacion_data = {
            'numero_cotizacion': quotation_number_to_save, 
            'quien_hace_cotizacion': cotizacion_quien_hace_dropdown.value,
            'fecha_automatica': cotizacion_fecha_automatica_input.value,
            'dirigido_a': cotizacion_dirigido_a_input.value,
            'actividad': cotizacion_actividad_dropdown.value,
            'nombre_item': cotizacion_nombre_item_input.value.strip(),
            'fecha_actividad': cotizacion_fecha_actividad_input.value,
            'cantidad': cantidad,
            'precio': precio,
            'sinpe': cotizacion_sinpe_dropdown.value if cotizacion_sinpe_dropdown.value else '',
            'nota': cotizacion_nota_input.value.strip()
        }
        print(f"DEBUG: Datos de cotización a guardar: {cotizacion_data}")

        success, message = add_cotizacion_db(cotizacion_data)

        page.snack_bar = ft.SnackBar(
            ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600 if success else ft.Colors.RED_600,
            open=True
        )
        page.update()

        if success:
            cotizacion_quien_hace_dropdown.value = ''
            cotizacion_fecha_automatica_input.value = datetime.date.today().strftime('%Y-%m-%d')
            cotizacion_dirigido_a_input.value = LOGGED_IN_USER if LOGGED_IN_USER else ""
            cotizacion_actividad_dropdown.value = ''
            cotizacion_nombre_item_input.value = ''
            cotizacion_fecha_actividad_input.value = ''
            cotizacion_cantidad_input.value = ''
            cotizacion_precio_input.value = ''
            cotizacion_total_input.value = '₡0.00' # Resetear el total
            cotizacion_sinpe_dropdown.value = ''
            cotizacion_nota_input.value = ''
            cotizacion_numero_input.value = peek_next_quotation_number_db() 
            page.update()
            page.go("/quotations_list") 
        print("DEBUG: Finalizando save_cotizacion.")

    # --- VISTAS DE LA APLICACIÓN ---

    # Vista de Inicio (Home)
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
                    icon=ft.Icons.RECEIPT, 
                    icon_color=ft.Colors.WHITE,
                    icon_size=24,
                    tooltip="Ver Cotizaciones",
                    on_click=lambda e: page.go("/quotations_list"), 
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
                        ft.Container(height=30), 

                        ft.Card(
                            elevation=2,
                            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                            content=ft.Container(
                                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                                content=ft.Row(
                                    [
                                        ft.Text("Agenda", size=16, weight=ft.FontWeight.W_500, expand=True), 
                                        ft.Icon(name=ft.Icons.KEYBOARD_ARROW_RIGHT, color=ft.Colors.GREY_500),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                on_click=lambda e: page.go("/agenda")
                            )
                        ), 
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT), 

                        ft.Card(
                            elevation=2,
                            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                            content=ft.Container(
                                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                                content=ft.Row(
                                    [
                                        ft.Text("Ver Cotizaciones", size=16, weight=ft.FontWeight.W_500, expand=True), 
                                        ft.Icon(name=ft.Icons.KEYBOARD_ARROW_RIGHT, color=ft.Colors.GREY_500),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                on_click=lambda e: page.go("/quotations_list") 
                            )
                        ),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT), 

                        ft.Card(
                            elevation=2,
                            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                            content=ft.Container(
                                padding=ft.padding.symmetric(vertical=15, horizontal=15),
                                content=ft.Row(
                                    [
                                        ft.Text("Ver Contactos", size=16, weight=ft.FontWeight.W_500, expand=True), 
                                        ft.Icon(name=ft.Icons.KEYBOARD_ARROW_RIGHT, color=ft.Colors.GREY_500),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                on_click=lambda e: page.go("/contacts_list")
                            )
                        ),
                        
                        ft.Container(expand=True), 
                        footer_text_widget, 
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                    expand=True,
                    scroll=ft.ScrollMode.ADAPTIVE 
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.START, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # Vista de Formulario de Cotización
    def cotizacion_form_view():
        cotizacion_dirigido_a_input.value = LOGGED_IN_USER if LOGGED_IN_USER else ""
        cotizacion_fecha_automatica_input.value = datetime.date.today().strftime('%Y-%m-%d') 
        cotizacion_numero_input.value = peek_next_quotation_number_db() 
        cotizacion_total_input.value = '₡0.00' # Asegurar que el total se inicialice al cargar la vista

        return ft.View(
            "/cotizacion_form",
            [
                ft.AppBar(
                    title=ft.Text("Nueva Cotización"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/quotations_list")) 
                ),
                ft.Column( 
                    [
                        ft.Text("Crear Nueva Cotización", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK54),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                        ft.ResponsiveRow([ft.Column([cotizacion_numero_input], col={"xs": 12})]), 
                        ft.ResponsiveRow([ft.Column([cotizacion_quien_hace_dropdown], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_fecha_automatica_input], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_dirigido_a_input], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_actividad_dropdown], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_nombre_item_input], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_fecha_actividad_input], col={"xs": 12})]),
                        ft.ResponsiveRow([
                            ft.Column([cotizacion_cantidad_input], col={"xs": 12, "md": 6}),
                            ft.Column([cotizacion_precio_input], col={"xs": 12, "md": 6}),
                        ]),
                        ft.ResponsiveRow([ft.Column([cotizacion_total_input], col={"xs": 12})]), # Añadir el campo Total
                        ft.ResponsiveRow([ft.Column([cotizacion_sinpe_dropdown], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_nota_input], col={"xs": 12})]),
                        
                        ft.Container(height=20),
                        ft.ResponsiveRow(
                            [ft.Column([ft.ElevatedButton("Guardar Cotización", on_click=save_cotizacion, expand=True)], col={"xs": 12, "md": 6})],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    width=350,
                    scroll=ft.ScrollMode.ADAPTIVE, 
                    expand=True,
                ),
                footer_text_widget,
            ],
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # Vista de Agenda (Placeholder)
    def agenda_view():
        return ft.View(
            "/agenda",
            [
                ft.AppBar(
                    title=ft.Text("Agenda"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/home"))
                ),
                ft.Column(
                    [
                        ft.Container(expand=True),
                        ft.Text("Contenido de la Agenda (próximamente)", size=20, color=ft.Colors.BLACK54),
                        ft.Container(expand=True),
                        footer_text_widget,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # --- Controles de Autenticación (Globales) ---
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

    # Lógica de auto-inicio de sesión
    saved_username_email_from_db = get_setting_db("saved_username_email")
    remember_me_checked_from_db = get_setting_db("remember_me_checkbox") 
    
    print(f"DEBUG: Valor recuperado de DB al inicio: '{saved_username_email_from_db}'")
    print(f"DEBUG: Checkbox estado recuperado de DB al inicio: '{remember_me_checked_from_db}'")

    if saved_username_email_from_db and remember_me_checked_from_db == "True":
        username_email_input.value = saved_username_email_from_db
        remember_me_checkbox.value = True 
        print("DEBUG: username_email_input.value y remember_me_checkbox.value establecidos desde DB.")

        hashed_password_for_auto_login = get_hashed_password_db(saved_username_email_from_db)
        if hashed_password_for_auto_login:
            success, user_name = authenticate_user_db(saved_username_email_from_db, hashed_password_for_auto_login)
            if success:
                LOGGED_IN_USER = user_name
                print(f"DEBUG: Auto-inicio de sesión exitoso para: {user_name}")
                page.route = "/home" 
            else:
                print("DEBUG: Auto-inicio de sesión fallido (credenciales no válidas).")
        else:
            print("DEBUG: No se encontró hash de contraseña para auto-inicio de sesión.")
    else:
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
            
            if remember_me_checkbox.value:
                set_setting_db("saved_username_email", identifier)
                set_setting_db("remember_me_checkbox", "True") 
                print(f"DEBUG: '{identifier}' y 'True' guardados en DB.")
            else:
                set_setting_db("remember_me_checkbox", "False") 
                print("DEBUG: Valor eliminado de DB (checkbox desmarcado).")

            password_input.value = "" 
            page.update() 
            page.go("/home")
        else:
            login_message_text.value = "Usuario o contraseña incorrectos."
            login_message_text.color = ft.Colors.RED_500
            page.update()

    # Vista de Inicio de Sesión
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

    # --- Controles de Registro (Globales) ---
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

    # Vista de Registro
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

    # --- Controles de Contacto (Globales) ---
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

    # Vista de Agregar Contacto
    def add_contact_view():
        # Limpiar campos al cargar la vista
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

    # --- Controles de Lista de Contactos ---
    search_input = ft.TextField(
        label="Buscar contacto",
        hint_text="Buscar por nombre, teléfono, móvil, actividad o participación",
        prefix_icon=ft.Icons.SEARCH, 
        on_change=lambda e: update_contacts_list(e.control.value),
        expand=True
    )

    contacts_list_container = ft.Column(
        controls=[],
        expand=True,
        spacing=10,
        scroll=ft.ScrollMode.ADAPTIVE
    )

    def get_filtered_contacts_db(search_term=""):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        search_term_lower = f"%{search_term.lower()}%"
        
        query = """
            SELECT * FROM contactos WHERE
            LOWER(nombre) LIKE ? OR
            LOWER(primer_apellido) LIKE ? OR
            LOWER(segundo_apellido) LIKE ? OR
            telefono LIKE ? OR
            movil LIKE ? OR
            LOWER(actividad) LIKE ? OR
            LOWER(participacion) LIKE ?
            ORDER BY nombre, primer_apellido
        """
        cursor.execute(query, (search_term_lower, search_term_lower, search_term_lower, 
                               search_term_lower, search_term_lower, search_term_lower, search_term_lower))
        contacts = cursor.fetchall()
        conn.close()
        return contacts

    def update_contacts_list(search_term=""):
        contacts = get_filtered_contacts_db(search_term)
        contact_items = []
        if not contacts:
            contact_items.append(
                ft.Text("No hay contactos que coincidan con tu búsqueda.", italic=True, color=ft.Colors.BLACK54)
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
        contacts_list_container.controls = contact_items
        page.update()

    # Vista de Lista de Contactos
    def contacts_list_view():
        update_contacts_list("") 
        return ft.View(
            "/contacts_list",
            [
                ft.AppBar(
                    title=ft.Text("Lista de Contactos"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/home")),
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=search_input,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5)
                        ),
                        contacts_list_container,
                        # Nuevo botón para crear contacto
                        ft.Container(height=20), # Espacio
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [
                                        ft.ElevatedButton(
                                            "Crear Nuevo Contacto", # Texto del botón
                                            icon=ft.Icons.ADD,
                                            on_click=lambda e: page.go("/add_contact"), # Navega a la vista de agregar contacto
                                            bgcolor=ft.Colors.ORANGE_700,
                                            color=ft.Colors.WHITE,
                                            expand=True,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                                                padding=ft.padding.symmetric(vertical=15, horizontal=25) # Mismo padding que el botón de cotizaciones
                                            )
                                        )
                                    ],
                                    col={"xs": 12},
                                    alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        ft.Container(height=20), # Espacio
                        footer_text_widget,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # --- Controles de Lista de Cotizaciones ---
    quotation_search_input = ft.TextField(
        label="Buscar cotización",
        hint_text="Buscar por actividad, nombre de item o dirigido a",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: update_quotations_list(e.control.value),
        expand=True
    )

    quotations_list_container = ft.Column(
        controls=[],
        expand=True,
        spacing=10,
        scroll=ft.ScrollMode.ADAPTIVE
    )

    def get_filtered_cotizaciones_db(search_term=""):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        search_term_lower = f"%{search_term.lower()}%"
        
        query = """
            SELECT * FROM cotizaciones WHERE
            LOWER(numero_cotizacion) LIKE ? OR 
            LOWER(actividad) LIKE ? OR
            LOWER(nombre_item) LIKE ? OR
            LOWER(dirigido_a) LIKE ?
            ORDER BY fecha_automatica DESC
        """
        cursor.execute(query, (search_term_lower, search_term_lower, search_term_lower, search_term_lower))
        cotizaciones = cursor.fetchall()
        conn.close()
        return cotizaciones

    def update_quotations_list(search_term=""):
        cotizaciones = get_filtered_cotizaciones_db(search_term)
        quotation_items = []
        if not cotizaciones:
            quotation_items.append(
                ft.Text("No hay cotizaciones que coincidan con tu búsqueda.", italic=True, color=ft.Colors.BLACK54)
            )
        else:
            for cotizacion in cotizaciones:
                cotizacion_id = cotizacion[0]
                numero_cotizacion = cotizacion[1] 
                dirigido_a = cotizacion[3] 
                actividad = cotizacion[4] 
                nombre_item = cotizacion[5] 
                fecha_actividad = cotizacion[6] 

                quotation_items.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column(
                                [
                                    ft.Text(f"Cotización #: {numero_cotizacion}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800), 
                                    ft.Text(f"Para: {dirigido_a}", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Actividad: {actividad}", size=14, color=ft.Colors.GREY_700),
                                    ft.Text(f"Item: {nombre_item}", size=14, color=ft.Colors.GREY_700),
                                    ft.Text(f"Fecha de Actividad: {fecha_actividad}", size=14, color=ft.Colors.GREY_700),
                                    ft.Divider(height=5, color=ft.Colors.GREY_300),
                                    ft.TextButton(
                                        "Ver Detalles",
                                        on_click=lambda e, qid=cotizacion_id: page.go(f"/quotation_detail/{qid}"),
                                        style=ft.ButtonStyle(color=ft.Colors.ORANGE_600)
                                    )
                                ],
                                spacing=5
                            ),
                        ),
                        margin=ft.margin.symmetric(vertical=5, horizontal=10)
                    )
                )
        quotations_list_container.controls = quotation_items
        page.update()

    # Vista de Lista de Cotizaciones
    def quotations_list_view():
        print("DEBUG: Entrando a quotations_list_view()") # Debugging
        update_quotations_list("")
        return ft.View(
            "/quotations_list",
            [
                ft.AppBar(
                    title=ft.Text("Lista de Cotizaciones"),
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/home")),
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=quotation_search_input,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5)
                        ),
                        quotations_list_container,
                        # Nuevo botón para crear cotización
                        ft.Container(height=20), # Espacio
                        ft.ResponsiveRow(
                            [
                                ft.Column(
                                    [
                                        ft.ElevatedButton(
                                            "Crear Nueva Cotización",
                                            icon=ft.Icons.ADD,
                                            on_click=lambda e: page.go("/cotizacion_form"),
                                            bgcolor=ft.Colors.ORANGE_700,
                                            color=ft.Colors.WHITE,
                                            expand=True,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                                                # Modificado: Añadido padding horizontal
                                                padding=ft.padding.symmetric(vertical=15, horizontal=25) 
                                            )
                                        )
                                    ],
                                    col={"xs": 12},
                                    alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        ft.Container(height=20), # Espacio
                        footer_text_widget,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # --- Funciones de Diálogo ---
    def close_confirm_dialog(e_dialog): 
        confirm_dialog_global.open = False
        page.update()

    # --- Vistas de Detalle y Edición de Contacto ---
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

    # --- Vistas de Detalle y Edición de Cotización ---
    def quotation_detail_view(quotation_id):
        cotizacion = get_cotizacion_by_id_db(quotation_id)

        if not cotizacion:
            return ft.View(
                f"/quotation_detail/{quotation_id}",
                [
                    ft.AppBar(
                        title=ft.Text("Cotización No Encontrada"),
                        center_title=True,
                        bgcolor=ft.Colors.ORANGE_700,
                        color=ft.Colors.WHITE,
                        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/quotations_list"))
                    ),
                    ft.Column(
                        [
                            ft.Container(expand=True),
                            ft.Text("La cotización solicitada no pudo ser encontrada.", size=16, color=ft.Colors.RED_500),
                            ft.Container(expand=True),
                            footer_text_widget,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True
                    )
                ]
            )
        
        # Calcular el total para mostrar en el detalle
        try:
            cantidad = float(cotizacion[8])
            precio = float(cotizacion[9])
            total_calculado = cantidad * precio
            total_display = f"₡{total_calculado:.2f}"
        except (ValueError, TypeError):
            total_display = "N/A" # En caso de que los valores no sean numéricos

        details = [
            ft.Text(f"Número de Cotización: {cotizacion[1]}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
            ft.Text(f"Quien hace: {cotizacion[2]}", size=14, color=ft.Colors.BLACK87),
            ft.Text(f"Fecha automática: {cotizacion[3]}", size=14, color=ft.Colors.BLACK87),
            ft.Text(f"Dirigido a: {cotizacion[4]}", size=14, color=ft.Colors.BLACK87),
            ft.Text(f"Actividad: {cotizacion[5]}", size=14, color=ft.Colors.BLACK87),
            ft.Text(f"Nombre del Item: {cotizacion[6]}", size=14, color=ft.Colors.BLACK87),
            ft.Text(f"Fecha de Actividad: {cotizacion[7]}", size=14, color=ft.Colors.BLACK87),
            ft.Text(f"Cantidad: {cotizacion[8]}", size=14, color=ft.Colors.BLACK87), 
            ft.Text(f"Costo: ₡{cotizacion[9]:.2f}", size=14, color=ft.Colors.BLACK87), 
            ft.Text(f"Total: {total_display}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700), # Mostrar el total
            ft.Text(f"Sinpe: {cotizacion[10]}", size=14, color=ft.Colors.BLACK87),
            ft.Text(f"Nota: {cotizacion[11]}", size=14, color=ft.Colors.BLACK87),
        ]

        def confirm_delete_quotation_handler(e):
            def delete_confirmed(e_dialog):
                confirm_dialog_global.open = False
                page.update()
                success, message = delete_cotizacion_db(quotation_id)
                page.snack_bar = ft.SnackBar(
                    ft.Text(message, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_600 if success else ft.Colors.RED_600,
                    open=True
                )
                page.update()
                if success:
                    time.sleep(0.3)
                    page.go("/quotations_list")

            confirm_dialog_global.content.value = f"¿Estás seguro de que deseas eliminar esta cotización para {cotizacion[4]} (Cotización #: {cotizacion[1]})?"
            confirm_dialog_global.actions[0].on_click = delete_confirmed
            confirm_dialog_global.actions[1].on_click = close_confirm_dialog
            confirm_dialog_global.open = True
            page.update()

        return ft.View(
            f"/quotation_detail/{quotation_id}",
            [
                ft.AppBar(
                    title=ft.Text(f"Detalle Cotización: {cotizacion[4]}"), 
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/quotations_list")),
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=ft.Colors.WHITE,
                            tooltip="Editar Cotización",
                            on_click=lambda e: page.go(f"/edit_quotation/{quotation_id}")
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_200,
                            tooltip="Eliminar Cotización",
                            on_click=confirm_delete_quotation_handler
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
                                        ft.Text("Detalles de la Cotización", size=22, weight=ft.FontWeight.BOLD),
                                        ft.Divider(height=10, color=ft.Colors.ORANGE_200),
                                        *details,
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

    def edit_quotation_view(quotation_id):
        cotizacion = get_cotizacion_by_id_db(quotation_id)

        if not cotizacion:
            return ft.View(
                f"/edit_quotation/{quotation_id}",
                [
                    ft.AppBar(title=ft.Text("Cotización No Encontrada"), bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE,
                              leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/quotations_list"))),
                    ft.Text("ID de cotización no válido para edición.", color=ft.Colors.RED_500)
                ]
            )

        cotizacion_numero_input.value = cotizacion[1] if cotizacion[1] else '' 
        cotizacion_quien_hace_dropdown.value = cotizacion[2] if cotizacion[2] else ''
        cotizacion_fecha_automatica_input.value = cotizacion[3] if cotizacion[3] else ''
        cotizacion_dirigido_a_input.value = cotizacion[4] if cotizacion[4] else ''
        cotizacion_actividad_dropdown.value = cotizacion[5] if cotizacion[5] else ''
        cotizacion_nombre_item_input.value = cotizacion[6] if cotizacion[6] else ''
        cotizacion_fecha_actividad_input.value = cotizacion[7] if cotizacion[7] else ''
        cotizacion_cantidad_input.value = str(cotizacion[8]) if cotizacion[8] else ''
        cotizacion_precio_input.value = str(cotizacion[9]) if cotizacion[9] else ''
        cotizacion_sinpe_dropdown.value = cotizacion[10] if cotizacion[10] else ''
        cotizacion_nota_input.value = cotizacion[11] if cotizacion[11] else ''
        
        # Calcular y establecer el total inicial al cargar la vista de edición
        try:
            cantidad = float(cotizacion_cantidad_input.value or 0)
            precio = float(cotizacion_precio_input.value or 0)
            total = cantidad * precio
            cotizacion_total_input.value = f"₡{total:.2f}"
        except ValueError:
            cotizacion_total_input.value = "Error"

        page.update()

        def update_existing_quotation(e):
            if not all([cotizacion_quien_hace_dropdown.value, cotizacion_dirigido_a_input.value,
                        cotizacion_actividad_dropdown.value, cotizacion_nombre_item_input.value,
                        cotizacion_fecha_actividad_input.value, cotizacion_cantidad_input.value,
                        cotizacion_precio_input.value]):
                page.snack_bar = ft.SnackBar(
                    ft.Text("Por favor, completa todos los campos obligatorios para la cotización.", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_600,
                    open=True
                )
                page.update()
                return
            
            try:
                cantidad = int(cotizacion_cantidad_input.value)
                precio = float(cotizacion_precio_input.value)
            except ValueError:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Cantidad y Costo deben ser números válidos.", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_600,
                    open=True
                )
                page.update()
                return

            updated_data = {
                'numero_cotizacion': cotizacion_numero_input.value, 
                'quien_hace_cotizacion': cotizacion_quien_hace_dropdown.value,
                'fecha_automatica': cotizacion_fecha_automatica_input.value,
                'dirigido_a': cotizacion_dirigido_a_input.value,
                'actividad': cotizacion_actividad_dropdown.value,
                'nombre_item': cotizacion_nombre_item_input.value.strip(),
                'fecha_actividad': cotizacion_fecha_actividad_input.value,
                'cantidad': cantidad,
                'precio': precio,
                'sinpe': cotizacion_sinpe_dropdown.value if cotizacion_sinpe_dropdown.value else '',
                'nota': cotizacion_nota_input.value.strip()
            }

            success, message = update_cotizacion_db(quotation_id, updated_data)

            page.snack_bar = ft.SnackBar(
                ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_600 if success else ft.Colors.RED_600,
                open=True
            )
            page.update()

            if success:
                page.go(f"/quotation_detail/{quotation_id}")

        return ft.View(
            f"/edit_quotation/{quotation_id}",
            [
                ft.AppBar(
                    title=ft.Text(f"Editar Cotización: {cotizacion[4]}"), 
                    center_title=True,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go(f"/quotation_detail/{quotation_id}"))
                ),
                ft.Column(
                    [
                        ft.Text("Modificar Datos de la Cotización", size=24, weight=ft.FontWeight.BOLD),
                        ft.ResponsiveRow([ft.Column([cotizacion_numero_input], col={"xs": 12})]), 
                        ft.ResponsiveRow([ft.Column([cotizacion_quien_hace_dropdown], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_fecha_automatica_input], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_dirigido_a_input], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_actividad_dropdown], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_nombre_item_input], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_fecha_actividad_input], col={"xs": 12})]),
                        ft.ResponsiveRow([
                            ft.Column([cotizacion_cantidad_input], col={"xs": 12, "md": 6}),
                            ft.Column([cotizacion_precio_input], col={"xs": 12, "md": 6}),
                        ]),
                        ft.ResponsiveRow([ft.Column([cotizacion_total_input], col={"xs": 12})]), # Añadir el campo Total
                        ft.ResponsiveRow([ft.Column([cotizacion_sinpe_dropdown], col={"xs": 12})]),
                        ft.ResponsiveRow([ft.Column([cotizacion_nota_input], col={"xs": 12})]),
                        ft.Container(height=20),
                        ft.ResponsiveRow(
                            [ft.Column([ft.ElevatedButton("Actualizar Cotización", on_click=update_existing_quotation, expand=True)], col={"xs": 12, "md": 6})],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Container(expand=True),
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

    # --- Manejo de Rutas ---
    def route_change(route):
        page.views.clear()
        # Restablecer el FAB para todas las vistas primero
        page.floating_action_button = None 
        
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
            # Configurar FAB para Agregar Contacto
            page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.ADD, 
                on_click=lambda e: page.go("/add_contact"),
                bgcolor=ft.Colors.ORANGE_700,
                tooltip="Agregar Nuevo Contacto (FAB)" # Cambiado el tooltip para diferenciar
            )
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
        elif page.route == "/quotations_list":
            print("DEBUG: La ruta actual es /quotations_list. Configurando FAB para Nueva Cotización.") # Debugging
            page.views.append(quotations_list_view())
            # Se mantiene el FAB, pero ahora hay un botón adicional dentro de la vista.
            page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                on_click=lambda e: page.go("/cotizacion_form"), 
                bgcolor=ft.Colors.ORANGE_700,
                tooltip="Crear Nueva Cotización (FAB)" # Cambiado el tooltip para diferenciar
            )
        elif page.route.startswith("/quotation_detail/"):
            parts = page.route.split("/")
            try:
                quotation_id = int(parts[-1])
                page.views.append(quotation_detail_view(quotation_id))
            except ValueError:
                page.views.append(
                    ft.View(
                        "/error",
                        [
                            ft.AppBar(title=ft.Text("Error"), bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE),
                            ft.Text("ID de cotización no válido.", color=ft.Colors.RED_500),
                            ft.ElevatedButton("Volver a Cotizaciones", on_click=lambda e: page.go("/quotations_list"))
                        ]
                    )
                )
        elif page.route.startswith("/edit_quotation/"):
            parts = page.route.split("/")
            try:
                quotation_id = int(parts[-1])
                page.views.append(edit_quotation_view(quotation_id))
            except ValueError:
                page.views.append(
                    ft.View(
                        "/error",
                        [
                            ft.AppBar(title=ft.Text("Error"), bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE),
                            ft.Text("ID de cotización no válido para edición.", color=ft.Colors.RED_500),
                            ft.ElevatedButton("Volver a Cotizaciones", on_click=lambda e: page.go("/quotations_list"))
                        ]
                    )
                )
        elif page.route == "/agenda":
            page.views.append(agenda_view())
        elif page.route == "/cotizacion_form":
            page.views.append(cotizacion_form_view())
        else: 
            page.views.append(home_view())
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Establecer la ruta inicial basada en el estado de la sesión
    if LOGGED_IN_USER:
        page.go("/home")
    else:
        page.go("/login")

if __name__ == "__main__":
    ft.app(target=main)
