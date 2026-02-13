"""
Web interface for the Always-On AI Assistant documentation and status.
Serves USER_GUIDE.md as a rendered HTML page with navigation.
"""

import os
import re
import markdown
from flask import Flask, render_template, jsonify
from markupsafe import Markup

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_markdown(filename):
    """Load and convert a markdown file to HTML."""
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        return "", []

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract TOC entries from markdown headings
    toc = []
    for match in re.finditer(r"^(#{1,3})\s+(.+)$", text, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[\s]+", "-", slug).strip("-")
        toc.append({"level": level, "title": title, "slug": slug})

    # Convert markdown to HTML with extensions
    html = markdown.markdown(
        text,
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "attr_list",
            "md_in_html",
        ],
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": False},
            "toc": {"permalink": True, "permalink_class": "anchor-link"},
        },
    )

    return html, toc


def load_config():
    """Load assistant config for status display."""
    config_path = os.path.join(BASE_DIR, "assistant_config.yml")
    if not os.path.exists(config_path):
        return {}
    try:
        import yaml

        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return {}


@app.route("/")
def index():
    """Main documentation page."""
    guide_html, toc = load_markdown("USER_GUIDE.md")
    readme_html, _ = load_markdown("README.md")
    config = load_config()
    return render_template(
        "index.html",
        guide_html=Markup(guide_html),
        readme_html=Markup(readme_html),
        toc=toc,
        config=config,
    )


@app.route("/api/status")
def status():
    """API endpoint returning assistant status."""
    config = load_config()
    return jsonify(
        {
            "status": "running",
            "config": config,
            "files": {
                "user_guide": os.path.exists(os.path.join(BASE_DIR, "USER_GUIDE.md")),
                "readme": os.path.exists(os.path.join(BASE_DIR, "README.md")),
                "scratchpad": os.path.exists(os.path.join(BASE_DIR, "scratchpad.md")),
                "config": os.path.exists(
                    os.path.join(BASE_DIR, "assistant_config.yml")
                ),
            },
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
