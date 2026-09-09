"""
StockPro v1.0 - Launcher de Escritorio
=======================================
Este script inicia el servidor Django en segundo plano y abre
una ventana de escritorio nativa usando pywebview.
Al cerrar la ventana, el servidor se detiene automáticamente.
"""
import os
import sys
import threading
import socket
import time
import ctypes
import traceback

# Determinar la ruta base (funciona tanto en desarrollo como empaquetado con PyInstaller)
if getattr(sys, 'frozen', False):
    # Ejecutándose desde el .exe empaquetado
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Ejecutándose desde el script Python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False) and 'debug' not in os.path.basename(sys.executable).lower():
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)

# Agregar el directorio base al path de Python
sys.path.insert(0, BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemaDeStock.settings')


def find_free_port():
    """Busca un puerto libre en el sistema para evitar conflictos."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_for_server(port, timeout=15):
    """Espera hasta que el servidor Django esté listo para recibir conexiones."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.3)
    return False


def run_migrations():
    """Ejecuta las migraciones pendientes automáticamente."""
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])


def start_django_server(port):
    """Inicia el servidor de desarrollo de Django."""
    from django.core.management import execute_from_command_line
    execute_from_command_line([
        'manage.py', 'runserver',
        f'127.0.0.1:{port}',
        '--noreload'  # Desactivar auto-reload (innecesario en producción)
    ])


def main():
    # Cambiar al directorio del proyecto
    os.chdir(BASE_DIR)

    log_path = os.path.join(BASE_DIR, 'StockPro_error.log')
    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Launcher iniciado: {sys.executable}\n")
    if getattr(sys, 'frozen', False):
        output_log = open(log_path, 'a', encoding='utf-8')
        sys.stdout = output_log
        sys.stderr = output_log

    def log(message):
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(message + '\n')

    port = find_free_port()
    log(f"Puerto elegido: {port}")
    print(f"[StockPro] Iniciando en puerto {port}...")

    # Ejecutar migraciones antes de iniciar
    print("[StockPro] Verificando base de datos...")
    try:
        run_migrations()
        log("Migraciones finalizadas")
    except Exception as e:
        log(f"Error en migraciones: {e}")
        print(f"[StockPro] Advertencia en migraciones: {e}")

    # Iniciar Django en un hilo separado (daemon=True para que muera con el proceso principal)
    print("[StockPro] Iniciando servidor...")
    server_thread = threading.Thread(target=start_django_server, args=(port,), daemon=True)
    server_thread.start()
    log("Hilo del servidor iniciado")

    # Esperar a que el servidor esté listo
    if not wait_for_server(port):
        log("ERROR: El servidor no respondió")
        print("[StockPro] ERROR: El servidor no respondió a tiempo.")
        sys.exit(1)

    log("Servidor listo")
    print(f"[StockPro] Servidor listo en http://127.0.0.1:{port}")
    print("[StockPro] Abriendo ventana de la aplicación...")

    # Abrir la ventana nativa del escritorio
    import webview
    window = webview.create_window(
        title='StockPro v1.0 - Sistema de Gestión de Almacén',
        url=f'http://127.0.0.1:{port}',
        width=1366,
        height=768,
        resizable=True,
        min_size=(1024, 600),
    )
    # webview.start() bloquea hasta que se cierra la ventana
    log("Iniciando webview")
    webview.start()
    log("Webview finalizado")

    print("[StockPro] Aplicación cerrada.")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        log_path = os.path.join(BASE_DIR, 'StockPro_error.log')
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write("Excepción no controlada:\n")
            traceback.print_exc(file=log_file)
        raise
