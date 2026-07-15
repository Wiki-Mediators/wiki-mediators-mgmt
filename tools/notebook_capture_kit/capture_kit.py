#!/usr/bin/env python3
"""Notebook-side, stills-first object capture ingestion and quality checks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

TOOL_DIR = Path(__file__).resolve().parent
VENDOR_DIR = TOOL_DIR / "vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

import cv2  # type: ignore  # noqa: E402
import numpy as np  # type: ignore  # noqa: E402
from PIL import Image  # type: ignore  # noqa: E402

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
MANIFEST_FIELDS = [
    "frame_id", "source_name", "accepted_name", "status", "reason",
    "source_sha256", "accepted_sha256", "width", "height", "blur_score",
    "mean_luma", "dark_fraction", "bright_fraction", "exif_present_source",
    "exif_removed", "camera_type", "captured_at_utc", "processed_at_utc",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip()).strip("-").lower()
    return value or "object"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def has_exif(data: bytes) -> bool:
    try:
        with Image.open(io.BytesIO(data)) as image:
            return bool(image.getexif())
    except Exception:
        return False


@dataclass(frozen=True)
class Thresholds:
    blur_min: float = 20.0
    mean_min: float = 35.0
    mean_max: float = 225.0
    clipped_fraction_max: float = 0.85


@dataclass
class CheckResult:
    readable: bool
    accepted: bool
    reason: str
    width: int = 0
    height: int = 0
    blur_score: float = 0.0
    mean_luma: float = 0.0
    dark_fraction: float = 0.0
    bright_fraction: float = 0.0


def decode_image(data: bytes) -> np.ndarray | None:
    return cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)


def check_image(data: bytes, thresholds: Thresholds) -> tuple[CheckResult, np.ndarray | None]:
    image = decode_image(data)
    if image is None or image.size == 0:
        return CheckResult(False, False, "unreadable"), None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean = float(gray.mean())
    dark = float(np.mean(gray <= 10))
    bright = float(np.mean(gray >= 245))
    reasons: list[str] = []
    if blur < thresholds.blur_min:
        reasons.append("blur")
    if mean < thresholds.mean_min or dark > thresholds.clipped_fraction_max:
        reasons.append("underexposed")
    if mean > thresholds.mean_max or bright > thresholds.clipped_fraction_max:
        reasons.append("overexposed")
    return CheckResult(
        readable=True,
        accepted=not reasons,
        reason="accepted" if not reasons else "+".join(reasons),
        width=width,
        height=height,
        blur_score=round(blur, 3),
        mean_luma=round(mean, 3),
        dark_fraction=round(dark, 6),
        bright_fraction=round(bright, 6),
    ), image


def sanitize_jpeg(image: np.ndarray, quality: int = 95) -> bytes:
    ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("OpenCV could not encode sanitized JPEG")
    sanitized = encoded.tobytes()
    if has_exif(sanitized):
        raise RuntimeError("EXIF verification failed after sanitization")
    return sanitized


def unique_destination(folder: Path, name: str) -> Path:
    candidate = folder / name
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    counter = 2
    while True:
        candidate = folder / f"{stem}_{counter:02d}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def ensure_session(session: Path) -> None:
    required = ["incoming", "images", "originals", "rejected", "checks"]
    missing = [name for name in required if not (session / name).is_dir()]
    if missing or not (session / "capture_session.md").is_file() or not (session / "manifest.csv").is_file():
        raise SystemExit(f"Not a capture-kit session: {session} (missing: {', '.join(missing)})")


def init_session(args: argparse.Namespace) -> int:
    sessions_root = Path(args.sessions_root).resolve()
    session_id = args.session_id or f"{datetime.now():%Y%m%d_%H%M%S}_{slugify(args.object)}"
    session = sessions_root / session_id
    if session.exists():
        raise SystemExit(f"Session already exists: {session}")
    for name in ["incoming", "images", "originals", "rejected", "checks"]:
        (session / name).mkdir(parents=True, exist_ok=True)
    log = f"""---
session_id: {session_id}
created_utc: {utc_now()}
object: {args.object}
purpose: {args.purpose}
camera_type: {args.camera_type}
status: capture-ready
---

# Capture Session — {args.object}

- Lighting: {args.lighting}
- Scale reference: {args.scale_reference}
- Coarse known dimension: {args.known_dimension}
- Operator notes: {args.notes}
- Planned passes: level orbit, high orbit, regrip/opposite orientation
- Privacy: physical shutter opens only during active capture; microphone unused
"""
    (session / "capture_session.md").write_text(log, encoding="utf-8")
    with (session / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS).writeheader()
    config = {
        "schema": "notebook_capture_session_v1",
        "session_id": session_id,
        "camera_type": args.camera_type,
        "thresholds": asdict(Thresholds(args.blur_min, args.mean_min, args.mean_max, args.clipped_fraction_max)),
        "metronome_interval_seconds": args.interval,
    }
    (session / "checks" / "session_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(session)
    return 0


def manifest_rows(session: Path) -> list[dict[str, str]]:
    with (session / "manifest.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def append_manifest(session: Path, row: dict[str, object]) -> None:
    normalized = {field: row.get(field, "") for field in MANIFEST_FIELDS}
    with (session / "manifest.csv").open("a", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS).writerow(normalized)


def process_file(session: Path, source: Path, thresholds: Thresholds, camera_type: str) -> dict[str, object]:
    data = source.read_bytes()
    source_hash = sha256_bytes(data)
    prior_hashes = {row["source_sha256"] for row in manifest_rows(session)}
    frame_id = f"F{len(manifest_rows(session)) + 1:04d}"
    processed_at = utc_now()
    captured_at = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    exif_source = has_exif(data)
    if source_hash in prior_hashes:
        result = CheckResult(False, False, "duplicate")
        image = None
    else:
        result, image = check_image(data, thresholds)

    accepted_name = ""
    accepted_hash = ""
    exif_removed = False
    if result.accepted and image is not None:
        accepted_name = f"{frame_id}.jpg"
        sanitized = sanitize_jpeg(image)
        accepted_path = session / "images" / accepted_name
        accepted_path.write_bytes(sanitized)
        accepted_hash = sha256_file(accepted_path)
        exif_removed = not has_exif(accepted_path.read_bytes())
        original_path = unique_destination(session / "originals", source.name)
        shutil.move(str(source), str(original_path))
        status = "accepted"
    else:
        reject_path = unique_destination(session / "rejected", source.name)
        shutil.move(str(source), str(reject_path))
        status = "rejected"

    row: dict[str, object] = {
        "frame_id": frame_id,
        "source_name": source.name,
        "accepted_name": accepted_name,
        "status": status,
        "reason": result.reason,
        "source_sha256": source_hash,
        "accepted_sha256": accepted_hash,
        "width": result.width,
        "height": result.height,
        "blur_score": result.blur_score,
        "mean_luma": result.mean_luma,
        "dark_fraction": result.dark_fraction,
        "bright_fraction": result.bright_fraction,
        "exif_present_source": str(exif_source).lower(),
        "exif_removed": str(exif_removed).lower(),
        "camera_type": camera_type,
        "captured_at_utc": captured_at,
        "processed_at_utc": processed_at,
    }
    append_manifest(session, row)
    receipt = {"schema": "capture_check_v1", **row, "thresholds": asdict(thresholds)}
    (session / "checks" / f"{frame_id}.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"{frame_id} {status}: {source.name} ({result.reason})")
    return row


def incoming_files(session: Path) -> Iterable[Path]:
    for path in sorted((session / "incoming").iterdir()):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def process_incoming(session: Path, thresholds: Thresholds, camera_type: str) -> int:
    ensure_session(session)
    count = 0
    for source in incoming_files(session):
        process_file(session, source, thresholds, camera_type)
        count += 1
    return count


def copy_stable_new_files(
    source_dir: Path,
    incoming: Path,
    baseline: set[Path],
    observed_sizes: dict[Path, int],
) -> int:
    """Copy newly created source photos after their size is stable for two polls."""
    copied = 0
    for source in sorted(source_dir.iterdir()):
        if not source.is_file() or source.suffix.lower() not in IMAGE_EXTENSIONS or source in baseline:
            continue
        size = source.stat().st_size
        prior = observed_sizes.get(source)
        observed_sizes[source] = size
        if prior is None or prior != size or size == 0:
            continue
        target = unique_destination(incoming, source.name)
        shutil.copy2(source, target)
        baseline.add(source)
        observed_sizes.pop(source, None)
        print(f"Copied new Camera photo: {source.name}")
        copied += 1
    return copied


def beep(frequency: int = 880, duration_ms: int = 120) -> None:
    if os.name == "nt":
        import winsound
        winsound.Beep(frequency, duration_ms)
    else:
        print("\a", end="", flush=True)


def startup_signal(prep_seconds: float) -> None:
    beep(660, 100)
    time.sleep(0.12)
    beep(660, 100)
    print(f"Preparation window: {prep_seconds:g}s — turn on lights, open shutter, and hold the first pose.")
    time.sleep(max(0.0, prep_seconds))
    beep(1200, 450)
    print("Capture sequence started. First snapshot follows after one interval.")


def watch(args: argparse.Namespace) -> int:
    session = Path(args.session).resolve()
    thresholds = Thresholds(args.blur_min, args.mean_min, args.mean_max, args.clipped_fraction_max)
    ensure_session(session)
    source_dir = Path(args.source_dir).expanduser().resolve() if args.source_dir else None
    if source_dir:
        source_dir.mkdir(parents=True, exist_ok=True)
    baseline = {
        path for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    } if source_dir else set()
    observed_sizes: dict[Path, int] = {}
    source_note = f" and new photos from {source_dir}" if source_dir else ""
    print(f"Watching {session / 'incoming'}{source_note}; Ctrl+C stops. Interval={args.interval:g}s")
    started = time.monotonic()
    next_beep = time.monotonic()
    try:
        while True:
            if args.duration > 0 and time.monotonic() - started >= args.duration:
                print(f"Duration reached ({args.duration:g}s). Watcher stopped.")
                break
            if source_dir:
                copy_stable_new_files(source_dir, session / "incoming", baseline, observed_sizes)
            process_incoming(session, thresholds, args.camera_type)
            now = time.monotonic()
            if args.beep and now >= next_beep:
                beep()
                next_beep = now + args.interval
            time.sleep(args.poll)
    except KeyboardInterrupt:
        print("\nWatcher stopped.")
    return 0


def ingest(args: argparse.Namespace) -> int:
    session = Path(args.session).resolve()
    thresholds = Thresholds(args.blur_min, args.mean_min, args.mean_max, args.clipped_fraction_max)
    if args.files:
        ensure_session(session)
        incoming = session / "incoming"
        for item in args.files:
            source = Path(item).resolve()
            if not source.is_file():
                raise SystemExit(f"Input file not found: {source}")
            target = unique_destination(incoming, source.name)
            shutil.copy2(source, target)
    count = process_incoming(session, thresholds, args.camera_type)
    print(f"Processed {count} file(s).")
    return 0


def open_camera(index: int, width: int, height: int) -> cv2.VideoCapture:
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY
    camera = cv2.VideoCapture(index, backend)
    if not camera.isOpened():
        camera.release()
        raise SystemExit(
            "Camera could not be opened. Close other camera applications, open the physical shutter, and retry."
        )
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return camera


def capture(args: argparse.Namespace) -> int:
    session = Path(args.session).resolve()
    ensure_session(session)
    thresholds = Thresholds(args.blur_min, args.mean_min, args.mean_max, args.clipped_fraction_max)
    camera = open_camera(args.camera_index, args.width, args.height)
    total = args.shots if args.shots > 0 else max(1, int(args.duration // args.interval))
    accepted = 0
    rejected = 0
    print(
        f"Direct capture: {total} snapshot(s), every {args.interval:g}s. "
        "Rotate after each shot, then hold still for the next beep. Ctrl+C stops."
    )
    try:
        startup_signal(args.prep_seconds)
        # Warm up exposure and discard stale startup frames.
        for _ in range(8):
            camera.read()
        next_capture = time.monotonic() if args.immediate else time.monotonic() + args.interval
        for shot_number in range(1, total + 1):
            time.sleep(max(0.0, next_capture - time.monotonic()))
            # Pull the freshest available frame before marking the capture moment.
            frame = None
            ok = False
            for _ in range(3):
                ok, frame = camera.read()
            beep()
            if not ok or frame is None:
                print(f"Shot {shot_number:03d}: camera frame unavailable")
                rejected += 1
            else:
                source = session / "incoming" / f"direct_{shot_number:04d}.png"
                if not cv2.imwrite(str(source), frame):
                    raise RuntimeError(f"Could not write camera frame: {source.name}")
                row = process_file(session, source, thresholds, args.camera_type)
                if row["status"] == "accepted":
                    accepted += 1
                else:
                    rejected += 1
            next_capture += args.interval
    except KeyboardInterrupt:
        print("\nDirect capture stopped by operator.")
    finally:
        camera.release()
    review_folder = session / ("images" if accepted else "rejected")
    print(f"Capture complete: accepted={accepted}, rejected={rejected}, review={review_folder}")
    if args.open_folder and os.name == "nt":
        os.startfile(review_folder)  # type: ignore[attr-defined]
    return 0


def add_threshold_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--blur-min", type=float, default=20.0)
    parser.add_argument("--mean-min", type=float, default=35.0)
    parser.add_argument("--mean-max", type=float, default=225.0)
    parser.add_argument("--clipped-fraction-max", type=float, default=0.85)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create a capture session before taking photos")
    init.add_argument("--object", required=True)
    init.add_argument("--purpose", default="reconstruction-feasibility")
    init.add_argument("--camera-type", choices=["webcam", "phone", "mixed"], default="webcam")
    init.add_argument("--lighting", required=True)
    init.add_argument("--scale-reference", required=True)
    init.add_argument("--known-dimension", default="coarse ruler reference +/-0.5 mm")
    init.add_argument("--notes", default="none")
    init.add_argument("--sessions-root", default=str(TOOL_DIR / "sessions"))
    init.add_argument("--session-id")
    init.add_argument("--interval", type=float, default=3.0)
    add_threshold_args(init)
    init.set_defaults(func=init_session)

    ingest_parser = sub.add_parser("ingest", help="Process current incoming photos once")
    ingest_parser.add_argument("session")
    ingest_parser.add_argument("files", nargs="*")
    ingest_parser.add_argument("--camera-type", choices=["webcam", "phone", "mixed"], default="webcam")
    add_threshold_args(ingest_parser)
    ingest_parser.set_defaults(func=ingest)

    watcher = sub.add_parser("watch", help="Watch incoming/ and check new photos")
    watcher.add_argument("session")
    watcher.add_argument("--camera-type", choices=["webcam", "phone", "mixed"], default="webcam")
    watcher.add_argument("--interval", type=float, default=3.0)
    watcher.add_argument("--poll", type=float, default=0.5)
    watcher.add_argument("--duration", type=float, default=0.0, help="Stop after this many seconds; 0 runs until Ctrl+C")
    watcher.add_argument(
        "--source-dir",
        default=str(Path.home() / "Pictures" / "Camera Roll"),
        help="Watch this Camera app folder for new photos; pass an empty value to watch incoming/ only",
    )
    watcher.add_argument("--beep", action=argparse.BooleanOptionalAction, default=True)
    add_threshold_args(watcher)
    watcher.set_defaults(func=watch)

    direct = sub.add_parser("capture", help="Directly take timed snapshots from the integrated camera")
    direct.add_argument("session")
    direct.add_argument("--camera-type", choices=["webcam", "phone", "mixed"], default="webcam")
    direct.add_argument("--camera-index", type=int, default=0)
    direct.add_argument("--width", type=int, default=1920)
    direct.add_argument("--height", type=int, default=1080)
    direct.add_argument("--interval", type=float, default=3.0)
    direct.add_argument("--prep-seconds", type=float, default=10.0)
    direct.add_argument("--duration", type=float, default=60.0)
    direct.add_argument("--shots", type=int, default=0, help="Exact shot count; overrides duration when positive")
    direct.add_argument("--immediate", action="store_true", help="Take the first shot immediately instead of after one interval")
    direct.add_argument("--open-folder", action=argparse.BooleanOptionalAction, default=True)
    add_threshold_args(direct)
    direct.set_defaults(func=capture)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
