"""Shared visual system for the user and administrator applications."""

from .components import (
    render_brand_lockup,
    render_dimension_bars,
    render_empty_state,
    render_metric_tile,
    render_page_intro,
    render_score_ring,
    render_skeleton,
    render_status_badge,
)
from .theme import inject_theme
from .feedback import render_request_error

__all__ = [
    "inject_theme",
    "render_brand_lockup",
    "render_dimension_bars",
    "render_empty_state",
    "render_metric_tile",
    "render_page_intro",
    "render_score_ring",
    "render_skeleton",
    "render_status_badge",
    "render_request_error",
]
