"""Dependency-free checks for this GitHub Pages site; never follows external links."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.errors = []
        self.scripts = []
        self.script = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        for name in ("src", "href", "poster"):
            if attrs.get(name):
                self.references.append(attrs[name])
        if tag == "img" and "alt" not in attrs:
            self.errors.append(f"line {self.getpos()[0]}: image missing alt attribute")
        if tag == "script" and not attrs.get("src") and attrs.get("type", "").lower() not in ("application/json", "application/ld+json"):
            self.script = []

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.script is not None:
            self.scripts.append("".join(self.script))
            self.script = None


def local_reference(root, source, reference):
    url = urlsplit(reference)
    if url.scheme or url.netloc or not url.path:
        return None
    target = (root / unquote(url.path).lstrip("/") if url.path.startswith("/") else source.parent / unquote(url.path)).resolve()
    if not target.is_relative_to(root):
        return f"local reference escapes site: {reference}"
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return f"missing local target: {reference}"
    return None


def syntax(code):
    result = subprocess.run(["node", "--check", "--input-type=module"], input=code, capture_output=True, text=True, timeout=15)
    return "JavaScript syntax error" if result.returncode else None


def validate(root):
    root = Path(root).resolve()
    errors = []
    for source in sorted(root.rglob("*")):
        if not source.is_file() or any(part in (".git", "scripts", "tests") for part in source.relative_to(root).parts):
            continue
        references = []
        issues = []
        if source.suffix == ".html":
            page = Page()
            page.feed(source.read_text())
            references = page.references
            issues.extend(page.errors)
            issues.extend(error for code in page.scripts if (error := syntax(code)))
        elif source.suffix == ".webmanifest":
            try:
                manifest = json.loads(source.read_text())
                references = [manifest[k] for k in ("start_url",) if k in manifest]
                references += [icon["src"] for icon in manifest.get("icons", [])]
            except (ValueError, KeyError, TypeError) as exc:
                issues.append(f"invalid manifest: {exc}")
        elif source.suffix == ".js":
            code = source.read_text()
            if error := syntax(code):
                issues.append(error)
            # Check literal precache lists used by the existing Relay worker.
            match = re.search(r"\bASSETS\s*=\s*(\[[^;]*\])", code)
            if match:
                try:
                    references = json.loads(match.group(1))
                except ValueError:
                    issues.append("precache ASSETS must be a JSON array")
        elif source.suffix == ".css":
            references = [value.strip(" \"'") for value in re.findall(r"url\(([^)]+)\)", source.read_text())]
        issues.extend(error for ref in references if (error := local_reference(root, source, ref)))
        errors.extend(f"{source.relative_to(root)}: {issue}" for issue in issues)
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1])
    errors = validate(parser.parse_args().root)
    print("\n".join(errors) if errors else "Static checks passed: local references, manifests, image alt text and JavaScript syntax.")
    raise SystemExit(bool(errors))
