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
TALL_VIEWPORT = 2200   # tall enough to lay the whole app out without scrolling

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
            "one grant that was never written. The first time this test ran for real, "
            "it returned the note, because the role had secondary roles still active. "
            "One statement fixed it: use secondary roles none."
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
    """One framed still per beat.

    Streamlit scrolls an inner container, so window.scrollTo and
    scroll_into_view_if_needed are both unreliable here. Instead render the whole
    page tall, measure the anchor element, and take a full-page screenshot clipped
    to a 1280x720 window around it. Deterministic, and every beat is guaranteed to
    frame the thing its narration is talking about.
    """
    from playwright.sync_api import sync_playwright

    shots: list[Path] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        # Streamlit scrolls section[data-testid="stMain"], and document.body has
        # zero height, so a "scroll then shoot" loop captures the same frame every
        # time. Render tall enough that the whole app is laid out at once, then clip.
        page = browser.new_page(viewport={"width": WIDTH, "height": TALL_VIEWPORT})
        page.goto(url, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(5000)
        page.get_by_text("Warehouse status", exact=False).first.wait_for(timeout=30_000)
        page.wait_for_timeout(1500)

        total = page.evaluate(
            "() => { const m = document.querySelector('section[data-testid=\"stMain\"]');"
            "  return m ? m.scrollHeight : document.documentElement.scrollHeight; }"
        )
        for beat in BEATS:
            top = _anchor_top(page, beat["action"])
            top = max(0, min(top, max(0, total - HEIGHT)))
            path = workdir / f"{beat['name']}.png"
            page.screenshot(
                path=str(path),
                clip={"x": 0, "y": top, "width": WIDTH, "height": HEIGHT},
            )
            shots.append(path)
        browser.close()
    return shots


# Streamlit scrolls an inner container, not the window. Anchor each beat on real
# text and frame the shot from that element's measured position.
_ANCHORS = {
    "top": "Publish your impact without publishing your people.",
    "left": "Stays in the warehouse",
    "denied": "The read this app is not allowed to make",
    "right": "Impact brief",
    "status": "Warehouse status",
}

# How far above the anchor the frame starts, so the heading is not flush to the edge.
_HEADROOM = 70


def _anchor_top(page, action: str) -> float:
    text = _ANCHORS.get(action)
    if not text:
        return 0.0
    box = page.get_by_text(text, exact=False).first.bounding_box()
    if not box:
        return 0.0
    return box["y"] - _HEADROOM


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
    listing.write_text("".join(f"file '{seg.name}'\n" for seg in segments))
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "segments.txt",
         "-c", "copy", str(out.resolve())],
        cwd=work, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed:\n{result.stderr[-2000:]}")
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
