"""
MapReduce word frequency + visualization (multithreaded).
Використання:
    python3 mapreduce_wordfreq.py --url "https://..." --top 20 --workers 8
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import logging
import re
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mapreduce")

WORD_RE = re.compile(r"\b[а-яА-ЯёЁa-zA-Z0-9']+\b", flags=re.UNICODE)


def fetch_text(url: str, timeout: int = 15) -> str:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def chunk_text_by_lines(text: str, chunks: int) -> List[str]:
    lines = text.splitlines()
    if chunks <= 1 or len(lines) == 0:
        return ["\n".join(lines)]
    # roughly equal number of lines per chunk
    k, m = divmod(len(lines), chunks)
    parts = []
    i = 0
    for c in range(chunks):
        size = k + (1 if c < m else 0)
        part = lines[i : i + size]
        parts.append("\n".join(part))
        i += size
    return parts


def map_count_words(text_part: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for m in WORD_RE.finditer(text_part):
        w = m.group(0).lower()
        counts[w] = counts.get(w, 0) + 1
    return counts


def reduce_dicts(dicts: List[Dict[str, int]]) -> Dict[str, int]:
    total: collections.Counter = collections.Counter()
    for d in dicts:
        total.update(d)
    return dict(total)


def visualize_top_words(freq: Dict[str, int], top_n: int = 10, title: str = "Top words") -> None:
    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    if not top:
        logger.warning("No words to visualize")
        return
    words, counts = zip(*top)
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(words)), counts)
    plt.xticks(range(len(words)), words, rotation=45, ha="right")
    plt.title(title)
    plt.tight_layout()
    plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MapReduce word frequency analyzer")
    parser.add_argument("--url", "-u", required=True, help="URL to fetch text from")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Number of threads for Map step")
    parser.add_argument("--top", "-t", type=int, default=10, help="Top N words to visualize")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        text = fetch_text(args.url)
    except Exception as exc:
        logger.exception("Failed to fetch URL: %s", exc)
        raise SystemExit(1)

    parts = chunk_text_by_lines(text, args.workers or 1)
    logger.info("Text split into %d parts", len(parts))

    # Map step in thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as exe:
        futures = [exe.submit(map_count_words, p) for p in parts]
        results: List[Dict[str, int]] = []
        for fut in concurrent.futures.as_completed(futures):
            try:
                results.append(fut.result())
            except Exception:
                logger.exception("Map worker failed")

    # Reduce step
    total = reduce_dicts(results)
    logger.info("Total unique words: %d", len(total))

    visualize_top_words(total, top_n=args.top, title=f"Top {args.top} words from {args.url}")


if __name__ == "__main__":
    main()