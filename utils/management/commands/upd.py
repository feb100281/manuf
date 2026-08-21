from django.core.management.base import BaseCommand
import duckdb
from django.conf import settings
import pandas as pd
from utils.models import Jobs, JobStatus
from django.utils import timezone
from pathlib import Path
from django.apps import apps


def update_model(model, df, unique_field):

    try:
        model_fields = {
            f.attname for f in model._meta.concrete_fields if not f.auto_created
        }

        objects = []

        for row in df.itertuples(index=False, name=None):

            data = {}

            for field, value in zip(df.columns, row):

                if field not in model_fields:
                    continue

                if pd.isna(value):
                    value = None

                data[field] = value

            objects.append(model(**data))

        # для bulk_create update_fields нужны ИМЕНА ПОЛЕЙ,
        # а не attname
        update_fields = [
            f.name
            for f in model._meta.concrete_fields
            if not f.auto_created
            and f.attname in df.columns
            and f.attname != unique_field
        ]

        model.objects.bulk_create(
            objects,
            update_conflicts=True,
            unique_fields=[unique_field],
            update_fields=update_fields,
            batch_size=1000,
        )
        return "Ok"

    except Exception as exc:
        return str(exc)


class Command(BaseCommand):
    help = "Обновляем базу данных."

    def add_arguments(self, parser):
        parser.add_argument(
            "job_id",
            type=int,
        )

    def handle(self, *args, **options):

        job_id = options["job_id"]
        job = Jobs.objects.get(pk=job_id)

        log_file = job.logfile.path

        def writelog(log, text):
            log.write(text + "\n")
            log.flush()

        with open(log_file, "w", encoding="utf-8") as log:

            writelog(log, "")
            writelog(log, f"{timezone.now()}: Start {job.command} ({job.name})")
            writelog(
                log, "============================================================"
            )
            writelog(log, "Parameters:")
            writelog(log, str(job.param))
            writelog(
                log, "============================================================"
            )
            writelog(log, "Running...")

            try:
                params = job.param or {}
                base_dir = settings.BASE_DIR
                raw_parquet_path = (
                    Path(settings.RAW_PARQUET_PATH).expanduser().resolve()
                )
                with duckdb.connect() as con:
                    writelog(log, "Creating views form raw_parquet_path:")
                    for file in raw_parquet_path.glob("*.parquet"):
                        table = file.stem.lower()
                        writelog(log, f"  - processing: {table}")
                        con.execute(
                            f"""
                            CREATE OR REPLACE VIEW {table} AS
                            SELECT *
                            FROM read_parquet('{file.as_posix()}');
                        """
                        )
                        writelog(log, f"  - {table} - ok")
                    writelog(log, "Updating models...")

                    for item in params["models"]:
                        model_name = item["model"]
                        Model = apps.get_model(model_name)
                        sql_path = base_dir / Path(item["sql"])
                        unique_field = item["unique_field"]
                        sql = sql_path.read_text(encoding="utf-8")
                        writelog(log, f"Updating {model_name}: sql {sql_path}")
                        df = con.execute(sql).df()
                        writelog(log, f"    - Updating field: {df.columns.tolist()}")
                        res = update_model(Model, df, unique_field)
                        writelog(log, f"    - Updating {model_name}: results {res}")
                    
                    writelog(log, "============================================================")
                    writelog(log, "DONE")
                    writelog(log, "============================================================")
    
                    job.status = JobStatus.DONE
                    job.lastrun = timezone.now()
    
                    job.save(
                        update_fields=[
                            "status",
                            "lastrun",
                        ]
                    )

            except Exception as exc:

                writelog(
                    log, "============================================================"
                )
                writelog(log, "FAILED")
                writelog(log, str(exc))
                writelog(
                    log, "============================================================"
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

 