# Website maintenance

This repository owns the public static site and historical Relay pages. Preserve original content and attribution. Private architecture belongs in Systems Hub, tasks in ClickUp and asynchronous coordination in the canonical Chat Queue.

Use a branch/worktree and focused PR. Run `python3 scripts/validate_static.py`, `python3 -m unittest discover -s tests` and review the diff. Validation checks local references, manifests, image alternative text and JavaScript syntax; it does not prove remote links, mobile deep links or deployment.

Never copy private repositories, credentials, runtime data or internal dashboards into this public site. Do not execute Apple Shortcut/Home Assistant deep links during static validation. Retain existing assets and historical release context. GitHub Pages deployment and live HTTP/content verification require separate evidence. Revert the scoped commit for rollback.
