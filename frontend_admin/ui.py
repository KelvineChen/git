from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared_ui import (  # noqa: E402,F401
    inject_theme,
    render_brand_lockup,
    render_empty_state,
    render_metric_tile,
    render_page_intro,
    render_score_ring,
    render_status_badge,
)
from shared_ui.feedback import render_request_error  # noqa: E402,F401
