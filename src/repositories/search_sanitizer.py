"""Search term sanitizer to prevent wildcard injection (SEC-07)."""


def sanitize_search(term: str) -> str:
    """
    Sanitize search term for ILIKE queries.
    - Truncate to 100 chars
    - Escape backslashes (SQLAlchemy ILIKE wildcard escape)
    - Strip leading/trailing whitespace
    """
    if not term:
        return ""
    term = term[:100].strip()
    term = term.replace("\\", "\\\\")  # escape backslash
    return term
