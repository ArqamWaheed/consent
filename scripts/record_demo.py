#!/usr/bin/env python3
"""Record the demo: drive the app with Playwright, narrate it with Piper, mux with ffmpeg.

Not part of the product. Kept in the repo because a demo you cannot regenerate is
a demo you cannot fix.

Usage:  .venv/bin/python scripts/record_demo.py --out demo/consent-demo.mp4
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = Path(
    "/tmp/claude-1000/-home-arqamwd-theodinproject-repos-consent/"
    "4f002b7f-8c8d-4f95-a62d-120279e167dd/scratchpad"
)
VOICE = SCRATCH / "voices" / "en_GB-alba-medium.onnx"
WIDTH, HEIGHT = 1280, 720

# Each beat: how long the camera holds, and what is said over it.
BEATS = [
    dict(
        name="open",
        say=(
            "A charity's proof of impact is made of other people's private lives. "
            "So the proof never gets published. Consent keeps the raw record inside "
            "the warehouse, and lets only the redacted truth out."
        ),
        action="top",
    ),
    dict(
        name="left",
        say=(
            "On the left is what stays in Snowflake. Sixty private records. The app "
            "knows how many, because a view runs with its owner's rights. It does not "
            "know who, because it was never granted the table."
        ),
        action="left",
    ),
    dict(
        name="denied",
        say=(
            "This is the app deliberately trying to read the private note, and being "
            "refused by the engine. Not hidden by the interface. Refused, because of "
            "one grant that was never written."
        ),
        action="denied",
    ),
    dict(
        name="right",
        say=(
            "On the right is everything the charity may publish. Redacted notes, a "
            "need category, an open flag, and a written brief. Every name, phone "
            "number, address and reference is gone."
        ),
        action="right",
    ),
    dict(
        name="status",
        say=(
            "And the status panel probes each Cortex function live. Most of them are "
            "red on this account. Nine of eleven refused, so the whole pipeline was "
            "rebuilt out of the one that answered."
        ),
        action="status",
    ),
    dict(
        name="close",
        say=(
            "The data does not move. Only the safe part does. That is the whole "
            "project, and it is one grant away from being true on any account."
        ),
        action="top",
    ),
]


def say(text: str, out_wav: Path) -> float:
    """Render narration and return its duration in seconds."""
    subprocess.run(
        [str(ROOT / ".venv/bin/python"), "-m", "piper", "-m", str(VOICE), "-f", str(out_wav)],
        input=text.encode(),
        check=True,
        capture_output=True,
    )
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(out_wav)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(dur)


def shoot(url: str, workdir: Path, durations: list[float]) -> list[Path]:
    """Screenshot the app once per beat, scrolled to the region that beat describes."""
    from playwright.sync_api import sync_playwright

    shots: list[Path] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
        page.goto(url, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(4000)
        for beat in BEATS:
            _position(page, beat["action"])
            page.wait_for_timeout(900)
            path = workdir / f"{beat['name']}.png"
            page.screenshot(path=str(path))
            shots.append(path)
        browser.close()
    return shots


def _position(page, action: str) -> None:
    targets = {
        "top": 0,
        "left": 380,
        "denied": 780,
        "right": 380,
        "status": 2200,
    }
    page.mouse.wheel(0, 0)
    page.evaluate(f"window.scrollTo(0, {targets.get(action, 0)})")


def build(shots: list[Path], wavs: list[Path], durations: list[float], out: Path) -> None:
    """One still per beat, held for exactly as long as its narration runs."""
    work = out.parent / "_segments"
    work.mkdir(parents=True, exist_ok=True)
    segments = []
    for i, (shot, wav, dur) in enumerate(zip(shots, wavs, durations)):
        seg = work / f"seg{i:02d}.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", str(shot), "-i", str(wav),
             "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", "-shortest",
             "-t", f"{dur + 0.6:.2f}",
             "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                    f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x0E1117",
             "-r", "30", str(seg)],
            check=True, capture_output=True,
        )
        segments.append(seg)

    listing = work / "segments.txt"
    listing.write_text("".join(f"file '{s.name}'\n" for s in segments))
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-c", "copy", str(out)],
        check=True, cwd=work, capture_output=True,
    )
    shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8501")
    ap.add_argument("--out", default=str(ROOT / "demo" / "consent-demo.mp4"))
    args = ap.parse_args()

    if not VOICE.exists():
        print(f"Voice model missing: {VOICE}", file=sys.stderr)
        return 1

    work = SCRATCH / "demo_build"
    work.mkdir(parents=True, exist_ok=True)

    wavs, durations = [], []
    for beat in BEATS:
        wav = work / f"{beat['name']}.wav"
        durations.append(say(beat["say"], wav))
        wavs.append(wav)
    print(f"narration: {sum(durations):.1f}s across {len(BEATS)} beats")

    shots = shoot(args.url, work, durations)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    build(shots, wavs, durations, out)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
