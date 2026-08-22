from pathlib import Path
from dataclasses import dataclass
import shutil
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from utils.models import Jobs, JobStatus


@dataclass
class FileInfo:
    source_path: Path
    target_path: Path
    la_id: int


def get_files(path: Path) -> list[Path]:
    """Получить все файлы рекурсивно."""
    if not path.exists():
        raise FileNotFoundError(f"Папка не найдена: {path}")

    return [
        p
        for p in path.rglob("*")
        if p.is_file() and not p.name.lower().startswith(".ds")
    ]


def split_files(files: list[Path]) -> tuple[list[Path], list[Path]]:
    """
    Делит файлы на:
    - файлы соглашений: имя начинается с integer id
    - остальные файлы/report
    """
    la_files: list[Path] = []
    report_files: list[Path] = []

    for file in files:
        parts = file.name.strip().split()

        if not parts:
            report_files.append(file)
            continue

        first_part = parts[0]

        if "_" in first_part:
            report_files.append(file)
            continue

        try:
            int(first_part)
            la_files.append(file)
        except ValueError:
            report_files.append(file)

    return la_files, report_files


class Command(BaseCommand):
    help = "Распаковывает архив договоров и присоединяет файлы к la.SA."

    def add_arguments(self, parser):
        parser.add_argument(
            "job_id",
            type=int,
        )

    def handle(self, *args, **options):
        job_id = options["job_id"]

        job = Jobs.objects.get(pk=job_id)
        log_file = job.logfile.path

        def writelog(log, text=""):
            log.write(str(text) + "\n")
            log.flush()

        with open(log_file, "w", encoding="utf-8") as log:
            writelog(log)
            writelog(
                log,
                f"{timezone.now()}: Start {job.command} ({job.name})"
            )
            writelog(log, "=" * 60)
            writelog(log, "Parameters:")
            writelog(log, str(job.param))
            writelog(log, "=" * 60)
            writelog(log, "Running...")

            try:
                params = job.param or {}

                # --------------------------------------------------
                # Paths
                # --------------------------------------------------

                archive_value = params.get("zip_file")

                if not archive_value:
                    raise ValueError(
                        'Не указан параметр "zip_file"'
                    )

                archive_path = Path(archive_value).expanduser()
                target = Path.home() / "Downloads" / "latemp"
                media_path = Path(settings.MEDIA_ROOT)

                if not archive_path.exists():
                    raise FileNotFoundError(
                        f"Архив не найден: {archive_path}"
                    )

                if not archive_path.is_file():
                    raise ValueError(
                        f"Путь не является файлом: {archive_path}"
                    )

                target.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                media_path.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                # --------------------------------------------------
                # Unpack
                # --------------------------------------------------

                writelog(
                    log,
                    f"Unzip {archive_path} to {target} ..."
                )

                tar_path = target / "la.tar"

                writelog(log, f"Распаковываем ZSTD -> {tar_path}")

                subprocess.run(
                    [
                        "zstd",
                        "-d",
                        "-f",              # <-- ВОТ ЭТО
                        str(archive_path),
                        "-o",
                        str(tar_path),
                    ],
                    check=True,
                )

                writelog(log, "ZSTD распакован")

                subprocess.run(
                    [
                        "tar",
                        "-xf",
                        str(tar_path),
                        "-C",
                        str(target),
                    ],
                    check=True,
                )

                writelog(log, "TAR распакован")

                writelog(
                    log,
                    f"Unzip OK. Все документы в {target}"
                )
                writelog(log)

                # --------------------------------------------------
                # Analyze files
                # --------------------------------------------------

                writelog(log, "Анализируем файлы ...")

                files = get_files(target)

                writelog(
                    log,
                    f"    - Итого файлов: {len(files)}"
                )

                la_files, report_files = split_files(files)

                writelog(
                    log,
                    f"    - Файлы к документам: {len(la_files)}"
                )
                writelog(
                    log,
                    f"    - Файлы нераспознанные: {len(report_files)}"
                )

                if report_files:
                    writelog(log)
                    writelog(log, "Нераспознанные файлы:")

                    for file in report_files:
                        writelog(
                            log,
                            f"    [REPORT] {file}"
                        )

                writelog(log)

                # --------------------------------------------------
                # Match with DB
                # --------------------------------------------------

                result: list[FileInfo] = []

                with connection.cursor() as con:
                    writelog(
                        log,
                        "Сопоставляем документы с БД ..."
                    )

                    for file in la_files:
                        first_part = file.name.strip().split()[0]
                        id_agr = int(first_part)
                        extension = file.suffix.lower()

                        writelog(
                            log,
                            f"Документ: {file.name} | id={id_agr}"
                        )

                        con.execute(
                            f"""
                            SELECT
                                COALESCE(cp.name, 'Без контрагента')
                                || '/' ||
                                replace(
                                    COALESCE(la.number, 'бн'),
                                    '/',
                                    '-'
                                )
                                || '/' ||
                                replace(
                                    COALESCE(sa.number, 'бн'),
                                    '/',
                                    '-'
                                )
                                || ' от ' ||
                                COALESCE(
                                    CAST(sa.date_from AS TEXT),
                                    'бд'
                                )
                                || '{extension}'
                                AS target_path
                            FROM la_sa AS sa
                            LEFT JOIN la_la AS la
                                ON la.id = sa.la_id
                            LEFT JOIN cp_cp AS cp
                                ON cp.id = la.cp_id
                            WHERE sa.id = {id_agr}
                            """
                        )

                        row = con.fetchone()

                        if row is None:
                            writelog(
                                log,
                                f"    [SKIP] "
                                f"В БД не найден id={id_agr}: "
                                f"{file.name}"
                            )
                            continue

                        target_path = row[0]

                        if not target_path:
                            writelog(
                                log,
                                f"    [SKIP] "
                                f"target_path пустой для "
                                f"id={id_agr}: {file.name}"
                            )
                            continue

                        file_info = FileInfo(
                            source_path=file,
                            target_path=media_path / "la" / target_path,
                            la_id=id_agr,
                        )

                        result.append(file_info)

                        writelog(
                            log,
                            f"    [MATCH] "
                            f"{file.name} -> {file_info.target_path}"
                        )

                    writelog(log)
                    writelog(log, "=" * 60)
                    writelog(
                        log,
                        f"СОПОСТАВЛЕНО С БД: {len(result)} файлов"
                    )
                    writelog(log, "=" * 60)
                    writelog(log)

                    # --------------------------------------------------
                    # Copy files
                    # --------------------------------------------------

                    writelog(log, "Копируем файлы ...")

                    copied = 0

                    for file_info in result:
                        file_info.target_path.parent.mkdir(
                            parents=True,
                            exist_ok=True,
                        )

                        shutil.copy2(
                            file_info.source_path,
                            file_info.target_path,
                        )

                        copied += 1

                        writelog(
                            log,
                            f"[COPY] {file_info.source_path.name}"
                        )
                        writelog(
                            log,
                            f"       -> {file_info.target_path}"
                        )

                    writelog(log)
                    writelog(
                        log,
                        f"Скопировано файлов: {copied}"
                    )
                    writelog(log)

                    # --------------------------------------------------
                    # Update database
                    # --------------------------------------------------

                    writelog(
                        log,
                        "Обновляем ссылки на файлы в базе данных ..."
                    )

                    updated = 0
                    update_errors = 0

                    for file_info in result:
                        db_path = (
                            file_info.target_path
                            .relative_to(media_path)
                        )

                        con.execute(
                            f"""
                            UPDATE la_sa
                            SET file = '{db_path.as_posix()}'
                            WHERE id = {file_info.la_id}
                            """
                        )

                        if con.rowcount == 1:
                            updated += 1

                            writelog(
                                log,
                                f"[DB] "
                                f"id={file_info.la_id} "
                                f"-> {db_path.as_posix()}"
                            )
                        else:
                            update_errors += 1

                            writelog(
                                log,
                                f"[DB ERROR] "
                                f"id={file_info.la_id}: "
                                f"строка не обновлена"
                            )

                    writelog(log)
                    writelog(
                        log,
                        f"Обновлено записей: {updated}"
                    )

                    if update_errors:
                        writelog(
                            log,
                            f"Ошибок обновления: {update_errors}"
                        )

                # --------------------------------------------------
                # Done
                # --------------------------------------------------

                writelog(log)
                writelog(log, "=" * 60)
                writelog(log, "DONE")
                writelog(log, "=" * 60)

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
                writelog(log, "=" * 60)
                writelog(log, "FAILED")
                writelog(
                    log,
                    f"{type(exc).__name__}: {exc}"
                )
                writelog(log, "=" * 60)

                job.status = JobStatus.FAILED
                job.lastrun = timezone.now()

                job.save(
                    update_fields=[
                        "status",
                        "lastrun",
                    ]
                )

                raise