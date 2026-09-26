# Verificación Final del Paso 10

Esta guía separa la prueba local sin dominio público de la activación TLS real. El perfil local usa HTTP y credenciales solo de prueba; no reutilice esos valores en producción.

## 1. Instalar dependencias en Windows

Instale Python 3.12 o superior y ejecute desde la raíz del repositorio en PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, ejecute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` en esa terminal y vuelva a activar el entorno. `requirements.txt` incluye dependencias web y de escritorio; el contenedor usa `requirements-prod.txt`, que omite PyInstaller y pywebview.

## 2. Migraciones y suite en el entorno local

El perfil local usa SQLite. Si ya existe `db.sqlite3`, haga una copia antes de migrar:

```powershell
if (Test-Path .\db.sqlite3) { Copy-Item .\db.sqlite3 .\db.sqlite3.pre-verificacion.bak }
python manage.py check
python manage.py migrate --plan
python manage.py migrate
python manage.py migrate --check
python manage.py showmigrations
python manage.py test --verbosity 2
```

El último comando debe terminar con `OK`. El runner crea una base de pruebas separada; no use una base de producción para ejecutar pruebas.

## 3. Suite completa contra PostgreSQL

La validación representativa de producción está en Docker: se ejecuta más abajo contra el PostgreSQL del Compose. Para reproducirla manualmente en Windows, inicie primero el servicio `db` y configure `DATABASE_URL` al nombre/puerto publicado que use en esa instalación; por defecto el servicio no expone PostgreSQL al host, intencionalmente.

## 4. Check de despliegue

La comprobación debe usar el perfil `production`, una clave real temporal para la prueba, hosts/orígenes válidos y PostgreSQL. Con el stack iniciado, ejecute:

```powershell
docker compose exec -e DJANGO_SECURE_SSL_REDIRECT=true -e DJANGO_SECURE_COOKIES=true web python manage.py check --deploy --fail-level WARNING
```

El resultado esperado es `System check identified no issues (0 silenced).`; `--fail-level WARNING` hace que cualquier advertencia también devuelva un código de error. No copie la clave real en reportes o capturas. Si modifica settings localmente, repita también los tests.

## 5. Prueba local detrás de Nginx

Instale y abra Docker Desktop, espere que indique que el motor está ejecutándose y confirme que los puertos locales elegidos estén libres. Desde la raíz del repositorio:

```powershell
Copy-Item .env.docker-local.example .env
docker compose config --quiet
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 web nginx
```

Cuando `web` y `nginx` estén saludables, abra `http://localhost:8080`. Esta plantilla configura un Postgres descartable, Nginx en HTTP y cookies no seguras únicamente para facilitar la prueba local; no emite certificados para `localhost`.

Verifique las migraciones, suite sobre PostgreSQL y controles de producción dentro de los contenedores:

```powershell
docker compose exec web python manage.py migrate --check
docker compose exec -e DJANGO_ENV=local web python manage.py test --verbosity 2
docker compose exec -e DJANGO_SECURE_SSL_REDIRECT=true -e DJANGO_SECURE_COOKIES=true web python manage.py check --deploy --fail-level WARNING
```

Para probar también una operación: inicie sesión con una cuenta de prueba y cree datos ficticios. No importe datos reales en este stack.

## 6. Dominio real y HTTPS

Let's Encrypt necesita un dominio público cuyo DNS apunte a la máquina y que acepte conexiones externas en los puertos 80 y 443. En un servidor de despliegue, no use `.env.docker-local.example`: copie `.env.production.example` a `.env`, configure secretos fuertes, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DOMAIN` y `CERTBOT_EMAIL`; deje `DJANGO_SECURE_SSL_REDIRECT=true` y `DJANGO_SECURE_COOKIES=true` (son los valores por defecto).

Con DNS y firewall listos, ejecute en PowerShell desde la raíz:

```powershell
docker compose up --build -d
docker compose --profile renewal run --rm --entrypoint certbot certbot certonly --webroot --webroot-path /var/www/certbot --email admin@example.com --agree-tos --no-eff-email -d stock.example.com
docker compose restart nginx
docker compose --profile renewal up -d certbot
docker compose ps
```

Sustituya el correo y el dominio de ejemplo por los valores reales. Abra `https://stock.example.com`, confirme el certificado, inicio de sesión y carga de estáticos/medios. No es posible completar la emisión de Let's Encrypt para `localhost` ni para un dominio que no resuelva públicamente a la máquina.

## 7. Al terminar la prueba local

```powershell
docker compose down
```

Esto conserva los volúmenes. Para borrar también la base local y los medios de prueba, y solo si está seguro de no necesitarlos, use `docker compose down --volumes`.

## 8. Compartir un error para diagnóstico

Pegue en el chat el comando exacto ejecutado, la salida completa desde la primera línea del error hasta el código de salida y el resultado de:

```powershell
docker compose ps
docker compose logs --tail=200 web nginx db
python --version
python -m pip show Django django-simple-history dj-database-url psycopg2-binary
```

Para un fallo de tests, incluya también el nombre del test fallido y su traceback completo. Redacte contraseñas, `DJANGO_SECRET_KEY`, tokens, dominios privados y cualquier dato personal antes de compartir logs.