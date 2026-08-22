from pathlib import Path
import duckdb
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from utils.models import Jobs, JobStatus


# EXCLUDED_TABLES = {
#   "GroupCompanues" : True,
#   "sqlite_sequence" : False,
#   "PremisType" : True,
#   "PremisStatus" : True,
#   "PremisConntact" : True,
#   "LeaseTermTyps" : True,
#   "Export" : False,
#   "Properties_building" : True,
#   "tempPremises" : False,
#   "Offices" : True,
#   "LeaseTerms" : True,
#   "Revenues" : True,
#   "_carReconsilaton" : False,
#   "Companies" : True,
#   "BankAccounts" : True,
#   "Items" : True,
#   "AccountsCF" : True,
#   "_thirdPartyExceptions" : False,
#   "_contractsExceptions" : False,
#   "_rentCfDistribution" : False,
#   "Contracts" : True,
#   "cfMaster" : True,
#   "TypeContrAgent" : True,
#   "_LeaseTerms" : False,
#   "gl_temp_f" : False,
#   "_fixNanInn" : False,
#   "Chart" : True,
#   "_gl_temp_fBE" : False,
#   "_manuAccuralsAccounts" : False,
#   "budget" : True,
#   "beginingBalance2021" : True,
#   "TempPrem" : False,
#   "ReferenRate" : True,
#   "ContrAgents" : True,
#   "Documents" : True,
#   "__pen__" : False,
#   "la_fs_backup" : False,
#   "Properties" : True,
#   "indexation" : True,
#   "Brands" : True,
#   "akt_change" : True,
#   "number_change" : True,
#   "type_special_project" : True,
#   "RentPremises" : True,
#   "Sales_agreement" : True,
#   "floorArea" : True,
#   "temp_la" : False,
#   "right_exit" : True,
#   "LeaseAgreements" : True,
#   "temp_raw" : False,
#   "try" : False,
#   "fs_la_temp" : False,
#   "__penfix__" : False,
#   "__gl__" : False,
#   "__13__" : False,
#   "__penvar__" : False,
#   "_manuAccuralsAccountsNew" : False,
#   "gl_temp" : False,
#   "temp_cfMaster" : False,
#   "temp_comparison" : False,
#   "temp_summary" : False,
#   "temp_summary_final" : False,
#   "fs_tbl" : False,
#   "fs_la" : False, 
# }



class Command(BaseCommand):
    help = "Initialize DuckDB and attach the Django SQLite database."
    
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

                sqlite_path_raw = params["manu_path"]
                tables = params["tables"]

                sqlite_path = (
                    Path(sqlite_path_raw)
                    .expanduser()
                    .resolve()
                )

                if not sqlite_path.exists():
                    message = f"Не найдена Manu БД по пути {sqlite_path}"

                    writelog(log, message)

                    raise CommandError(message)

                raw_parquet_path = (
                    Path(settings.RAW_PARQUET_PATH)
                    .expanduser()
                    .resolve()
                )

                # RAW_PARQUET_PATH — это папка
                raw_parquet_path.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                writelog(
                    log,
                    f"SQLite database: {sqlite_path}"
                )

                writelog(
                    log,
                    f"Writing parquet files to: {raw_parquet_path}"
                )

                with duckdb.connect() as con:

                    con.execute("INSTALL sqlite")
                    con.execute("LOAD sqlite")
                    con.execute("SET sqlite_all_varchar=true")

                    con.execute(
                        f"""
                        ATTACH '{sqlite_path.as_posix()}'
                        AS sqlite_db
                        (TYPE SQLITE)
                        """
                    )

                    writelog(
                        log,
                        "SQLite database attached as sqlite_db."
                    )

                    for table in tables:

                        parquet_file = (
                            raw_parquet_path
                            / f"{table.lower()}.parquet"
                        )

                        writelog(
                            log,
                            f"Processing {table}..."
                        )

                        con.execute(
                            f"""
                            COPY (
                                SELECT *
                                FROM sqlite_db.{table}
                            )
                            TO '{parquet_file.as_posix()}'
                            (
                                FORMAT PARQUET,
                                COMPRESSION ZSTD
                            )
                            """
                        )

                        writelog(
                            log,
                            f"Saved: {parquet_file}"
                        )

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

                writelog(log, "============================================================")
                writelog(log, "FAILED")
                writelog(log, str(exc))
                writelog(log, "============================================================")

                job.status = JobStatus.FAILED
                job.lastrun = timezone.now()

                job.save(
                    update_fields=[
                        "status",
                        "lastrun",
                    ]
                )

                raise
        
   