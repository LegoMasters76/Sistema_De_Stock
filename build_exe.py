"""
Script de empaquetado para generar el .exe de StockPro
Ejecutar: python build_exe.py
"""
import PyInstaller.__main__
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist', 'StockPro')

def build():
    print("=" * 50)
    print("  StockPro - Generador de .exe")
    print("=" * 50)

    # Limpiar builds anteriores
    for folder in ['build', 'dist']:
        path = os.path.join(BASE_DIR, folder)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"[BUILD] Limpiado: {folder}/")

    # Ejecutar PyInstaller
    print("[BUILD] Empaquetando con PyInstaller...")
    PyInstaller.__main__.run([
        'launcher.py',
        '--name=StockPro',
        '--onedir',             # Carpeta con todos los archivos
        '--windowed',           # Sin ventana de consola
        '--noconfirm',          # No preguntar confirmación
        '--clean',              # Limpiar cache
        # Incluir los archivos del proyecto Django
        f'--add-data={os.path.join(BASE_DIR, "SistemaDeStock")};SistemaDeStock',
        f'--add-data={os.path.join(BASE_DIR, "Stock")};Stock',
        f'--add-data={os.path.join(BASE_DIR, "account")};account',
        f'--add-data={os.path.join(BASE_DIR, "ventas")};ventas',
        f'--add-data={os.path.join(BASE_DIR, "messenger")};messenger',
        f'--add-data={os.path.join(BASE_DIR, "main")};main',
        f'--add-data={os.path.join(BASE_DIR, "templates")};templates',
        f'--add-data={os.path.join(BASE_DIR, "manage.py")};.',
        # Hidden imports que Django necesita
        '--hidden-import=django',
        '--hidden-import=django.contrib.admin',
        '--hidden-import=django.contrib.auth',
        '--hidden-import=django.contrib.contenttypes',
        '--hidden-import=django.contrib.sessions',
        '--hidden-import=django.contrib.messages',
        '--hidden-import=django.contrib.staticfiles',
        '--hidden-import=django.contrib.auth.backends',
        '--hidden-import=django.template.defaulttags',
        '--hidden-import=django.template.defaultfilters',
        '--hidden-import=django.template.loader_tags',
        '--hidden-import=django.templatetags',
        '--hidden-import=django.templatetags.static',
        '--hidden-import=django.templatetags.i18n',
        '--hidden-import=SistemaDeStock',
        '--hidden-import=SistemaDeStock.settings',
        '--hidden-import=SistemaDeStock.urls',
        '--hidden-import=SistemaDeStock.wsgi',
        '--hidden-import=Stock',
        '--hidden-import=Stock.models',
        '--hidden-import=Stock.views',
        '--hidden-import=Stock.urls',
        '--hidden-import=Stock.forms',
        '--hidden-import=Stock.admin',
        '--hidden-import=Stock.apps',
        '--hidden-import=Stock.migrations',
        '--hidden-import=account',
        '--hidden-import=account.models',
        '--hidden-import=account.views',
        '--hidden-import=account.urls',
        '--hidden-import=account.forms',
        '--hidden-import=account.admin',
        '--hidden-import=account.apps',
        '--hidden-import=account.migrations',
        '--hidden-import=ventas',
        '--hidden-import=ventas.models',
        '--hidden-import=ventas.views',
        '--hidden-import=ventas.urls',
        '--hidden-import=ventas.forms',
        '--hidden-import=ventas.admin',
        '--hidden-import=ventas.apps',
        '--hidden-import=ventas.migrations',
        '--hidden-import=messenger',
        '--hidden-import=messenger.models',
        '--hidden-import=messenger.views',
        '--hidden-import=messenger.urls',
        '--hidden-import=messenger.admin',
        '--hidden-import=messenger.apps',
        '--hidden-import=messenger.context_processors',
        '--hidden-import=messenger.migrations',
        '--hidden-import=main',
        '--hidden-import=main.models',
        '--hidden-import=main.views',
        '--hidden-import=main.admin',
        '--hidden-import=main.apps',
        '--hidden-import=main.middleware',
        '--hidden-import=main.migrations',
        '--hidden-import=webview',
        '--hidden-import=ckeditor',
    ])

    # Copiar la base de datos si existe
    db_path = os.path.join(BASE_DIR, 'db.sqlite3')
    if os.path.exists(db_path):
        shutil.copy2(db_path, DIST_DIR)
        print("[BUILD] Base de datos copiada.")

    # Copiar archivos de media si existen
    media_src = os.path.join(BASE_DIR, 'media')
    if os.path.exists(media_src):
        media_dst = os.path.join(DIST_DIR, 'media')
        shutil.copytree(media_src, media_dst, dirs_exist_ok=True)
        print("[BUILD] Carpeta media copiada.")

    print()
    print("=" * 50)
    print("  ¡BUILD EXITOSO!")
    print(f"  Tu .exe está en: dist/StockPro/StockPro.exe")
    print("=" * 50)


if __name__ == '__main__':
    build()
