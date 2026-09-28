"""Copy ingestion: real copy files -> structured blocks.

House rule this module enforces: the engine never invents content. Everything
the site says must come from the project's copy/ files (markdown, txt, json)
plus the brief. External image URLs are dropped (download-only / no hotlink
rails); only local asset paths survive.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}")
PRICE_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
HOTLINK_RE = re.compile(
    r"(?:images\.unsplash\.com|plus\.unsplash\.com|img\.freepik\.com|"
    r"cdn\.pixabay\.com|images\.pexels\.com|static\.freepik\.com)",
    re.I,
)

COPY_EXTS = {".md", ".markdown", ".txt", ".json"}


class Block:
    """One heading-scoped chunk of real copy."""

    def __init__(self, file: str, level: int, title: str):
        self.file = file
        self.level = level
        self.title = title
        self.paragraphs: list[str] = []
        self.bullets: list[str] = []
        self.numbered: list[str] = []
        self.qa: list[dict] = []      # [{"q":..., "a":...}]
        self.prices: list[dict] = []  # [{"name","desc","price"}]
        self.images: list[dict] = []  # [{"src","alt"}]
        self.emails: list[str] = []
        self.phones: list[str] = []

    def to_dict(self) -> dict:
        return {
            "file": self.file, "level": self.level, "title": self.title,
            "paragraphs": self.paragraphs, "bullets": self.bullets,
            "numbered": self.numbered, "qa": self.qa, "prices": self.prices,
            "images": self.images, "emails": self.emails, "phones": self.phones,
        }


class Copy:
    def __init__(self):
        self.brief = ""
        self.blocks: list[Block] = []
        self.warnings: list[str] = []
        self.assets: dict[str, str] = {}  # name -> relative path (local only)

    @property
    def emails(self):
        seen, out = set(), []
        for b in self.blocks:
            for e in b.emails:
                if e.lower() not in seen:
                    seen.add(e.lower())
                    out.append(e)
        return out

    @property
    def phones(self):
        seen, out = set(), []
        for b in self.blocks:
            for p in b.phones:
                if p not in seen:
                    seen.add(p)
                    out.append(p)
        return out

    def text_digest(self, max_chars: int) -> str:
        """Compact plain-text view of all copy, for the LLM prompt."""
        parts = []
        for b in self.blocks:
            head = f"{'#' * max(b.level, 1)} {b.title}" if b.title else "(untitled)"
            lines = [head]
            lines += [p for p in b.paragraphs]
            if b.bullets:
                lines += ["- " + x for x in b.bullets]
            if b.numbered:
                lines += [f"{i + 1}. {x}" for i, x in enumerate(b.numbered)]
            for qa in b.qa:
                lines.append(f"Q: {qa['q']}")
                lines.append(f"A: {qa['a']}")
            for pr in b.prices:
                desc = f" - {pr['desc']}" if pr["desc"] else ""
                price = f" ({pr['price']})" if pr["price"] else ""
                lines.append(f"* {pr['name']}{desc}{price}")
            for im in b.images:
                lines.append(f"[image: {im['alt'] or im['src']}]")
            parts.append("\n".join(lines))
        text = "\n\n".join(parts)
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[copy truncated]"
            self.warnings.append(
                f"copy digest truncated at {max_chars} chars; raise --max-copy-chars for full fidelity")
        return text


# ---------------------------------------------------------------- markdown

MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
MD_EMphasis_RE = re.compile(r"\*\*([^*]+)\*\*|__([^_]+)__")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def strip_md_inline(text: str) -> str:
    text = MD_IMAGE_RE.sub(lambda m: f"[image: {m.group(1) or Path(m.group(2)).stem}]", text)
    text = MD_LINK_RE.sub(lambda m: m.group(1) if m.group(1) else m.group(2), text)
    text = MD_EMphasis_RE.sub(lambda m: m.group(1) or m.group(2) or "", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return text.strip()


def parse_markdown(text: str, file: str) -> list[Block]:
    blocks: list[Block] = []
    cur: Block | None = None
    last_para_was_q = False

    def ensure(level: int, title: str):
        nonlocal cur, last_para_was_q
        cur = Block(file, level, title)
        blocks.append(cur)
        last_para_was_q = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            last_para_was_q = False
            continue
        m = HEADING_RE.match(stripped)
        if m:
            ensure(len(m.group(1)), strip_md_inline(m.group(2)))
            continue
        if stripped.startswith(("- ", "* ", "+ ")):
            if cur is None:
                ensure(1, "")
            item = strip_md_inline(stripped[2:].strip())
            # "Name - $12" or "Name | $12" bullet lines double as price rows.
            pm = re.match(r"(.+?)\s*[|:\u2013\u2014-]\s*(\$\s?\d[\d,.]*)\s*$", item)
            if pm and PRICE_RE.search(pm.group(2)):
                cur.prices.append({"name": pm.group(1).strip(), "desc": "", "price": pm.group(2)})
            else:
                cur.bullets.append(item)
            last_para_was_q = False
            continue
        nm = re.match(r"^(\d+)[.)]\s+(.*)$", stripped)
        if nm:
            if cur is None:
                ensure(1, "")
            cur.numbered.append(strip_md_inline(nm.group(2)))
            last_para_was_q = False
            continue
        if stripped.startswith(">"):
            if cur is None:
                ensure(1, "")
            cur.paragraphs.append(strip_md_inline(stripped.lstrip("> ")))
            continue
        # plain paragraph line
        if cur is None:
            ensure(1, "")
        para = strip_md_inline(stripped)
        if last_para_was_q and cur.qa:
            cur.qa[-1]["a"] = (cur.qa[-1]["a"] + " " + para).strip()
            last_para_was_q = False
            continue
        if para.endswith("?") and len(para) < 200:
            cur.qa.append({"q": para, "a": ""})
            last_para_was_q = True
            continue
        cur.paragraphs.append(para)
        last_para_was_q = False

    # post-pass: images, contact patterns
    for b in blocks:
        b.emails = list(dict.fromkeys(EMAIL_RE.findall(" ".join(b.paragraphs + b.bullets))))
        b.phones = list(dict.fromkeys(PHONE_RE.findall(" ".join(b.paragraphs + b.bullets))))
    return blocks


def parse_json_copy(path: Path, warnings: list[str]) -> list[Block]:
    """JSON copy: either a list of {title, paragraphs|bullets|qa|prices...}
    blocks, or {"blocks": [...]}."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        warnings.append(f"{path.name}: unreadable JSON ({exc})")
        return []
    if isinstance(data, dict) and isinstance(data.get("blocks"), list):
        data = data["blocks"]
    if not isinstance(data, list):
        warnings.append(f"{path.name}: JSON copy must be a list of blocks")
        return []
    blocks = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        b = Block(path.name, int(item.get("level") or 2), str(item.get("title") or f"block-{i + 1}"))
        b.paragraphs = [str(x) for x in item.get("paragraphs", []) if str(x).strip()]
        b.bullets = [str(x) for x in item.get("bullets", []) if str(x).strip()]
        b.numbered = [str(x) for x in item.get("numbered", []) if str(x).strip()]
        b.qa = [{"q": str(x.get("q", "")), "a": str(x.get("a", ""))}
                for x in item.get("qa", []) if isinstance(x, dict) and str(x.get("q", "")).strip()]
        b.prices = [{"name": str(x.get("name", "")), "desc": str(x.get("desc", "")),
                     "price": str(x.get("price", ""))}
                    for x in item.get("prices", []) if isinstance(x, dict) and str(x.get("name", "")).strip()]
        b.images = [{"src": str(x.get("src", "")), "alt": str(x.get("alt", ""))}
                    for x in item.get("images", []) if isinstance(x, dict) and str(x.get("src", "")).strip()]
        b.emails = list(dict.fromkeys(EMAIL_RE.findall(" ".join(b.paragraphs))))
        b.phones = list(dict.fromkeys(PHONE_RE.findall(" ".join(b.paragraphs))))
        blocks.append(b)
    return blocks


def load_project(project_dir: Path, max_assets: int = 24) -> Copy:
    """Load brief.md + copy/* + assets.json from a project directory."""
    c = Copy()
    project_dir = Path(project_dir)
    if not project_dir.exists():
        raise SystemExit(f"project dir not found: {project_dir}")

    for name in ("brief.md", "brief.txt"):
        p = project_dir / name
        if p.exists():
            c.brief = p.read_text(encoding="utf-8", errors="replace").strip()
            break

    copy_dir = project_dir / "copy"
    if copy_dir.exists():
        files = sorted(p for p in copy_dir.iterdir() if p.is_file() and p.suffix.lower() in COPY_EXTS)
        if not files:
            c.warnings.append("copy/ has no .md/.txt/.json files")
        for p in files:
            if p.suffix.lower() == ".json":
                c.blocks.extend(parse_json_copy(p, c.warnings))
            else:
                text = p.read_text(encoding="utf-8", errors="replace")
                c.blocks.extend(parse_markdown(text, p.name))
    else:
        c.warnings.append("no copy/ directory; site will be structure only")

    # assets.json: {"images": {"name": "relative/path.jpg"}} - local files only
    assets_path = project_dir / "assets.json"
    if assets_path.exists():
        try:
            data = json.loads(assets_path.read_text(encoding="utf-8"))
            for name, rel in (data.get("images") or {}).items():
                rel = str(rel)
                if rel.startswith(("http://", "https://")):
                    c.warnings.append(f"assets.json: dropped external image '{name}' (download-only rule)")
                    continue
                if HOTLINK_RE.search(rel):
                    c.warnings.append(f"assets.json: dropped hotlinked image '{name}'")
                    continue
                if not (project_dir / rel).exists():
                    c.warnings.append(f"assets.json: '{name}' -> {rel} not found on disk; skipped")
                    continue
                if len(c.assets) >= max_assets:
                    c.warnings.append(f"assets.json: more than {max_assets} images; rest ignored")
                    break
                c.assets[str(name)] = rel
        except (OSError, ValueError) as exc:
            c.warnings.append(f"assets.json unreadable ({exc})")

    # markdown images referencing local files get wired to assets
    if c.assets:
        for b in c.blocks:
            for para in list(b.paragraphs):
                m = MD_IMAGE_RE.search(para)
                if m:
                    key = Path(m.group(2)).stem
                    if key in c.assets:
                        b.images.append({"src": c.assets[key], "alt": m.group(1) or key})
                        b.paragraphs.remove(para)
    return c
