"""
Асинхронний сортер файлів за розширенням.
Використання:
    python3 sorter_async.py --source /path/to/source --output /path/to/output --concurrency 10
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import pathlib
import shutil
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("sorter")


async def find_files_recursive(source: pathlib.Path) -> List[pathlib.Path]:
    """
    Виконує os.walk у threadpool та повертає список файлів.
    """
    def _walk(s: str) -> List[str]:
        found: List[str] = []
        for root, _, files in os.walk(s):
            for f in files:
                found.append(os.path.join(root, f))
        return found

    result = await asyncio.to_thread(_walk, str(source))
    return [pathlib.Path(p) for p in result]


async def copy_file(src: pathlib.Path, dst_root: pathlib.Path) -> None:
    """
    Копіює src -> dst_root/<ext>/<filename>. Викликається у threadpool.
    """
    try:
        ext = src.suffix.lower().lstrip(".") or "no_ext"
        target_dir = dst_root / ext
        target_dir.mkdir(parents=True, exist_ok=True)
        dst_path = target_dir / src.name

        # Використаємо shutil.copy2 у потоці
        await asyncio.to_thread(shutil.copy2, str(src), str(dst_path))
        logger.info("Copied %s -> %s", src, dst_path)
    except Exception as exc:  # явна обробка помилок
        logger.exception("Error copying %s: %s", src, exc)


async def read_and_copy_all(source: pathlib.Path, output: pathlib.Path, concurrency: int = 10) -> None:
    files = await find_files_recursive(source)
    logger.info("Found %d files in %s", len(files), source)

    sem = asyncio.Semaphore(concurrency)
    tasks: List[asyncio.Task] = []

    async def sem_copy(f: pathlib.Path):
        async with sem:
            await copy_file(f, output)

    for f in files:
        tasks.append(asyncio.create_task(sem_copy(f)))

    # чекаємо завершення всіх задач, збираємо помилки
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # логування ексепшенів якщо є
    for r in results:
        if isinstance(r, Exception):
            logger.error("Task failed: %s", r)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Асинхронний сортер файлів за розширенням.")
    parser.add_argument("--source", "-s", required=True, help="Шлях до вихідної папки")
    parser.add_argument("--output", "-o", required=True, help="Шлях до цільової папки")
    parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=10,
        help="Макс. кількість одночасних операцій копіювання (default=10)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    src = pathlib.Path(args.source).expanduser().resolve()
    out = pathlib.Path(args.output).expanduser().resolve()

    if not src.exists() or not src.is_dir():
        logger.error("Source folder не існує або не є директорією: %s", src)
        raise SystemExit(1)
    out.mkdir(parents=True, exist_ok=True)

    try:
        asyncio.run(read_and_copy_all(src, out, concurrency=args.concurrency))
        logger.info("Finished.")
    except Exception:
        logger.exception("Unhandled error in main")
        raise


if __name__ == "__main__":
    main()