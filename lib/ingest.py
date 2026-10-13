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
    re.IGNORECASE,
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
    """Join consecutive plain lines into one paragraph.

    A blank line starts a new paragraph. Bullets, numbered lines, headings,
    and blockquotes are not folded into that paragraph. A question line is
    still a question; following plain lines join into its answer until a
    blank line, the next question, or a non-plain line.

    An indented line that is not a new list marker, heading, or blank line
    continues the previous bullet or numbered item, joined with one space.
    A blank line ends that item. Continuation lines are not a paragraph.
    """
    blocks: list[Block] = []
    cur: Block | None = None
    expect_answer = False
    pending: list[str] = []
    pending_answer = False
    # ("bullet"|"numbered"|"price", index) until a blank line or a new block.
    open_item: tuple[str, int] | None = None

    def ensure(level: int, title: str):
        nonlocal cur, expect_answer
        cur = Block(file, level, title)
        blocks.append(cur)
        expect_answer = False

    def close_item() -> None:
        nonlocal open_item
        open_item = None

    def join_item(prev: str, extra: str) -> str:
        if not prev:
            return extra
        if not extra:
            return prev
        return f"{prev} {extra}"

    def continue_item(extra: str) -> None:
        if open_item is None or cur is None:
            return
        kind, idx = open_item
        if kind == "bullet":
            cur.bullets[idx] = join_item(cur.bullets[idx], extra)
        elif kind == "numbered":
            cur.numbered[idx] = join_item(cur.numbered[idx], extra)
        else:
            cur.prices[idx]["desc"] = join_item(cur.prices[idx]["desc"], extra)

    def flush() -> None:
        nonlocal pending_answer, expect_answer
        close_item()
        if not pending or cur is None:
            pending.clear()
            pending_answer = False
            return
        joined = " ".join(pending)
        pending.clear()
        if pending_answer and cur.qa:
            cur.qa[-1]["a"] = (cur.qa[-1]["a"] + " " + joined).strip()
            expect_answer = False
        else:
            cur.paragraphs.append(joined)
        pending_answer = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush()
            expect_answer = False
            continue
        m = HEADING_RE.match(stripped)
        if m:
            flush()
            ensure(len(m.group(1)), strip_md_inline(m.group(2)))
            continue
        is_bullet = stripped.startswith(("- ", "* ", "+ "))
        numbered = re.match(r"^(\d+)[.)]\s+(.*)$", stripped)
        indented = line[:1] in (" ", "\t")
        # Soft wrap of the open bullet or numbered item. Not a new paragraph.
        if indented and open_item is not None and not is_bullet and numbered is None:
            extra = strip_md_inline(stripped)
            if extra:
                continue_item(extra)
            continue
        if is_bullet:
            flush()
            if cur is None:
                ensure(1, "")
            item = strip_md_inline(stripped[2:].strip())
            # "Name - $12" or "Name | $12" bullet lines double as price rows.
            pm = re.match(r"(.+?)\s*[|:\u2013\u2014-]\s*(\$\s?\d[\d,.]*)\s*$", item)
            if pm and PRICE_RE.search(pm.group(2)):
                cur.prices.append({"name": pm.group(1).strip(), "desc": "", "price": pm.group(2)})
                open_item = ("price", len(cur.prices) - 1)
            else:
                cur.bullets.append(item)
                open_item = ("bullet", len(cur.bullets) - 1)
            expect_answer = False
            continue
        if numbered:
            flush()
            if cur is None:
                ensure(1, "")
            cur.numbered.append(strip_md_inline(numbered.group(2)))
            open_item = ("numbered", len(cur.numbered) - 1)
            expect_answer = False
            continue
        if stripped.startswith(">"):
            flush()
            if cur is None:
                ensure(1, "")
            cur.paragraphs.append(strip_md_inline(stripped.lstrip("> ")))
            continue
        close_item()
        if cur is None:
            ensure(1, "")

        # Check for markdown image tags in this line
        img_matches = list(MD_IMAGE_RE.finditer(stripped))
        if img_matches:
            for m in img_matches:
                cur.images.append({"src": m.group(2).strip(), "alt": (m.group(1) or Path(m.group(2)).stem).strip()})
            if not MD_IMAGE_RE.sub("", stripped).strip():
                # Line was purely an image reference
                continue

        para = strip_md_inline(stripped)
        if not para:
            continue
        # The first plain line after a question is the answer, even if it
        # itself ends with "?". Later "?" lines start the next question.
        if expect_answer and cur.qa and not pending_answer:
            pending.append(para)
            pending_answer = True
            expect_answer = False
            continue
        if para.endswith("?") and len(para) < 200:
            flush()
            cur.qa.append({"q": para, "a": ""})
            expect_answer = True
            continue
        pending.append(para)

    flush()

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

    # Auto-discover project assets/ directory if it exists
    assets_dir = project_dir / "assets"
    if assets_dir.is_dir():
        for p in sorted(assets_dir.iterdir()):
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}:
                rel = f"assets/{p.name}"
                stem = p.stem.lower()
                if stem not in c.assets and len(c.assets) < max_assets:
                    c.assets[stem] = rel

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

    # Wire and validate block images against local assets
    for b in c.blocks:
        resolved = []
        for im in b.images:
            src = im.get("src", "")
            if src.startswith(("http://", "https://")):
                c.warnings.append(f"{b.file}: dropped external image '{src}' (download-only rule)")
                continue
            if HOTLINK_RE.search(src):
                c.warnings.append(f"{b.file}: dropped hotlinked image '{src}'")
                continue
            stem = Path(src).stem.lower()
            if src in c.assets.values():
                resolved.append(im)
            elif stem in c.assets:
                resolved.append({"src": c.assets[stem], "alt": im.get("alt") or stem})
            elif (project_dir / src).is_file():
                resolved.append(im)
                if stem not in c.assets and len(c.assets) < max_assets:
                    c.assets[stem] = src
            else:
                c.warnings.append(f"{b.file}: image '{src}' not found on disk; skipped")
        b.images = resolved
        b.paragraphs = [
            p for p in b.paragraphs
            if not (p.startswith("[image: ") and p.endswith("]"))
        ]
    return c


def _selftest() -> int:
    wrapped = "\n".join([
        "# Title",
        "",
        "You give it a brief and",
        "real copy files.",
        "",
        "Second paragraph",
        "continues here.",
        "",
        "- bullet one",
        "kept apart",
        "from the bullet",
        "1. numbered item",
        "> quoted line",
        "after quote",
        "",
        "Is this a question?",
        "Yes. The answer wraps",
        "onto the next line.",
        "",
        "What about a second?",
        "It stays separate.",
    ])
    block = parse_markdown(wrapped, "overview.md")[0]
    assert block.paragraphs[0] == "You give it a brief and real copy files."
    assert block.paragraphs[1] == "Second paragraph continues here."
    assert block.bullets == ["bullet one"]
    assert "kept apart from the bullet" in block.paragraphs
    assert "bullet one kept apart" not in " ".join(block.paragraphs)
    assert block.numbered == ["numbered item"]
    assert "quoted line" in block.paragraphs
    assert "after quote" in block.paragraphs
    assert "quoted line after quote" not in block.paragraphs
    assert block.qa[0]["q"] == "Is this a question?"
    assert block.qa[0]["a"] == "Yes. The answer wraps onto the next line."
    assert block.qa[1]["q"] == "What about a second?"
    assert block.qa[1]["a"] == "It stays separate."
    split = parse_markdown("# One\n\nAlpha\nbeta.\n\n## Two\n\nGamma\ndelta.\n", "t.md")
    assert split[0].paragraphs == ["Alpha beta."]
    assert split[1].title == "Two"
    assert split[1].paragraphs == ["Gamma delta."]
    quotes = parse_markdown("Before\nthe quote.\n> First quote\n> Second quote\nAfter\nthe quote.\n", "q.md")
    assert quotes[0].paragraphs == [
        "Before the quote.",
        "First quote",
        "Second quote",
        "After the quote.",
    ]
    soft = parse_markdown(
        "- One-call AI builds: a single compact planning call produces the whole site\n"
        "  shape, with at most one JSON-repair retry.\n",
        "overview.md",
    )[0]
    assert len(soft.bullets) == 1
    assert "whole site" in soft.bullets[0] and "JSON-repair" in soft.bullets[0]
    assert soft.paragraphs == []
    numbered_wrap = parse_markdown(
        "1. Step one goes\n  onto the next line.\n\n  after a blank\n",
        "commands.md",
    )[0]
    assert numbered_wrap.numbered == ["Step one goes onto the next line."]
    assert numbered_wrap.paragraphs == ["after a blank"]
    print("ingest selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
