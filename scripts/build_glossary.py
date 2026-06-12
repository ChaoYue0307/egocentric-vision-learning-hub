#!/usr/bin/env python3
"""Compile the three sibling repos' docs/concepts.md into docs/glossary.html."""
from __future__ import annotations

import html
import re
from pathlib import Path

SOURCES = [
    ("Action Recognition", "egocentric-action-baselines", "#38bdf8"),
    ("3D Reconstruction", "egocentric-3d-reconstruction-demo", "#f59e0b"),
    ("Scene Graph Memory", "scene-graph-from-egocentric-video", "#a78bfa"),
]

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Glossary · Egocentric Vision Learning Hub</title>
  <style>
    :root {{ color-scheme: light dark; --bg:#090f1d; --panel:#101a2d; --text:#eef4ff; --muted:#a8b4c7; --line:#2a3a5a; --a:#38bdf8; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--text); background: radial-gradient(circle at 12% 0%, #1e3a8a, transparent 32%), radial-gradient(circle at 90% 8%, #581c87, transparent 32%), linear-gradient(145deg,#090f1d,#0f172a); }}
    a {{ color:var(--a); text-decoration:none; }}
    main {{ max-width:980px; margin:auto; padding:42px 20px 72px; }}
    .topbar {{ position:sticky; top:0; z-index:3; backdrop-filter:blur(18px); border-bottom:1px solid rgba(148,163,184,.16); background:rgba(9,15,29,.74); }}
    .topbar-inner {{ max-width:980px; margin:auto; padding:12px 20px; display:flex; justify-content:space-between; gap:16px; align-items:center; }}
    .nav a {{ border:1px solid var(--line); border-radius:999px; padding:8px 12px; color:var(--muted); font-size:.9rem; margin-left:8px; }}
    .nav a:hover {{ border-color:var(--a); color:var(--text); }}
    h1 {{ font-size:clamp(2rem,5vw,3.4rem); letter-spacing:-.05em; margin:18px 0; }}
    h2.section {{ margin:42px 0 6px; letter-spacing:-.03em; border-left:5px solid var(--accent, var(--a)); padding-left:14px; }}
    .source {{ color:var(--muted); margin:0 0 18px 19px; font-size:.92rem; }}
    .card {{ border:1px solid var(--line); border-radius:20px; padding:20px 24px; background:color-mix(in srgb, var(--panel) 88%, transparent); margin-bottom:14px; }}
    .card h3 {{ margin:0 0 8px; }}
    .card p {{ color:var(--muted); line-height:1.62; margin:8px 0; }}
    .card pre {{ overflow:auto; border:1px solid var(--line); border-radius:12px; padding:12px; background:#020617; color:#bfdbfe; }}
    .toc {{ border:1px solid var(--line); border-radius:20px; padding:18px 24px; background:#0b1220; columns:2; }}
    .toc a {{ display:block; color:var(--muted); padding:3px 0; break-inside:avoid; }}
    .toc a:hover {{ color:var(--text); }}
    @media (max-width:700px) {{ .toc {{ columns:1; }} }}
  </style>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <strong>Egocentric Vision Learning Hub</strong>
    <nav class="nav">
      <a href="index.html">Hub</a>
      <a href="article.html">Narrative</a>
    </nav>
  </div>
</header>
<main>
  <h1>Unified Glossary</h1>
  <p style="color:var(--muted)">Every concept from the three project glossaries, cross-linked in one place. Generated from each repo's <code>docs/concepts.md</code> by <code>scripts/build_glossary.py</code>.</p>
  <div class="toc">
{toc}
  </div>
{sections}
</main>
</body>
</html>
"""


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def md_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def parse_concepts(md_path: Path) -> list[tuple[str, str]]:
    entries = []
    title, lines = None, []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if title:
                entries.append((title, "\n".join(lines).strip()))
            title, lines = line[3:].strip(), []
        elif title is not None:
            lines.append(line)
    if title:
        entries.append((title, "\n".join(lines).strip()))
    return entries


def body_to_html(body: str) -> str:
    parts = []
    in_code = False
    paragraph: list[str] = []

    def flush():
        if paragraph:
            parts.append(f"<p>{md_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    for line in body.splitlines():
        if line.strip().startswith("```"):
            flush()
            parts.append("<pre>" if not in_code else "</pre>")
            in_code = not in_code
        elif in_code:
            parts.append(html.escape(line))
        elif line.strip().startswith("- "):
            flush()
            parts.append(f"<p>• {md_inline(line.strip()[2:])}</p>")
        elif not line.strip():
            flush()
        else:
            paragraph.append(line.strip())
    flush()
    return "\n".join(parts)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    toc_lines, section_lines = [], []
    for section, repo, accent in SOURCES:
        md_path = root / repo / "docs/concepts.md"
        if not md_path.exists():
            print(f"missing {md_path}, skipping")
            continue
        repo_url = f"https://github.com/ChaoYue0307/{repo}"
        section_lines.append(f'  <h2 class="section" style="--accent:{accent}">{html.escape(section)}</h2>')
        section_lines.append(f'  <p class="source">from <a href="{repo_url}">{repo}</a></p>')
        for title, body in parse_concepts(md_path):
            anchor = slugify(f"{section}-{title}")
            toc_lines.append(f'    <a href="#{anchor}">{html.escape(title)}</a>')
            section_lines.append(f'  <div class="card" id="{anchor}"><h3>{html.escape(title)}</h3>{body_to_html(body)}</div>')
    out = root / "egocentric-vision-learning-hub/docs/glossary.html"
    out.write_text(PAGE.format(toc="\n".join(toc_lines), sections="\n".join(section_lines)), encoding="utf-8")
    print(f"wrote {out} with {len(toc_lines)} concepts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
