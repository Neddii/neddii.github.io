# Development and updates

Review focused changes in PRs; retain external attribution. Use appropriate project-specific build/tests where configured; do not claim successful deployment from source changes alone.

Historical static website, not a private systems dashboard.

Run `python3 scripts/validate_static.py` and `python3 -m unittest discover -s tests` with Python 3.9+ and Node.js on PATH. No dependencies are installed. These checks inspect local HTML/CSS/manifest/precache references, image alt attributes and inline/external JavaScript syntax without executing browser actions or following remote/deep links. They are bounded validation, not comprehensive HTML conformance or browser/mobile testing. GitHub Actions runs the same commands for PRs and main. GitHub Pages deployment and live content verification remain separate.
