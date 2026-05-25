"""
Shared navigation helpers for role-specific Streamlit pages.
"""

from __future__ import annotations

from arthritis_platform.web.language import LANGUAGE_LABELS, language_code


def get_query_language(st_module: object, default: str = "zh") -> str:
    """Read ?lang=zh/en from Streamlit query params."""
    try:
        value = st_module.query_params.get("lang", default)
    except Exception:
        value = default
    if isinstance(value, list):
        value = value[0] if value else default
    normalized = str(value).strip().lower()
    return "en" if normalized in {"en", "english"} else "zh"


def language_index(lang: str) -> int:
    """Return the selectbox index for a language code."""
    return 1 if lang == "en" else 0


def sync_language_query(st_module: object, selected_language: str) -> str:
    """Persist the selected language in the page URL for cross-page navigation."""
    lang = language_code(selected_language)
    try:
        current = st_module.query_params.get("lang")
        if isinstance(current, list):
            current = current[0] if current else None
        if current != lang:
            st_module.query_params["lang"] = lang
    except Exception:
        pass
    return lang


def language_selectbox(st_module: object, key: str, label: str = "页面语言 / Page language") -> tuple[str, str]:
    """Render a language selector initialized from the current URL."""
    selected = st_module.selectbox(
        label,
        LANGUAGE_LABELS,
        index=language_index(get_query_language(st_module)),
        key=key,
    )
    return selected, sync_language_query(st_module, selected)
