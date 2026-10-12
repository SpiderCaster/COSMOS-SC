"""Template library.

Two stores, and they do not mix.

* Vault — private OceanWP and GeneratePress frames and their photos.
  Never copied into the SpiderCaster package. One vendor frame per site.
  A frame already live on one site cannot go live on a second site.
* Molds — templates SpiderCaster made: scratch, a mutation, or a mix.
  These are the only templates the package ships.

A mutation of a vendor frame must change palette, type-lead, and nav.
Mix cites two or more parents and is not an as-is vendor frame.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SCHEMA = "spidercaster-library/2"
ORIGINS = ("scratch", "mutate", "mix")
TYPE_LEADS = ("serif", "sans", "slab", "mono-display")
NAVS = ("segmented", "top-bar", "sidebar", "one-page", "footer-only")
HEX = re.compile(r"^#[0-9a-f]{6}$")


class LibraryError(Exception):
    pass


def _read(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _slug(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    if not out:
        raise LibraryError("empty id")
    return out[:48]


def _sha_bound_dir(dest: Path) -> dict[str, str]:
    """sha256 of the release artifact: HTML + assets + site.json.

    Mirrors lib.hands._sha_bound (crew-ticket.json excluded, since a
    ticket cannot hash itself). A byte change in any bound file
    invalidates sign-off: re-run the crew.
    """
    bound: dict[str, str] = {}
    if not dest.is_dir():
        return bound
    for path in sorted(dest.rglob("*")):
        if not path.is_file() or path.name == "crew-ticket.json":
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
        key = str(path.relative_to(dest)).replace("\\", "/")
        bound[key] = digest
    return bound


def _ticket_visual_status(ticket: dict) -> str | None:
    """Visual-critic status across both ticket hands shapes.

    Crew tickets carry {"role": "visual"} rows; direct-hands tickets
    carry {"hand": "check_site"} rows. Either form counts.
    """
    hands = ticket.get("hands")
    if not isinstance(hands, list):
        return None
    for row in hands:
        if isinstance(row, dict) and row.get("role") == "visual":
            status = row.get("status")
            return str(status) if status else None
    for row in hands:
        if isinstance(row, dict) and row.get("hand") == "check_site":
            status = row.get("status")
            return str(status) if status else None
    return None


def verify_live_ticket(site_dir: Path, site: str, mold_id: str) -> dict:
    """Recompute hashes and refuse a stale or forged ticket.

    Fail-closed publish gate (round2 3.7/3.9): missing/unreadable
    ticket, site/mold mismatch, "ok" not true, visual not PASS, empty
    hash map, or any recomputed hash difference raises LibraryError.
    Returns the ticket plus recomputed hashes and ticket path.
    """
    dest = Path(site_dir)
    path = dest / "crew-ticket.json"
    if not path.is_file():
        raise LibraryError(f"bad ticket: {path} missing; re-run the crew")
    try:
        ticket = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LibraryError(f"bad ticket: {path} unreadable") from exc
    if not isinstance(ticket, dict):
        raise LibraryError(f"bad ticket: {path} is not an object")
    if ticket.get("site") != site:
        raise LibraryError(
            f"ticket site {ticket.get('site')!r} != {site!r}"
        )
    if ticket.get("mold") != mold_id:
        raise LibraryError(
            f"ticket mold {ticket.get('mold')!r} != {mold_id!r}"
        )
    if ticket.get("ok") is not True:
        raise LibraryError('ticket "ok" is not true; re-run the crew')
    visual = _ticket_visual_status(ticket)
    if visual != "PASS":
        raise LibraryError(f"visual is not PASS ({visual}); re-run the crew")
    recorded = ticket.get("sha256")
    if recorded is None:
        recorded = ticket.get("hashes")
    if not isinstance(recorded, dict) or not recorded:
        raise LibraryError("bad ticket: no sha256/hashes map")
    now = _sha_bound_dir(dest)
    if now != recorded:
        bad = next(
            (
                key
                for key in sorted(set(now) | set(recorded))
                if now.get(key) != recorded.get(key)
            ),
            "artifact",
        )
        raise LibraryError(f"hash mismatch: {bad} changed; re-run the crew")
    return {"ticket": ticket, "sha256": now, "path": path}


class Library:
    def __init__(self, package_root: Path, vault_root: Path):
        self.package_root = Path(package_root)
        self.vault_root = Path(vault_root)
        self.mold_dir = self.package_root / "molds"
        self.ledger_path = self.package_root / "ledger.json"
        self.frames_path = self.vault_root / "frames.json"

    def ledger(self) -> dict:
        data = _read(self.ledger_path, {"schema": SCHEMA, "assignments": []})
        data.setdefault("assignments", [])
        return data

    def frames(self) -> dict:
        data = _read(self.frames_path, {"schema": SCHEMA, "frames": []})
        data.setdefault("frames", [])
        return data

    def save_ledger(self, data: dict) -> None:
        data["schema"] = SCHEMA
        _write(self.ledger_path, data)

    def save_frames(self, data: dict) -> None:
        data["schema"] = SCHEMA
        data["package"] = False
        _write(self.frames_path, data)
        readme = self.vault_root / "README.md"
        if not readme.exists():
            readme.write_text(
                "# Vendor vault\n\n"
                "Private OceanWP and GeneratePress frames and photos.\n"
                "Not part of the SpiderCaster package. Do not copy these\n"
                "files into `library/molds` or into a public snapshot.\n"
                "One frame per site. A frame used live is not used live again.\n",
                encoding="utf-8",
            )

    def mold_path(self, mold_id: str) -> Path:
        return self.mold_dir / f"{_slug(mold_id)}.json"

    def load_mold(self, mold_id: str) -> dict:
        path = self.mold_path(mold_id)
        if not path.exists():
            raise LibraryError(f"no mold {mold_id}")
        mold = json.loads(path.read_text(encoding="utf-8"))
        if mold.get("package") is not True or mold.get("origin") not in ORIGINS:
            raise LibraryError(f"{mold_id} is not a SpiderCaster mold")
        return mold

    def list_molds(self) -> list[dict]:
        if not self.mold_dir.exists():
            return []
        out = []
        for path in sorted(self.mold_dir.glob("*.json")):
            out.append(json.loads(path.read_text(encoding="utf-8")))
        return out

    def frame_by_id(self, frame_id: str) -> dict | None:
        for frame in self.frames().get("frames", []):
            if frame.get("id") == frame_id:
                return frame
        return None

    def index_catalogs(self, owp_catalog: Path, gp_catalog: Path, owp_frames: Path | None = None) -> dict:
        """Register catalog names. Does not download theme files or photos."""
        found: dict[str, dict] = {}

        def add(vendor: str, slug: str, **extra) -> None:
            slug = _slug(slug)
            fid = f"{vendor}:{slug}"
            row = {
                "id": fid,
                "vendor": vendor,
                "slug": slug,
                "package": False,
                "photos": "not-pulled",
                "snapshot": None,
            }
            row.update(extra)
            found[fid] = row

        if owp_catalog.exists():
            cat = json.loads(owp_catalog.read_text(encoding="utf-8"))
            for key in ("core_frame_slugs", "hubspot_slugs", "gutenberg_slugs"):
                for slug in cat.get(key) or []:
                    add("owp", slug, catalog=key, claimed_total=cat.get("total_demo_count"))
        if owp_frames and owp_frames.exists():
            for manifest in owp_frames.glob("*/manifest.json"):
                data = json.loads(manifest.read_text(encoding="utf-8"))
                slug = data.get("slug") or manifest.parent.name
                add("owp", slug, name=data.get("name"), sections=data.get("key_sections") or [],
                    catalog="core-frames")
                for var in data.get("variations") or []:
                    add("owp", var, parent=f"owp:{_slug(slug)}", catalog="variation")
        if gp_catalog.exists():
            cat = json.loads(gp_catalog.read_text(encoding="utf-8"))
            for row in cat.get("confirmed_starter_sites") or []:
                add("gp", row.get("name") or "", name=row.get("name"),
                    category=row.get("category"), editor=row.get("editor"),
                    claimed_total=cat.get("total_sites"))

        store = self.frames()
        by_id = {f["id"]: f for f in store["frames"] if f.get("id")}
        for fid, row in found.items():
            prev = by_id.get(fid)
            if prev and prev.get("snapshot"):
                row["snapshot"] = prev["snapshot"]
                row["photos"] = prev.get("photos") or row["photos"]
            by_id[fid] = row
        store["frames"] = sorted(by_id.values(), key=lambda f: f["id"])
        store["note"] = (
            "Names only. Theme files and photos stay out until a snapshot "
            "is accepted into this vault. The package does not ship these rows."
        )
        self.save_frames(store)
        return {"frames": len(store["frames"]), "vault": str(self.vault_root)}

    def accept_snapshot(self, frame_id: str, snapshot: Path) -> dict:
        """Record a pulled demo directory. The directory must sit inside the vault."""
        snapshot = Path(snapshot).resolve()
        vault = self.vault_root.resolve()
        if vault not in snapshot.parents and snapshot != vault:
            raise LibraryError("snapshot must live inside the vendor vault")
        if not snapshot.is_dir():
            raise LibraryError(f"snapshot dir missing: {snapshot}")
        frame = self.frame_by_id(frame_id)
        if frame is None:
            raise LibraryError(f"unknown frame {frame_id}")
        photos = [p.name for p in snapshot.rglob("*")
                  if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}]
        frame["snapshot"] = str(snapshot)
        frame["photos"] = f"{len(photos)} file(s) in vault"
        frame["package"] = False
        store = self.frames()
        store["frames"] = [frame if f.get("id") == frame_id else f for f in store["frames"]]
        self.save_frames(store)
        return {"id": frame_id, "photos": len(photos), "snapshot": str(snapshot)}

    def save_mold(self, mold: dict) -> dict:
        origin = mold.get("origin")
        if origin not in ORIGINS:
            raise LibraryError(f"origin must be one of {ORIGINS}")
        mold_id = _slug(mold.get("id"))
        palette = str(mold.get("palette") or "").lower()
        type_lead = mold.get("type_lead")
        nav = mold.get("nav")
        if not HEX.fullmatch(palette):
            raise LibraryError("palette must be a #rrggbb accent")
        if type_lead not in TYPE_LEADS:
            raise LibraryError(f"type_lead must be one of {TYPE_LEADS}")
        if nav not in NAVS:
            raise LibraryError(f"nav must be one of {NAVS}")
        parents = [str(p) for p in (mold.get("parents") or [])]
        if origin == "scratch" and parents:
            raise LibraryError("a scratch mold has no vendor parent")
        if origin == "mutate" and len(parents) != 1:
            raise LibraryError("a mutation cites exactly one parent")
        if origin == "mix" and len(parents) < 2:
            raise LibraryError("a mix cites two or more parents")
        for parent in parents:
            if parent.startswith(("owp:", "gp:")) and self.frame_by_id(parent) is None:
                raise LibraryError(f"unknown parent frame {parent}")
        if origin == "mutate" and not parents[0].startswith(("owp:", "gp:")):
            parent_mold = self.load_mold(parents[0])
            if parent_mold.get("palette") == palette \
                    and parent_mold.get("type_lead") == type_lead \
                    and parent_mold.get("nav") == nav:
                raise LibraryError("mutation must change palette, type-lead, and nav")
        for existing in self.list_molds():
            if existing.get("id") == mold_id:
                continue
            if existing.get("parents") == parents \
                    and existing.get("palette") == palette \
                    and existing.get("type_lead") == type_lead \
                    and existing.get("nav") == nav:
                raise LibraryError(
                    f"same palette, type-lead, and nav as mold {existing['id']}"
                )
        row = {
            "id": mold_id,
            "origin": origin,
            "parents": parents,
            "palette": palette,
            "type_lead": type_lead,
            "nav": nav,
            "template": mold.get("template") if mold.get("template") in ("modern", "editorial", "bold") else "editorial",
            "sections": list(mold.get("sections") or []),
            "package": True,
            "note": str(mold.get("note") or ""),
        }
        _write(self.mold_path(mold_id), row)
        return row

    def _live_owner(self, key: str, value: str, site: str) -> str | None:
        for row in self.ledger().get("assignments", []):
            if row.get("live") and row.get(key) == value and row.get("site") != site:
                return row.get("site")
        return None

    def live_conflict(self, mold_id: str, site: str) -> str | None:
        return self._live_owner("mold", mold_id, site)

    def bind(
        self,
        site: str,
        mold_id: str,
        vendor_frame: str | None = None,
        live: bool = False,
        site_dir: Path | str | None = None,
    ) -> dict:
        """Attach one mold to a site. At most one vendor frame. Live use is exclusive.

        When live=True and site_dir is given, the crew ticket in that dir is
        verified first: bad ticket, site/mold mismatch, ok not true, visual
        not PASS, or any hash mismatch refuses before the mold-collision
        check. Direct calls without site_dir keep the legacy
        collision-only gate (selftests, drafts).
        """
        site = _slug(site) if "." not in site else str(site).strip().lower()
        mold = self.load_mold(mold_id)
        if vendor_frame:
            if self.frame_by_id(vendor_frame) is None:
                raise LibraryError(f"unknown vendor frame {vendor_frame}")
            if mold.get("origin") == "mix":
                raise LibraryError("a mix is not an as-is vendor frame")
            if mold.get("origin") == "scratch":
                raise LibraryError("a scratch mold does not wear a vendor frame")
        owner = self._live_owner("mold", mold["id"], site)
        bound_hashes: dict[str, str] = {}
        ticket_hash = ""
        if live and site_dir is not None:
            checked = verify_live_ticket(Path(site_dir), site, mold["id"])
            bound_hashes = checked["sha256"]
            ticket_path = checked["path"]
            try:
                ticket_hash = hashlib.sha256(
                    ticket_path.read_bytes()
                ).hexdigest()
            except OSError:
                ticket_hash = ""
        if live and owner:
            raise LibraryError(f"mold {mold['id']} is already live on {owner}")
        if live and vendor_frame:
            frame_owner = self._live_owner("vendor_frame", vendor_frame, site)
            if frame_owner:
                raise LibraryError(
                    f"frame {vendor_frame} is already live on {frame_owner}"
                )
        data = self.ledger()
        kept = [r for r in data["assignments"] if r.get("site") != site]
        row = {
            "site": site,
            "mold": mold["id"],
            "vendor_frame": vendor_frame,
            "live": bool(live),
        }
        if live and site_dir is not None:
            row["sha256"] = bound_hashes
            row["ticket_sha256"] = ticket_hash
        kept.append(row)
        data["assignments"] = kept
        self.save_ledger(data)
        return row

    def package_manifest(self) -> dict:
        """What the package may ship. Vendor rows are refused."""
        molds = []
        for mold in self.list_molds():
            if mold.get("package") is not True:
                raise LibraryError(f"mold {mold.get('id')} is not package-safe")
            if mold.get("origin") not in ORIGINS:
                raise LibraryError(f"mold {mold.get('id')} has a vendor origin")
            molds.append({"id": mold["id"], "origin": mold["origin"], "nav": mold["nav"],
                          "type_lead": mold["type_lead"], "palette": mold["palette"]})
        return {"schema": SCHEMA, "molds": molds, "vendor_frames": 0}


def selftest(root: Path) -> int:
    """Rules a second live use, a second vendor frame, and a vendor export must fail."""
    pkg = root / "pkg"
    vault = root / "vault"
    lib = Library(pkg, vault)
    lib.save_frames({"frames": [
        {"id": "owp:restaurant", "vendor": "owp", "slug": "restaurant", "package": False,
         "photos": "not-pulled", "snapshot": None},
        {"id": "gp:marketer", "vendor": "gp", "slug": "marketer", "package": False,
         "photos": "not-pulled", "snapshot": None},
    ]})
    made = lib.save_mold({
        "id": "harbor-editorial", "origin": "scratch",
        "palette": "#c8923e", "type_lead": "serif", "nav": "segmented",
        "template": "editorial", "note": "made here",
    })
    assert made["package"] is True
    lib.bind("one.example", "harbor-editorial", live=True)
    try:
        lib.bind("two.example", "harbor-editorial", live=True)
        raise SystemExit("live reuse was allowed")
    except LibraryError:
        pass
    mutated = lib.save_mold({
        "id": "bistro-sans", "origin": "mutate", "parents": ["owp:restaurant"],
        "palette": "#1f6f5b", "type_lead": "sans", "nav": "top-bar",
    })
    lib.bind("bistro.example", mutated["id"], vendor_frame="owp:restaurant", live=True)
    try:
        lib.bind("other.example", mutated["id"], vendor_frame="owp:restaurant", live=True)
        raise SystemExit("vendor frame reused live")
    except LibraryError:
        pass
    try:
        lib.save_mold({
            "id": "same-face", "origin": "mutate", "parents": ["owp:restaurant"],
            "palette": "#1f6f5b", "type_lead": "sans", "nav": "top-bar",
        })
    except LibraryError:
        pass
    mixed = lib.save_mold({
        "id": "mix-faq", "origin": "mix", "parents": ["owp:restaurant", "gp:marketer"],
        "palette": "#5b3a8c", "type_lead": "slab", "nav": "sidebar",
        "sections": ["hero", "faq"],
    })
    try:
        lib.bind("mix.example", mixed["id"], vendor_frame="owp:restaurant", live=False)
        raise SystemExit("mix accepted an as-is vendor frame")
    except LibraryError:
        pass
    manifest = lib.package_manifest()
    assert manifest["vendor_frames"] == 0
    assert all(m["origin"] in ORIGINS for m in manifest["molds"])
    snap = vault / "owp" / "restaurant"
    snap.mkdir(parents=True)
    (snap / "hero.jpg").write_bytes(b"not-a-real-photo")
    accepted = lib.accept_snapshot("owp:restaurant", snap)
    assert accepted["photos"] == 1
    try:
        lib.accept_snapshot("owp:restaurant", pkg)
        raise SystemExit("package dir accepted as a vendor snapshot")
    except LibraryError:
        pass
    live_mold = lib.save_mold({
        "id": "bind-live", "origin": "scratch",
        "palette": "#1f6f5b", "type_lead": "serif", "nav": "segmented",
    })
    site_dir = root / "live-site"
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "index.html").write_text("<html></html>\n", encoding="utf-8")
    (site_dir / "site.json").write_text('{"site": "x"}\n', encoding="utf-8")

    def _write_live_ticket(ok: bool, visual: str) -> None:
        hands = [
            {"role": "visual", "status": visual, "detail": "checker"},
            {"role": "deployer", "status": "PASS", "detail": "ticket"},
        ]
        ticket = {
            "site": "bind-live.example",
            "mold": live_mold["id"],
            "publish": "Keith click. This run does not deploy.",
            "hands": hands,
            "ok": ok,
            "sha256": _sha_bound_dir(site_dir),
        }
        (site_dir / "crew-ticket.json").write_text(
            json.dumps(ticket, indent=2) + "\n", encoding="utf-8"
        )

    _write_live_ticket(True, "PASS")
    row = lib.bind(
        "bind-live.example", live_mold["id"], live=True, site_dir=site_dir
    )
    if not row.get("live") or row.get("sha256") != _sha_bound_dir(site_dir):
        raise SystemExit("verified live bind did not record hashes")
    if not row.get("ticket_sha256"):
        raise SystemExit("verified live bind did not record ticket hash")
    (site_dir / "index.html").write_text("<html>changed</html>\n", encoding="utf-8")
    try:
        lib.bind(
            "bind-live.example", live_mold["id"], live=True, site_dir=site_dir
        )
        raise SystemExit("hash mismatch was allowed")
    except LibraryError as exc:
        if "hash mismatch" not in str(exc):
            raise SystemExit(f"wrong refusal: {exc}")
    (site_dir / "index.html").write_text("<html></html>\n", encoding="utf-8")
    _write_live_ticket(False, "PASS")
    try:
        lib.bind(
            "bind-live.example", live_mold["id"], live=True, site_dir=site_dir
        )
        raise SystemExit("ok:false ticket was allowed")
    except LibraryError as exc:
        if '"ok" is not true' not in str(exc):
            raise SystemExit(f"wrong refusal: {exc}")
    _write_live_ticket(True, "FAIL")
    try:
        lib.bind(
            "bind-live.example", live_mold["id"], live=True, site_dir=site_dir
        )
        raise SystemExit("visual FAIL ticket was allowed")
    except LibraryError as exc:
        if "visual is not PASS" not in str(exc):
            raise SystemExit(f"wrong refusal: {exc}")
    _write_live_ticket(True, "PASS")
    (site_dir / "crew-ticket.json").unlink()
    try:
        lib.bind(
            "bind-live.example", live_mold["id"], live=True, site_dir=site_dir
        )
        raise SystemExit("missing ticket was allowed")
    except LibraryError as exc:
        if "bad ticket" not in str(exc):
            raise SystemExit(f"wrong refusal: {exc}")
    second_dir = root / "live-site-two"
    second_dir.mkdir(parents=True, exist_ok=True)
    (second_dir / "index.html").write_text("<html></html>\n", encoding="utf-8")
    (second_dir / "site.json").write_text('{"site": "y"}\n', encoding="utf-8")
    second_ticket = {
        "site": "bind-live-two.example",
        "mold": live_mold["id"],
        "publish": "Keith click. This run does not deploy.",
        "hands": [
            {"role": "visual", "status": "PASS", "detail": "checker"},
            {"role": "deployer", "status": "PASS", "detail": "ticket"},
        ],
        "ok": True,
        "sha256": _sha_bound_dir(second_dir),
    }
    (second_dir / "crew-ticket.json").write_text(
        json.dumps(second_ticket, indent=2) + "\n", encoding="utf-8"
    )
    try:
        lib.bind(
            "bind-live-two.example",
            live_mold["id"],
            live=True,
            site_dir=second_dir,
        )
        raise SystemExit("live reuse was allowed after verify")
    except LibraryError as exc:
        if "already live" not in str(exc):
            raise SystemExit(f"wrong refusal: {exc}")
    print("library selftest ok")
    return 0
