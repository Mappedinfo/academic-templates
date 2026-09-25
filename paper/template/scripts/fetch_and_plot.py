#!/usr/bin/env python3
"""Fetch a batch of HTTP/API records concurrently, cache every raw response on
disk, and draw a preview figure from whatever arrived.

    python3 scripts/fetch_and_plot.py --urls config/urls.txt
    python3 scripts/fetch_and_plot.py --urls config/urls.txt --concurrency 16
    python3 scripts/fetch_and_plot.py --urls config/urls.txt --refresh
    python3 scripts/fetch_and_plot.py --selftest      # offline figure check

Why it is written this way
    1. Bounded concurrency: one worker pool keeps `--concurrency` requests in
       flight. A serial `for` loop over an API batch is a bug, not a
       simplification.
    2. Every raw response is cached under `data/cache/`, keyed by URL, so a
       rerun never re-requests what already succeeded and replotting never
       refetches. Cached payloads stay raw; derived values are computed.
    3. Resumable: interrupt it and rerun the same command. Cached items are
       skipped, failed items are retried with exponential backoff.
    4. Look at the figure before writing prose. A figure that cannot be
       regenerated from the cache is not evidence.
    5. Long batches belong in the background, never blocking a conversation:
       run this detached and collect the log and the figure afterwards.

Outputs
    data/cache/<key>.json       cached response per URL (raw body + metadata)
                                (--selftest writes its synthetic records under
                                data/cache/_selftest/ so they never mix with
                                real responses)
    data/fetch_manifest.csv     url, ok, http_status, bytes, fetched_at, error
    figures/fetch-preview.pdf   coverage panel + auto-detected map panel
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLE = Path(__file__).resolve().parent / "matplotlib-style.mplstyle"
USER_AGENT = "academic-templates-fetch-and-plot/1.0"

LAT_KEYS = ("lat", "latitude", "y")
LON_KEYS = ("lon", "lng", "longitude", "x")


def figure_dir(root: Path) -> Path:
    """`figures/`, else `paper/figures/` in the paper-with-code layout."""
    for candidate in (root / "figures", root / "paper" / "figures"):
        if candidate.is_dir():
            return candidate
    return root / "figures"


def cache_path(cache_dir: Path, url: str) -> Path:
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return cache_dir / (key + ".json")


def cached_record(cache_dir: Path, url: str):
    path = cache_path(cache_dir, url)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def is_settled(cache_dir: Path, url: str) -> bool:
    """Cached *and* successful. Failures stay pending so a rerun retries them."""
    record = cached_record(cache_dir, url)
    return bool(record) and bool(record.get("ok"))


def read_urls(path: Path, limit: int) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    urls = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    unique = sorted(set(urls))
    return unique[:limit] if limit > 0 else unique


def decode_body(body: bytes) -> dict:
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        encoded = base64.b64encode(body).decode("ascii")
        return {"kind": "base64", "value": encoded}
    try:
        return {"kind": "json", "value": json.loads(text)}
    except json.JSONDecodeError:
        return {"kind": "text", "value": text}


def fetch(url: str, timeout: float, retries: int) -> dict:
    """One URL with bounded retries and exponential backoff."""
    attempt = 0
    error = ""
    while attempt <= retries:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                return {
                    "ok": True,
                    "http_status": int(response.status),
                    "content_type": response.headers.get("Content-Type", ""),
                    "bytes": len(body),
                    "error": "",
                    "payload": decode_body(body),
                }
        except Exception as exc:  # recorded, never swallowed
            error = type(exc).__name__ + ": " + str(exc)
            if attempt < retries:
                time.sleep(min(2 ** attempt, 30))
        attempt += 1
    return {
        "ok": False,
        "http_status": 0,
        "content_type": "",
        "bytes": 0,
        "error": error,
        "payload": None,
    }


def write_cache(path: Path, url: str, result: dict) -> dict:
    record = {
        "url": url,
        "ok": result["ok"],
        "http_status": result["http_status"],
        "content_type": result["content_type"],
        "bytes": result["bytes"],
        "error": result["error"],
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "payload": result["payload"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)
    return record


def run_fetch(urls, cache_dir, concurrency, timeout, retries, refresh):
    pending = [u for u in urls if refresh or not is_settled(cache_dir, u)]
    reused = len(urls) - len(pending)
    failures = []
    started = time.time()
    if not pending:
        print("all " + str(len(urls)) + " urls cached; nothing to fetch")
        return reused, failures, time.time() - started
    print(
        "fetching "
        + str(len(pending))
        + " of "
        + str(len(urls))
        + " urls, concurrency="
        + str(concurrency)
        + ", "
        + str(reused)
        + " reused from cache",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(fetch, url, timeout, retries): url for url in pending}
        done = 0
        for future in as_completed(futures):
            url = futures[future]
            result = future.result()
            write_cache(cache_path(cache_dir, url), url, result)
            done += 1
            flag = "ok  " if result["ok"] else "FAIL"
            line = (
                "["
                + str(done)
                + "/"
                + str(len(pending))
                + "] "
                + flag
                + " "
                + str(result["http_status"]).rjust(3)
                + " "
                + str(result["bytes"]).rjust(9)
                + " B "
                + url
            )
            if not result["ok"]:
                line += "  <- " + result["error"]
            print(line, flush=True)
            if not result["ok"]:
                failures.append(url)
    return reused, failures, time.time() - started


def load_records(cache_dir: Path, urls) -> list[dict]:
    records = []
    for url in urls:
        path = cache_path(cache_dir, url)
        if not path.exists():
            continue
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            print("warn: unreadable cache for " + url + ": " + str(exc), file=sys.stderr)
    return records


def write_manifest(path: Path, records) -> None:
    fields = ["url", "ok", "http_status", "bytes", "fetched_at", "content_type", "error"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print("wrote " + str(path) + " (" + str(len(records)) + " rows)")


def iter_dicts(value, depth: int = 0):
    if isinstance(value, dict):
        yield value
        if depth < 2:
            for child in value.values():
                yield from iter_dicts(child, depth + 1)
    elif isinstance(value, list) and depth < 2:
        for child in value:
            yield from iter_dicts(child, depth + 1)


def pick_number(record: dict, keys) -> float | None:
    for key in keys:
        value = record.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def extract_points(records) -> list[tuple[float, float]]:
    """Auto-detect lon/lat in cached payloads so the first figure is a map."""
    points = []
    for entry in records:
        payload = entry.get("payload") or {}
        for item in iter_dicts(payload.get("value")):
            lat = pick_number(item, LAT_KEYS)
            lon = pick_number(item, LON_KEYS)
            if lat is None or lon is None:
                continue
            if abs(lat) > 90 or abs(lon) > 180:
                continue
            points.append((lon, lat))
            break
    return points


def plot_preview(records, points, out_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if STYLE.exists():
        plt.style.use(STYLE)

    if points:
        figure, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
        ax_counts, ax_map = axes
    else:
        figure, ax_counts = plt.subplots(figsize=(5.2, 3.2))
        ax_map = None

    ok = sum(1 for record in records if record.get("ok"))
    failed = len(records) - ok
    total_bytes = sum(int(record.get("bytes") or 0) for record in records)

    ax_counts.bar(["ok", "failed"], [ok, failed], color=["#4c72b0", "#c44e52"])
    ax_counts.set_ylabel("records")
    ax_counts.set_title(
        "cached payloads: n=" + str(len(records)) + ", " + format(total_bytes / 1024, ".1f") + " KiB"
    )

    if ax_map is not None:
        ax_map.scatter([p[0] for p in points], [p[1] for p in points], s=14, alpha=0.75)
        ax_map.set_xlabel("longitude")
        ax_map.set_ylabel("latitude")
        ax_map.set_aspect("equal", adjustable="datalim")
        ax_map.set_title("auto-detected coordinates: n=" + str(len(points)))

    figure.suptitle("raw fetch preview - not a result figure", fontsize="small")
    figure.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(out_path)
    plt.close(figure)
    print("wrote " + str(out_path))


def run_selftest(cache_dir: Path) -> list[dict]:
    """Synthetic records so a fresh project can check style/fonts offline."""
    samples = [
        ("selftest://point/a", 22.33, 114.17),
        ("selftest://point/b", 22.30, 114.21),
        ("selftest://point/c", 22.36, 114.13),
        ("selftest://point/d", 31.23, 121.47),
    ]
    records = []
    for url, lat, lon in samples:
        value = {"lat": lat, "lon": lon, "name": url.rsplit("/", 1)[-1]}
        payload = {"kind": "json", "value": value}
        result = {
            "ok": True,
            "http_status": 200,
            "content_type": "application/json",
            "bytes": len(json.dumps(value)),
            "error": "",
            "payload": payload,
        }
        records.append(write_cache(cache_path(cache_dir, url), url, result))
    failed = {
        "ok": False,
        "http_status": 0,
        "content_type": "",
        "bytes": 0,
        "error": "selftest: synthetic failure row",
        "payload": None,
    }
    records.append(write_cache(cache_path(cache_dir, "selftest://fail/a"), "selftest://fail/a", failed))
    print(
        "selftest: wrote "
        + str(len(records))
        + " synthetic records under "
        + str(cache_dir)
        + " (no network used)"
    )
    return records


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--urls", type=Path, help="file with one URL per line (# comments allowed)")
    parser.add_argument("--concurrency", type=int, default=8, help="in-flight requests (default 8)")
    parser.add_argument("--timeout", type=float, default=30.0, help="per-request timeout in seconds")
    parser.add_argument("--retries", type=int, default=2, help="retries per URL with backoff")
    parser.add_argument("--limit", type=int, default=0, help="only the first N urls (0 = all)")
    parser.add_argument("--refresh", action="store_true", help="ignore the cache and refetch")
    parser.add_argument("--allow-partial", action="store_true", help="exit 0 even with failures")
    parser.add_argument("--selftest", action="store_true", help="synthetic figure, no network")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "cache")
    parser.add_argument("--out", type=Path, help="figure path (default figures/fetch-preview.pdf)")
    args = parser.parse_args(argv)

    out_dir = figure_dir(ROOT)

    if args.selftest:
        records = run_selftest(args.cache_dir / "_selftest")
        target = args.out or out_dir / "fetch-selftest.pdf"
        plot_preview(records, extract_points(records), target)
        return 0

    if not args.urls:
        parser.error("--urls is required unless --selftest is used")
    if not args.urls.is_file():
        parser.error("urls file not found: " + str(args.urls))
    if args.concurrency < 1:
        parser.error("--concurrency must be >= 1")

    urls = read_urls(args.urls, args.limit)
    if not urls:
        parser.error("no urls found in " + str(args.urls))

    try:
        reused, failures, elapsed = run_fetch(
            urls, args.cache_dir, args.concurrency, args.timeout, args.retries, args.refresh
        )
    except KeyboardInterrupt:
        print(
            "\ninterrupted - rerun the same command to resume; "
            "finished responses are already cached",
            file=sys.stderr,
        )
        return 130

    records = load_records(args.cache_dir, urls)
    write_manifest(ROOT / "data" / "fetch_manifest.csv", records)
    plot_preview(records, extract_points(records), args.out or out_dir / "fetch-preview.pdf")

    ok = sum(1 for record in records if record.get("ok"))
    print(
        "summary: "
        + str(ok)
        + " ok, "
        + str(len(failures))
        + " failed, "
        + str(reused)
        + " reused from cache, "
        + format(elapsed, ".1f")
        + "s"
    )
    if failures:
        print("failed urls: " + ", ".join(failures[:10]), file=sys.stderr)
        if not args.allow_partial:
            print("rerun to retry only the failures, or pass --allow-partial", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
