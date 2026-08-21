from pathlib import Path
import subprocess
import shutil
import sys


SOURCE_DIR = Path("/Users/pavelustenko/Downloads/Договоры аренды/МАНУФАКТУРА ОФИСОВ ООО")
TARGET_DIR = Path("/Users/pavelustenko/Downloads/compressed/manu")

# /screen   — жесткое сжатие
# /ebook    — нормальный баланс
# /printer  — хорошее качество
# /prepress — минимальное вмешательство
PDF_PROFILE = "/screen"


def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]

    value = float(size)

    for unit in units:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} PB"


def compress_pdf(source: Path, target: Path) -> tuple[int, int, bool]:
    target.parent.mkdir(parents=True, exist_ok=True)

    temp_target = target.with_suffix(".tmp.pdf")

    command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.6",
        f"-dPDFSETTINGS={PDF_PROFILE}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        f"-sOutputFile={temp_target}",
        str(source),
    ]

    original_size = source.stat().st_size

    try:
        subprocess.run(
            command,
            check=True,
        )

        compressed_size = temp_target.stat().st_size

        # Если Ghostscript сделал PDF больше —
        # просто копируем оригинал.
        if compressed_size >= original_size:
            temp_target.unlink(missing_ok=True)

            shutil.copy2(source, target)

            return original_size, original_size, False

        temp_target.replace(target)

        return original_size, compressed_size, True

    except Exception:
        temp_target.unlink(missing_ok=True)
        raise


def main():
    if shutil.which("gs") is None:
        print("ERROR: Ghostscript не установлен.")
        sys.exit(1)

    pdf_files = sorted(
        path
        for path in SOURCE_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )

    if not pdf_files:
        print("PDF не найдены.")
        return

    print(f"Найдено PDF: {len(pdf_files)}")
    print()

    total_original = 0
    total_result = 0
    compressed_count = 0
    unchanged_count = 0
    failed_count = 0

    for i, source in enumerate(pdf_files, start=1):
        relative_path = source.relative_to(SOURCE_DIR)
        target = TARGET_DIR / relative_path

        print(f"[{i}/{len(pdf_files)}] {relative_path}")

        try:
            old_size, new_size, compressed = compress_pdf(
                source,
                target,
            )

            total_original += old_size
            total_result += new_size

            if compressed:
                compressed_count += 1

                saving = old_size - new_size
                saving_percent = saving / old_size * 100

                print(
                    f"    {human_size(old_size)}"
                    f" -> {human_size(new_size)}"
                    f"   -{saving_percent:.1f}%"
                )
            else:
                unchanged_count += 1

                print(
                    f"    {human_size(old_size)}"
                    " -> оставлен оригинал"
                )

        except Exception as exc:
            failed_count += 1

            print(f"    ERROR: {exc}")

    print()
    print("=" * 60)
    print("ГОТОВО")
    print("=" * 60)

    print(f"PDF всего:          {len(pdf_files)}")
    print(f"Сжато:              {compressed_count}")
    print(f"Без изменений:      {unchanged_count}")
    print(f"Ошибки:             {failed_count}")

    print()
    print(f"Исходный размер:     {human_size(total_original)}")
    print(f"Новый размер:        {human_size(total_result)}")

    if total_original:
        saved = total_original - total_result
        percent = saved / total_original * 100

        print(f"Экономия:            {human_size(saved)}")
        print(f"Экономия:            {percent:.2f}%")

    print()
    print(f"Результат: {TARGET_DIR}")


if __name__ == "__main__":
    main()