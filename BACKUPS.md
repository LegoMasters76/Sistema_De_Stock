# Respaldos de base de datos y archivos

El comando `python manage.py backup_db` guarda cada ejecución en una carpeta
`backups/stockpro-backup-<UTC timestamp>` junto a `manage.py`. Cada carpeta
contiene el respaldo de la base de datos, `media.tar.gz` y `manifest.json`.

PostgreSQL requiere que `pg_dump` esté instalado y disponible en `PATH`. Se usan
las credenciales y opciones de conexión de Django; la contraseña no se agrega a
los argumentos del proceso. El formato custom (`database.dump`) se restaura con
`pg_restore`. SQLite usa su API de backup en línea para generar
`database.sqlite3` de forma consistente. Los medios se archivan en gzip.

## Ejecución y retención

```powershell
python manage.py backup_db
python manage.py backup_db --output-dir D:\StockProBackups --retention-days 14
```

La retención predeterminada es de 30 días. Solo elimina carpetas antiguas con
prefijo `stockpro-backup-` dentro del directorio de destino; una ejecución
fallida elimina únicamente la carpeta incompleta que ella misma creó.

En Linux se puede programar diariamente a las 02:00 con cron:

```cron
0 2 * * * cd /ruta/a/stockpro && /ruta/al/venv/bin/python manage.py backup_db --output-dir /var/backups/stockpro >> /var/log/stockpro-backup.log 2>&1
```

En Windows, crear una tarea diaria en el Programador de tareas que ejecute
`python.exe` con argumentos `manage.py backup_db --output-dir D:\StockProBackups`
y establezca como directorio de inicio la carpeta del proyecto.

## Restauración

Para PostgreSQL, crear primero una base destino vacía y restaurar el formato
custom:

```sh
pg_restore --no-owner --dbname="$DATABASE_URL" database.dump
```

Para SQLite, detener la aplicación y reemplazar el archivo de base por
`database.sqlite3`. En ambos casos, extraer `media.tar.gz` en el directorio de
datos de la aplicación; el archivo contiene una carpeta raíz `media/`.

El backup de base y el de medios se capturan en la misma ejecución, pero no son
una transacción atómica entre sí. Mantener una copia adicional fuera del equipo
del servidor y comprobar periódicamente una restauración de prueba.
