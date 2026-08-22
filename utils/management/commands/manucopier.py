from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import subprocess

import duckdb

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from utils.models import Jobs, JobStatus


@dataclass
class FileInfo:
    table: str
    path: PurePosixPath


def export_models_to_parquet(
    models,
    output_dir: Path,
    log,
    writelog,
) -> list[FileInfo]:

    db_path = (
        Path(settings.DATABASES["default"]["NAME"])
        .expanduser()
        .resolve()
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    server_base = PurePosixPath(
        settings.SERVER_DATA_PARQUET_PATH
    )

    tables: list[FileInfo] = []

    con = duckdb.connect()

    try:
        con.execute("INSTALL sqlite")
        con.execute("LOAD sqlite")

        con.execute(
            f"""
            ATTACH '{db_path.as_posix()}'
            AS django_db
            (TYPE SQLITE)
            """
        )

        for model in models:
            table_name = model._meta.db_table

            parquet_path = (
                output_dir
                / f"{table_name}.parquet"
            )

            writelog(
                log,
                f"    - Copying {table_name}"
            )

            con.execute(
                f"""
                COPY django_db."{table_name}"
                TO '{parquet_path.as_posix()}'
                (
                    FORMAT PARQUET,
                    COMPRESSION ZSTD
                )
                """
            )

            writelog(
                log,
                f"    - Copy ready {parquet_path}"
            )

            tables.append(
                FileInfo(
                    table=table_name,
                    path=(
                        server_base
                        / f"{table_name}.parquet"
                    ),
                )
            )

    finally:
        con.close()

    return tables


def sync_to_server(
    output_dir: Path,
    log,
    writelog,
):
    writelog(
        log,
        f"Sync with {settings.SERVER_DATA_PARQUET_PATH}..."
    )

    result = subprocess.run(
        [
            "sshpass",
            "-p",
            settings.SERVER_PASSWORD,

            "rsync",
            "-avP",
            "--delete",

            "-e",
            "ssh -o StrictHostKeyChecking=no",

            "--rsync-path",
            (
                f"mkdir -p "
                f"{settings.SERVER_DATA_PARQUET_PATH} "
                f"&& rsync"
            ),

            f"{output_dir.as_posix()}/",

            (
                f"{settings.SERVER_USER}"
                f"@{settings.SERVER_HOST}:"
                f"{settings.SERVER_DATA_PARQUET_PATH}/"
            ),
        ],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        writelog(log, result.stdout)

    if result.returncode != 0:
        if result.stderr:
            writelog(log, result.stderr)

        raise RuntimeError(
            f"rsync failed with code {result.returncode}"
        )

    writelog(log, "Sync OK")


def import_parquet_on_server(
    tables: list[FileInfo],
    log,
    writelog,
):
    server_db = PurePosixPath(
        settings.SERVER_DB_PATH
    )

    writelog(log, "")
    writelog(
        log,
        f"Import parquet -> {server_db}"
    )

    sql: list[str] = [
        "INSTALL sqlite;",
        "LOAD sqlite;",
        (
            f"ATTACH '{server_db.as_posix()}' "
            f"AS db (TYPE SQLITE);"
        ),
    ]

    # --------------------------------------------------
    # Проверяем состояние FK в SQLite connection
    # --------------------------------------------------

    sql.append(
        """
        SELECT *
        FROM sqlite_query(
            'db',
            'PRAGMA foreign_keys;'
        );
        """
    )

    # --------------------------------------------------
    # Сначала удаляем данные из ВСЕХ таблиц
    # --------------------------------------------------

    writelog(log, "")
    writelog(log, "Clearing server tables...")

    for item in tables:
        writelog(
            log,
            f"    - DELETE {item.table}"
        )

        sql.append(
            f'DELETE FROM db."{item.table}";'
        )

    # --------------------------------------------------
    # Потом загружаем ВСЕ parquet
    # --------------------------------------------------

    writelog(log, "")
    writelog(log, "Loading parquet...")

    for item in tables:
        writelog(
            log,
            f"    - INSERT {item.table}"
        )

        sql.append(
            f"""
            INSERT INTO db."{item.table}" BY NAME

            SELECT *
            FROM read_parquet(
                '{item.path.as_posix()}'
            );
            """
        )

    # --------------------------------------------------
    # Проверяем FK после импорта
    # --------------------------------------------------

    sql.append(
        """
        SELECT *
        FROM sqlite_query(
            'db',
            'PRAGMA foreign_key_check;'
        );
        """
    )

    sql_text = "\n".join(sql)

    result = subprocess.run(
        [
            "sshpass",
            "-p",
            settings.SERVER_PASSWORD,

            "ssh",
            "-o",
            "StrictHostKeyChecking=no",

            (
                f"{settings.SERVER_USER}"
                f"@{settings.SERVER_HOST}"
            ),

            "duckdb",
        ],
        input=sql_text,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        writelog(log, result.stdout)

    if result.returncode != 0:
        if result.stderr:
            writelog(log, result.stderr)

        raise RuntimeError(
            f"DuckDB import failed "
            f"with code {result.returncode}"
        )

    writelog(
        log,
        "Server SQLite updated."
    )


class Command(BaseCommand):
    help = (
        "Export Django SQLite tables to parquet, "
        "sync them to server and update server SQLite."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "job_id",
            type=int,
        )

    def handle(self, *args, **options):
        job_id = options["job_id"]

        job = Jobs.objects.get(
            pk=job_id
        )

        log_file = job.logfile.path

        def writelog(log, text=""):
            log.write(
                str(text) + "\n"
            )
            log.flush()

        with open(
            log_file,
            "w",
            encoding="utf-8",
        ) as log:

            writelog(log)
            writelog(
                log,
                (
                    f"{timezone.now()}: "
                    f"Start {job.command} "
                    f"({job.name})"
                )
            )
            writelog(
                log,
                "=" * 60
            )
            writelog(
                log,
                "Parameters:"
            )
            writelog(
                log,
                str(job.param)
            )
            writelog(
                log,
                "=" * 60
            )
            writelog(
                log,
                "Running..."
            )

            try:
                params = job.param or {}

                app_list = params.get(
                    "app",
                    [],
                )

                if not app_list:
                    raise ValueError(
                        'Параметр "app" пуст'
                    )

                output_dir = (
                    Path(
                        settings.DATA_PARQUET_PATH
                    )
                    .expanduser()
                    .resolve()
                )

                # ------------------------------------------
                # Собираем Django models
                # ------------------------------------------

                models = []

                for app_name in app_list:
                    writelog(
                        log,
                        f"*** App {app_name} ***"
                    )

                    app_config = (
                        apps.get_app_config(
                            app_name
                        )
                    )

                    models.extend(
                        app_config.get_models()
                    )

                writelog(log)
                writelog(
                    log,
                    f"Models total: {len(models)}"
                )

                # ------------------------------------------
                # SQLite -> parquet
                # ------------------------------------------

                writelog(log)
                writelog(
                    log,
                    "Exporting to parquet..."
                )

                tables = export_models_to_parquet(
                    models=models,
                    output_dir=output_dir,
                    log=log,
                    writelog=writelog,
                )

                writelog(log)
                writelog(
                    log,
                    f"Parquet files: {len(tables)}"
                )

                # ------------------------------------------
                # rsync
                # ------------------------------------------

                writelog(log)
                writelog(
                    log,
                    "=" * 60
                )

                sync_to_server(
                    output_dir=output_dir,
                    log=log,
                    writelog=writelog,
                )

                # ------------------------------------------
                # parquet -> server SQLite
                # ------------------------------------------

                writelog(log)
                writelog(
                    log,
                    "=" * 60
                )

                import_parquet_on_server(
                    tables=tables,
                    log=log,
                    writelog=writelog,
                )

                # ------------------------------------------
                # DONE
                # ------------------------------------------

                writelog(log)
                writelog(
                    log,
                    "=" * 60
                )
                writelog(
                    log,
                    "DONE"
                )
                writelog(
                    log,
                    "=" * 60
                )

                job.status = JobStatus.DONE
                job.lastrun = timezone.now()

                job.save(
                    update_fields=[
                        "status",
                        "lastrun",
                    ]
                )

            except Exception as exc:
                writelog(log)
                writelog(
                    log,
                    "=" * 60
                )
                writelog(
                    log,
                    "FAILED"
                )
                writelog(
                    log,
                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    )
                )
                writelog(
                    log,
                    "=" * 60
                )

                job.status = JobStatus.FAILED
                job.lastrun = timezone.now()

                job.save(
                    update_fields=[
                        "status",
                        "lastrun",
                    ]
                )

                raise