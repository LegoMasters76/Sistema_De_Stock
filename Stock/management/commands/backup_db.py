import json
import os
import shutil
import sqlite3
import subprocess
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections


class Command(BaseCommand):
    help = "Respalda la base de datos y MEDIA_ROOT; elimina respaldos vencidos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default=str(Path(settings.BASE_DIR) / "backups"),
            help="Directorio donde guardar los respaldos (por defecto: BASE_DIR/backups).",
        )
        parser.add_argument(
            "--retention-days",
            type=int,
            default=30,
            help="Días que se conservan los respaldos completos (por defecto: 30).",
        )
        parser.add_argument(
            "--database",
            default="default",
            help="Alias de base de datos Django que se respaldará.",
        )

    def handle(self, *args, **options):
        retention_days = options["retention_days"]
        if retention_days < 1:
            raise CommandError("--retention-days debe ser al menos 1.")

        alias = options["database"]
        if alias not in connections:
            raise CommandError(f"No existe el alias de base de datos '{alias}'.")

        connection = connections[alias]
        output_dir = Path(options["output_dir"]).expanduser().resolve()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = output_dir / f"stockpro-backup-{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.mkdir()

        try:
            database_file = self._backup_database(connection, backup_dir)
            media_file = self._backup_media(backup_dir)
            manifest = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "database_alias": alias,
                "database_engine": connection.settings_dict["ENGINE"],
                "database_file": database_file,
                "media_file": media_file,
            }
            (backup_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
        except Exception as error:
            shutil.rmtree(backup_dir, ignore_errors=True)
            if isinstance(error, CommandError):
                raise
            raise CommandError(f"No se pudo completar el respaldo: {error}") from error

        removed = self._prune_backups(output_dir, backup_dir, retention_days)
        self.stdout.write(self.style.SUCCESS(f"Respaldo creado: {backup_dir}"))
        self.stdout.write(f"Base de datos: {database_file}")
        self.stdout.write(f"Archivos multimedia: {media_file}")
        self.stdout.write(f"Respaldos vencidos eliminados: {removed}")

    def _backup_database(self, connection, backup_dir):
        engine = connection.settings_dict["ENGINE"]
        if engine == "django.db.backends.postgresql":
            return self._backup_postgresql(connection, backup_dir)
        if engine == "django.db.backends.sqlite3":
            return self._backup_sqlite(connection, backup_dir)
        raise CommandError(f"Motor de base de datos no soportado: {engine}")

    def _backup_postgresql(self, connection, backup_dir):
        pg_dump = shutil.which("pg_dump")
        if not pg_dump:
            raise CommandError("No se encontró pg_dump; instala PostgreSQL client tools.")

        database = connection.settings_dict
        backup_name = "database.dump"
        backup_path = backup_dir / backup_name
        command = [pg_dump, "--format=custom", "--no-owner", "--file", str(backup_path)]
        environment = os.environ.copy()
        for setting, flag, env_name in (
            ("HOST", "--host", "PGHOST"),
            ("PORT", "--port", "PGPORT"),
            ("USER", "--username", "PGUSER"),
        ):
            value = database.get(setting)
            if value:
                command.extend([flag, str(value)])
                environment[env_name] = str(value)
        if database.get("PASSWORD"):
            environment["PGPASSWORD"] = str(database["PASSWORD"])

        options = database.get("OPTIONS", {})
        if options.get("sslmode"):
            environment["PGSSLMODE"] = str(options["sslmode"])
        command.append(str(database["NAME"]))
        result = subprocess.run(
            command,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            message = result.stderr.strip() or "pg_dump terminó con error."
            raise CommandError(message)
        return backup_name

    def _backup_sqlite(self, connection, backup_dir):
        backup_name = "database.sqlite3"
        connection.ensure_connection()
        destination = sqlite3.connect(backup_dir / backup_name)
        try:
            connection.connection.backup(destination)
        finally:
            destination.close()
        return backup_name

    def _backup_media(self, backup_dir):
        media_root = Path(settings.MEDIA_ROOT)
        archive_name = "media.tar.gz"
        archive_path = backup_dir / archive_name
        with tarfile.open(archive_path, "w:gz") as archive:
            if media_root.is_dir():
                archive.add(media_root, arcname="media")
        return archive_name

    def _prune_backups(self, output_dir, current_backup, retention_days):
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        removed = 0
        for backup in output_dir.glob("stockpro-backup-*"):
            if backup == current_backup or not backup.is_dir():
                continue
            modified = datetime.fromtimestamp(backup.stat().st_mtime, timezone.utc)
            if modified < cutoff:
                shutil.rmtree(backup)
                removed += 1
        return removed