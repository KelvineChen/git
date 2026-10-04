from __future__ import annotations

from html import escape
from typing import Iterable

import streamlit as st


ACCENTS = {
    "blue": "#2563EB",
    "cyan": "#0891B2",
    "violet": "#7C3AED",
    "green": "#059669",
    "amber": "#D97706",
    "red": "#DC2626",
    "slate": "#64748B",
}


def _safe(value: object) -> str:
    return escape("" if value is None else str(value))


def _accent(name: str) -> str:
    return ACCENTS.get(name, ACCENTS["blue"])


def render_brand_lockup(
    *,
    compact: bool = False,
    inverse: bool = False,
    subtitle: str = "科研协作匹配平台",
) -> None:
    classes = ["zl-brand-lockup"]
    if compact:
        classes.append("zl-brand-lockup--compact")
    if inverse:
        classes.append("zl-brand-lockup--inverse")
    st.markdown(
        f"""
        <div class="{' '.join(classes)}">
            <div class="zl-brand-mark" aria-hidden="true">
                <span></span><span></span><span></span>
            </div>
            <div>
                <div class="zl-brand-name">知遇 <strong>LinkLab</strong></div>
                <div class="zl-brand-subtitle">{_safe(subtitle)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_intro(
    title: str,
    description: str,
    *,
    eyebrow: str = "知遇 LinkLab",
) -> None:
    st.markdown(
        f"""
        <header class="zl-page-intro">
            <div class="zl-eyebrow">{_safe(eyebrow)}</div>
            <h1>{_safe(title)}</h1>
            <p>{_safe(description)}</p>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_metric_tile(
    label: str,
    value: object,
    *,
    accent: str = "blue",
    icon: str = "analytics",
    caption: str = "",
) -> None:
    color = _accent(accent)
    caption_html = (
        f'<div class="zl-metric-caption">{_safe(caption)}</div>' if caption else ""
    )
    st.markdown(
        f"""
        <div class="zl-metric-tile" style="--tile-accent:{color}">
            <div class="zl-metric-topline"></div>
            <div class="zl-metric-icon material-symbols-rounded" aria-hidden="true">{_safe(icon)}</div>
            <div class="zl-metric-label">{_safe(label)}</div>
            <div class="zl-metric-value">{_safe(value)}</div>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(
    title: str,
    description: str,
    *,
    icon: str = "search_off",
) -> None:
    st.markdown(
        f"""
        <div class="zl-empty-state">
            <span class="material-symbols-rounded" aria-hidden="true">{_safe(icon)}</span>
            <div class="zl-empty-title">{_safe(title)}</div>
            <div class="zl-empty-description">{_safe(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(status: str, label: str | None = None) -> None:
    styles = {
        "recruiting": ("green", "招募中"),
        "full": ("amber", "已满员"),
        "closed": ("slate", "已关闭"),
        "completed": ("blue", "已完成"),
        "mutual": ("green", "双方已匹配"),
        "pending": ("amber", "待处理"),
        "reviewing": ("blue", "处理中"),
        "resolved": ("green", "已处理"),
        "rejected": ("red", "已驳回"),
        "removed": ("red", "已下架"),
        "active": ("green", "正常"),
    }
    accent, default_label = styles.get(status, ("slate", status or "未知"))
    st.markdown(
        f'<span class="zl-status-badge" style="--badge-color:{_accent(accent)}">'
        f'{_safe(label or default_label)}</span>',
        unsafe_allow_html=True,
    )


def render_score_ring(
    score: float,
    *,
    label: str = "综合匹配度",
    size: str = "normal",
) -> None:
    bounded = max(0.0, min(float(score or 0), 1.0))
    percent = round(bounded * 100)
    accent = "green" if bounded >= 0.8 else "blue" if bounded >= 0.6 else "slate"
    st.markdown(
        f"""
        <div class="zl-score-wrap zl-score-wrap--{_safe(size)}">
            <div class="zl-score-ring" style="--score:{percent};--score-color:{_accent(accent)}">
                <div class="zl-score-core"><strong>{percent}%</strong><span>{_safe(label)}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dimension_bars(dimensions: Iterable[tuple[str, float, str]]) -> None:
    rows: list[str] = []
    for label, raw_score, accent in dimensions:
        score = max(0.0, min(float(raw_score or 0), 1.0))
        percent = round(score * 100)
        rows.append(
            f'<div class="zl-dimension-row">'
            f'<div class="zl-dimension-meta"><span>{_safe(label)}</span>'
            f'<strong>{percent}%</strong></div>'
            f'<div class="zl-dimension-track" role="progressbar" aria-label="{_safe(label)}" '
            f'aria-valuenow="{percent}" aria-valuemin="0" aria-valuemax="100">'
            f'<span style="width:{percent}%;--bar-color:{_accent(accent)}"></span>'
            f'</div></div>'
        )
    st.markdown(
        f'<div class="zl-dimension-list">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def render_skeleton(*, rows: int = 3) -> None:
    lines = "".join(
        f'<span class="zl-skeleton-line" style="--line-width:{max(45, 96 - index * 13)}%"></span>'
        for index in range(max(1, rows))
    )
    st.markdown(
        f'<div class="zl-skeleton" aria-label="内容加载中">{lines}</div>',
        unsafe_allow_html=True,
    )
