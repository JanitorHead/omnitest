"""Panel de trabajo / log de incidencias — HTML propio (sin st.container/st.status)."""
from __future__ import annotations

import html as html_lib
from typing import Literal

import streamlit as st

State = Literal["running", "complete", "error"]


class WorkLog:
    """Panel con estética Omnitest; API compatible con el antiguo st.status."""

    def __init__(self, title: str = "Trabajando…") -> None:
        self._title = title
        self._state: State = "running"
        self._lines: list[str] = []
        self._footer = ""
        self._panel = None

    def __enter__(self) -> WorkLog:
        self._panel = st.empty()
        self._render_panel()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool | None:
        return None

    def write(self, msg: str) -> None:
        self._lines.append(html_lib.escape(msg))
        self._render_panel()

    def markdown(self, msg: str) -> None:
        self._lines.append(msg)
        self._render_panel()

    def caption(self, msg: str) -> None:
        self._footer = msg
        self._render_panel()

    def update(
        self,
        *,
        label: str | None = None,
        state: State | None = None,
        expanded: bool | None = None,  # noqa: ARG002 — compat st.status
    ) -> None:
        if label is not None:
            self._title = label
        if state is not None:
            self._state = state
        self._render_panel()

    def _icon_html(self) -> str:
        if self._state == "complete":
            return '<span class="omni-worklog-icon omni-worklog-icon--ok" aria-hidden="true">✓</span>'
        if self._state == "error":
            return '<span class="omni-worklog-icon omni-worklog-icon--err" aria-hidden="true">!</span>'
        return '<span class="omni-worklog-spinner" aria-hidden="true"></span>'

    def _body_html(self) -> str:
        if not self._lines:
            return ""
        chunks = "".join(f'<p class="omni-worklog-line">{line}</p>' for line in self._lines)
        return f'<div class="omni-worklog-body">{chunks}</div>'

    def _footer_html(self) -> str:
        if not self._footer:
            return ""
        return (
            f'<p class="omni-worklog-foot">{html_lib.escape(self._footer)}</p>'
        )

    def _render_panel(self) -> None:
        if self._panel is None:
            return
        title = html_lib.escape(self._title)
        self._panel.markdown(
            f'<div class="omni-worklog-panel omni-worklog-panel--{self._state}">'
            f'<div class="omni-worklog-header">'
            f"{self._icon_html()}"
            f'<span class="omni-worklog-title">{title}</span>'
            f"</div>"
            f"{self._body_html()}"
            f"{self._footer_html()}"
            f"</div>",
            unsafe_allow_html=True,
        )


def work_log(title: str = "Trabajando…") -> WorkLog:
    return WorkLog(title=title)
