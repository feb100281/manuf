from django.core.management.base import BaseCommand
import duckdb
from django.conf import settings
import pandas as pd
from utils.models import Jobs, JobStatus
from django.utils import timezone
from pathlib import Path
from django.apps import apps
from django.db import connection


class Command(BaseCommand):
    help = "Чистим таблицы"

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
            writelog(
                log,
                f"{timezone.now()}: Start {job.command} ({job.name})"
            )
            writelog(log, "============================================================")
            writelog(log, "Parameters:")
            writelog(log, str(job.param))
            writelog(log, "============================================================")
            writelog(log, "Running...")
            
            try:
                params = job.param or {}
                tables = params["tables"]
                with connection.cursor() as con:
                    
                    for table in tables:
                        writelog(log, f"Clearing {table}")
                        con.execute(
                            f'DELETE FROM "{table}"'
                        )
                        writelog(log, f"{table} cleared")    
                        
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
            
            