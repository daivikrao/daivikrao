#!/usr/bin/env python3
"""daivik.service: records profile pings and renders the terminal status card.

Usage:
  python scripts/ping.py record   # reads PING_USER / PING_AT from env, appends a ping
  python scripts/ping.py render   # renders assets/status.svg and refreshes README cache key
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "pings.json"
SVG = ROOT / "assets" / "status.svg"
README = ROOT / "README.md"
REPLY = ROOT / "reply.md"
TZ = ZoneInfo("America/Chicago")
RECENT_KEEP = 25          # pings kept in history file
RECENT_SHOWN = 4          # pings shown in the terminal
COOLDOWN = timedelta(minutes=30)  # same user pinging again within this window isn't logged twice
USER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")

# ── palette (GitHub dark) ────────────────────────────────────────────────
BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
FG, DIM = "#c9d1d9", "#8b949e"
GREEN, BLUE, PURPLE, ORANGE, YELLOW = "#3fb950", "#58a6ff", "#d2a8ff", "#ffa657", "#e3b341"


def load():
    if DATA.exists():
        return json.loads(DATA.read_text())
    return {"total": 0, "users": [], "recent": []}


def save(d):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(d, indent=2) + "\n")


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def record():
    user = os.environ.get("PING_USER", "").strip()
    at = os.environ.get("PING_AT", "").strip() or datetime.now(timezone.utc).isoformat()
    if not USER_RE.match(user) and not user.endswith("[bot]"):
        sys.exit(f"refusing odd username: {user!r}")
    d = load()
    now = parse_ts(at)
    recent_same = [p for p in d["recent"] if p["user"].lower() == user.lower()]
    duplicate = bool(recent_same) and now - parse_ts(recent_same[-1]["at"]) < COOLDOWN
    if not duplicate:
        d["total"] += 1
        if user.lower() not in (u.lower() for u in d["users"]):
            d["users"].append(user)
        d["recent"] = (d["recent"] + [{"user": user, "at": now.isoformat()}])[-RECENT_KEEP:]
        save(d)
        body = (
            f"🟢 **200 OK** — ping received from @{user}.\n\n"
            f"You're ping **#{d['total']}** to `daivik.service`. Your ping is now logged in the terminal on "
            f"[my profile](https://github.com/daivikrao) (it can take a few minutes for GitHub's image cache to refresh).\n\n"
            "Thanks for stopping by! 👋\n\n"
            "<sub>Handled automatically by a GitHub Action — "
            "[see how it works](https://github.com/daivikrao/daivikrao/blob/main/.github/workflows/ping.yml).</sub>"
        )
    else:
        body = (
            f"🟡 **429 Too Many Requests** — easy there, @{user}! You pinged in the last "
            f"{int(COOLDOWN.total_seconds() // 60)} minutes, so this one wasn't logged again. Thanks for the enthusiasm 😄"
        )
    REPLY.write_text(body + "\n")
    print(body)


# ── rendering ────────────────────────────────────────────────────────────
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SIZE = 14
CHAR_W = SIZE * 0.61
LINE_H = 21
PAD_X = 22
TOP = 36  # title bar height


def seg(text, color=FG, bold=False):
    return (text, color, bold)


def build_lines(d):
    pings = d["recent"][-RECENT_SHOWN:]
    total = d["total"]
    last = f" · last from @{pings[-1]['user']}" if pings else " · be the first! ↓"

    L = []  # (kind, segments) kind: cmd | out | blank
    L.append(("cmd", [seg("systemctl status daivik.service")]))
    L.append(("out", [seg("● ", GREEN, True), seg("daivik.service", FG, True), seg(" - Daivik · Software Engineer", FG)]))
    L.append(("out", [seg("     Loaded: ", DIM), seg("loaded", GREEN), seg(" (Texas A&M University; Master of Computer Science)", FG)]))
    L.append(("out", [seg("     Active: ", DIM), seg("active (running)", GREEN, True), seg(" since Aug 2023; 3 yrs shipping @ Fidelity", FG)]))
    L.append(("out", [seg("   Location: ", DIM), seg("College Station, TX", FG), seg(" (from Bangalore)", DIM)]))
    L.append(("out", [seg("     Status: ", DIM), seg('"Open to Summer 2027 internships: SWE · Platform · PE"', YELLOW)]))
    L.append(("out", [seg("      Pings: ", DIM), seg(f"{total} received", PURPLE), seg(last, DIM)]))
    L.append(("blank", []))
    L.append(("cmd", [seg("journalctl -u daivik --no-pager")]))
    L.append(("out", [seg("2023          ", DIM), seg("daivik[1]: ", BLUE), seg("started SWE internship @ Fidelity Investments", FG)]))
    L.append(("out", [seg("2023          ", DIM), seg("daivik[1]: ", BLUE), seg("graduated B.E. ISE @ B.M.S. College of Engineering", FG)]))
    L.append(("out", [seg("Aug 2023      ", DIM), seg("daivik[1]: ", BLUE), seg("promoted to production: Software Engineer @ Fidelity", FG)]))
    L.append(("out", [seg("Aug 2026      ", DIM), seg("daivik[1]: ", BLUE), seg("forked to Texas A&M: Master of Computer Science", FG)]))
    if pings:
        for p in pings:
            t = parse_ts(p["at"]).astimezone(TZ)
            stamp = t.strftime("%b %d %H:%M")
            L.append(("out", [seg(f"{stamp:<14}", DIM), seg("daivik[1]: ", BLUE), seg("ping from ", FG),
                              seg(f"@{p['user']}", PURPLE), seg(" → ", DIM), seg("200 OK", GREEN, True)]))
    else:
        L.append(("out", [seg("now           ", DIM), seg("daivik[1]: ", BLUE), seg("listening for pings… hit the button below", ORANGE)]))
    L.append(("blank", []))
    L.append(("prompt", []))
    return L


def text_len(segs):
    return sum(len(s[0]) for s in segs)


def render():
    d = load()
    if not DATA.exists():
        save(d)
    lines = build_lines(d)
    longest = max(text_len(s) + (16 if k == "cmd" else 0) for k, s in lines)
    width = max(860, int(PAD_X * 2 + longest * CHAR_W) + 10)
    height = TOP + 18 + LINE_H * len(lines) + 12

    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
      f'role="img" aria-label="systemctl status daivik.service">')
    a(f'<style>text{{font-family:{FONT};font-size:{SIZE}px;white-space:pre}} .b{{font-weight:700}}</style>')
    a("<defs>")
    clip_defs_at = len(out)
    a("</defs>")
    # window
    a(f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>')
    a(f'<path d="M0.5 10.5a10 10 0 0 1 10-10h{width-21}a10 10 0 0 1 10 10v{TOP-10}h-{width-1}z" fill="{BAR}" stroke="{BORDER}"/>')
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        a(f'<circle cx="{22 + i*20}" cy="18" r="6" fill="{c}"/>')
    a(f'<text x="{width/2}" y="23" fill="{DIM}" text-anchor="middle" style="font-size:12px">daivik@tamu: ~</text>')

    clips = []
    t = 0.4
    y = TOP + 18 + 14
    for idx, (kind, segs) in enumerate(lines):
        if kind == "blank":
            y += LINE_H
            t += 0.15
            continue
        if kind in ("cmd", "prompt"):
            prompt = [seg("daivik@tamu", GREEN, True), seg(":", FG), seg("~", BLUE, True), seg("$ ", FG)]
            prompt_w = text_len(prompt) * CHAR_W
            a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.01s" fill="freeze"/>')
            a(f'<text x="{PAD_X}" y="{y}">' + "".join(_tspan(s) for s in prompt) + "</text>")
            if kind == "cmd":
                cmd_w = text_len(segs) * CHAR_W + 4
                dur = 0.045 * text_len(segs)
                cid = f"c{idx}"
                clips.append(f'<clipPath id="{cid}"><rect x="{PAD_X + prompt_w:.1f}" y="{y-16}" width="0" height="22">'
                             f'<animate attributeName="width" from="0" to="{cmd_w:.1f}" begin="{t+0.35:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
                             f'</rect></clipPath>')
                a(f'<text x="{PAD_X + prompt_w:.1f}" y="{y}" clip-path="url(#{cid})">' + "".join(_tspan(s) for s in segs) + "</text>")
                t += 0.35 + dur + 0.35
            else:  # final prompt with blinking cursor
                a(f'<rect x="{PAD_X + prompt_w:.1f}" y="{y-13}" width="8" height="16" fill="{FG}">'
                  f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>')
            a("</g>")
        else:
            a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.2s" fill="freeze"/>')
            # pulsing status dot on the service line
            if segs and segs[0][0].startswith("●"):
                a(f'<text x="{PAD_X}" y="{y}"><tspan fill="{GREEN}" class="b">●<animate attributeName="opacity" '
                  f'values="1;0.35;1" dur="2s" repeatCount="indefinite"/></tspan></text>')
                rest = segs[1:]
                a(f'<text x="{PAD_X + 2*CHAR_W:.1f}" y="{y}">' + "".join(_tspan(s) for s in rest) + "</text>")
            else:
                a(f'<text x="{PAD_X}" y="{y}">' + "".join(_tspan(s) for s in segs) + "</text>")
            a("</g>")
            t += 0.12
        y += LINE_H
    out[clip_defs_at:clip_defs_at] = clips
    a("</svg>")
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text("\n".join(out) + "\n")

    # bust GitHub's image cache so the profile picks up the new SVG quickly
    if README.exists():
        key = f"{d['total']}-{d['recent'][-1]['at'][:16].replace(':', '') if d['recent'] else 'init'}"
        readme = README.read_text()
        new = re.sub(r"(assets/status\.svg)\?v=[\w\-.:+]*", rf"\1?v={key}", readme)
        if new != readme:
            README.write_text(new)
    print(f"rendered {SVG.relative_to(ROOT)} ({len(lines)} lines, {d['total']} pings)")


def _tspan(s):
    text, color, bold = s
    cls = ' class="b"' if bold else ""
    return f'<tspan fill="{color}"{cls}>{escape(text)}</tspan>'


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    {"record": record, "render": render}[cmd]()
