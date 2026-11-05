"""Build one PDF from all course Markdown files.

Usage:  pip install markdown pygments
        python scripts/build_pdf.py
Needs Google Chrome or Microsoft Edge installed (used in headless mode to print the PDF).
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = ROOT / "build" / "ai-ml-interview-prep.html"
OUT_PDF = ROOT / "AI-ML-Interview-Prep.pdf"
TITLE = "AI / ML / DL / NLP Interview Prep — Zero to Hero"


def slugify(value, separator="-"):
    """GitHub-style heading anchors, so links written for GitHub also work in the PDF."""
    value = value.strip().lower()
    value = re.sub(r"[^\w\- ]", "", value, flags=re.UNICODE)
    return value.replace(" ", separator)


def course_files():
    files = sorted(p for p in ROOT.glob("[0-9][0-9]-*.md"))
    return [ROOT / "README.md"] + files


def file_key(path):
    return "readme" if path.name == "README.md" else "f" + path.name[:2]


def convert(path, names):
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "codehilite", "toc", "sane_lists"],
        extension_configs={
            "toc": {"slugify": slugify},
            "codehilite": {"guess_lang": False, "css_class": "hl"},
        },
    )
    body = md.convert(path.read_text(encoding="utf-8"))
    key = file_key(path)

    # Prefix every id so anchors from different files don't collide.
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{key}-{m.group(1)}"', body)

    def fix_href(m):
        href = html.unescape(m.group(1))
        if href.startswith(("http://", "https://", "mailto:")):
            return m.group(0)
        if href.startswith("#"):
            return f'href="#{key}-{href[1:]}"'
        target, _, anchor = href.partition("#")
        if target in names:
            tkey = names[target]
            return f'href="#{tkey}-{anchor}"' if anchor else f'href="#{tkey}"'
        return m.group(0)

    body = re.sub(r'href="([^"]+)"', fix_href, body)
    return f'<section class="chapter" id="{key}">\n{body}\n</section>'


def build_html():
    files = course_files()
    names = {p.name: file_key(p) for p in files}
    chapters = "\n".join(convert(p, names) for p in files)

    toc_items = []
    for p in files[1:]:
        first = next((l for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), p.stem)
        toc_items.append(f'<li><a href="#{file_key(p)}">{html.escape(first[2:].strip())}</a></li>')

    pyg_css = HtmlFormatter(style="friendly").get_style_defs(".hl")
    css = """
    @page { size: A4; margin: 18mm 16mm 18mm 16mm; }
    body { font-family: "Segoe UI", Calibri, Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1d2430; }
    h1 { font-size: 22pt; color: #1f3d7a; border-bottom: 2px solid #1f3d7a; padding-bottom: 4px; margin-top: 0; }
    h2 { font-size: 15pt; color: #1f3d7a; margin-top: 22px; border-bottom: 1px solid #d5dbe6; padding-bottom: 2px; }
    h3 { font-size: 12pt; color: #24324a; margin-top: 16px; }
    h2, h3 { break-after: avoid; }
    a { color: #2456c4; text-decoration: none; }
    table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.5pt; break-inside: auto; }
    tr { break-inside: avoid; }
    th, td { border: 1px solid #cfd6e2; padding: 4px 6px; text-align: left; vertical-align: top; }
    th { background: #eef2f9; }
    code { font-family: Consolas, "Courier New", monospace; font-size: 9pt; background: #f2f4f8; padding: 0 3px; border-radius: 3px; }
    pre, .hl pre { font-family: Consolas, "Courier New", monospace; font-size: 8.5pt; line-height: 1.35;
          background: #f6f8fb; border: 1px solid #dde3ec; border-radius: 4px; padding: 8px 10px;
          white-space: pre-wrap; word-break: break-word; }
    pre code { background: none; padding: 0; }
    blockquote { margin: 8px 0; padding: 6px 12px; border-left: 4px solid #2456c4; background: #f1f5fd; }
    .chapter { break-before: page; }
    .cover { text-align: center; padding-top: 70mm; }
    .cover h1 { border: none; font-size: 28pt; }
    .cover p { font-size: 12pt; color: #4a5568; }
    .toc { break-before: page; }
    .toc li { font-size: 12pt; margin: 6px 0; }
    """ + pyg_css

    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{TITLE}</title>
<style>{css}</style></head><body>
<div class="cover"><h1>{TITLE}</h1>
<p>System design · ML · Deep learning · NLP &amp; LLMs · Computer vision · Statistics · Coding · MLOps · Behavioral</p>
<p>With "what if this happens?" scenario answers for every topic</p></div>
<div class="toc"><h1>Contents</h1><ol>{''.join(toc_items)}</ol></div>
{chapters}
</body></html>"""


def find_browser():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        if shutil.which(name):
            return shutil.which(name)
    sys.exit("Chrome/Edge not found. Open build/ai-ml-interview-prep.html in a browser and print to PDF.")


def main():
    OUT_HTML.parent.mkdir(exist_ok=True)
    OUT_HTML.write_text(build_html(), encoding="utf-8")
    browser = find_browser()
    subprocess.run([
        browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri(),
    ], check=True, capture_output=True)
    print(f"PDF written: {OUT_PDF}")


if __name__ == "__main__":
    main()
