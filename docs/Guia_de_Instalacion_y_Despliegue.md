# Guía de Instalación y Despliegue

> Plantilla operativa. Complete los valores entre corchetes y almacene secretos únicamente en el servidor o en el gestor de secretos del proveedor.

## Requisitos previos

- Servidor Linux con Docker Engine y Docker Compose v2.
- DNS del dominio [dominio] apuntando al servidor; puertos TCP 80 y 443 accesibles.
- Espacio y política de respaldos definidos para PostgreSQL y archivos multimedia.
- Acceso al repositorio y a la versión aprobada de la aplicación.

## Configuración inicial

1. Obtenga el código de la versión aprobada en el servidor.
2. Copie `.env.production.example` como `.env` y complete los valores:
   - `DJANGO_SECRET_KEY`: valor aleatorio de al menos 50 caracteres.
   - `DJANGO_ALLOWED_HOSTS`: nombres DNS separados por comas.
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: orígenes completos con `https://`.
   - `POSTGRES_PASSWORD`: contraseña larga URL-safe; el formato alfanumérico evita problemas de codificación en `DATABASE_URL`.
   - `DOMAIN` y `CERTBOT_EMAIL`: dominio público y correo de renovación.
3. Restrinja permisos del archivo `.env` y no lo incluya en Git ni en imágenes.
4. Confirme que `DOMAIN`, `DJANGO_ALLOWED_HOSTS` y `DJANGO_CSRF_TRUSTED_ORIGINS` correspondan al DNS real.

## Primer despliegue y certificado TLS

Ejecute los comandos desde la raíz del proyecto en una terminal Bash/Linux:

```bash
docker compose up -d --build db web nginx
docker compose ps
```

Solicite el certificado de Let's Encrypt por el desafío HTTP-01:

```bash
docker compose --profile renewal run --rm --entrypoint certbot certbot \
  certonly --webroot --webroot-path /var/www/certbot \
  --email admin@example.com --agree-tos --no-eff-email -d stock.example.com
```

Reemplace `admin@example.com` y `stock.example.com` por los valores definidos en `.env`.

Reinicie Nginx para activar el virtual host HTTPS y habilite la renovación periódica:

```bash
docker compose restart nginx
docker compose --profile renewal up -d certbot
docker compose ps
```

Verifique `https://[dominio]`, el acceso al panel y la carga de archivos estáticos y multimedia. El contenedor web ejecuta migraciones y `collectstatic` al iniciar.

## Actualizaciones

1. Realice y verifique un respaldo de PostgreSQL y del volumen multimedia.
2. Despliegue el commit/tag aprobado.
3. Ejecute `docker compose up -d --build`.
4. Compruebe `docker compose ps`, `docker compose logs --tail=100 web nginx` y las operaciones principales.
5. Registre versión, fecha, responsable y resultado. Mantenga una estrategia documentada de reversión; una reversión de código no revierte automáticamente migraciones de base de datos.

## Operación, respaldos y recuperación

- Base de datos: [frecuencia, retención, cifrado, ubicación externa y responsable].
- Medios subidos: [frecuencia, retención y ubicación externa].
- Prueba de restauración: [frecuencia, fecha y procedimiento].
- Monitoreo y alertas: [responsable, señales y umbrales].
- Rotación de secretos y renovación de certificados: [procedimiento].

Los volúmenes de Docker persisten datos en el servidor, pero por sí solos no constituyen un respaldo.

## Diagnóstico

```bash
docker compose ps
docker compose logs --tail=200 web
docker compose logs --tail=200 nginx
docker compose exec db pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Para problemas de arranque, confirme `.env`, estado DNS, espacio libre, permisos/estado de volúmenes y conectividad a PostgreSQL. No comparta logs que contengan datos personales o secretos.

## Datos de entrega

- Entorno/servidor: [completar]
- Dominio y versión: [completar]
- Responsable técnico del cliente: [completar]
- Responsable de despliegue: [completar]
- Procedimiento de escalamiento: [completar]