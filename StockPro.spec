# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/Renzo/Desktop/Sistema de stock/SistemaDeStock', 'SistemaDeStock'), ('C:/Users/Renzo/Desktop/Sistema de stock/Stock', 'Stock'), ('C:/Users/Renzo/Desktop/Sistema de stock/account', 'account'), ('C:/Users/Renzo/Desktop/Sistema de stock/ventas', 'ventas'), ('C:/Users/Renzo/Desktop/Sistema de stock/messenger', 'messenger'), ('C:/Users/Renzo/Desktop/Sistema de stock/main', 'main'), ('C:/Users/Renzo/Desktop/Sistema de stock/templates', 'templates'), ('C:/Users/Renzo/Desktop/Sistema de stock/manage.py', '.')],
    hiddenimports=['django', 'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'django.contrib.auth.backends', 'django.template.defaulttags', 'django.template.defaultfilters', 'django.template.loader_tags', 'django.templatetags', 'django.templatetags.static', 'django.templatetags.i18n', 'SistemaDeStock', 'SistemaDeStock.settings', 'SistemaDeStock.urls', 'SistemaDeStock.wsgi', 'Stock', 'Stock.models', 'Stock.views', 'Stock.urls', 'Stock.forms', 'Stock.admin', 'Stock.apps', 'Stock.migrations', 'account', 'account.models', 'account.views', 'account.urls', 'account.forms', 'account.admin', 'account.apps', 'account.migrations', 'ventas', 'ventas.models', 'ventas.views', 'ventas.urls', 'ventas.forms', 'ventas.admin', 'ventas.apps', 'ventas.migrations', 'messenger', 'messenger.models', 'messenger.views', 'messenger.urls', 'messenger.admin', 'messenger.apps', 'messenger.context_processors', 'messenger.migrations', 'main', 'main.models', 'main.views', 'main.admin', 'main.apps', 'main.middleware', 'main.migrations', 'webview', 'ckeditor'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StockPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StockPro',
)
