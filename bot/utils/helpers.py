"""Small helper functions."""
import hashlib
import random
import string


def format_number(n: int) -> str:
    """Format int with thousand separators."""
    if n is None:
        return "0"
    return f"{int(n):,}"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def md5(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def escape_md(text: str) -> str:
    """Escape Telegram markdown special chars."""
    if not text:
        return ""
    for ch in ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]:
        text = text.replace(ch, f"\\{ch}")
    return text


def truncate(text: str, max_len: int = 200, suffix: str = "…") -> str:
    """Truncate text to max_len, append suffix if cut."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def progress_bar(percent: float, length: int = 10) -> str:
    """ASCII progress bar."""
    percent = max(0.0, min(100.0, percent))
    filled = int(length * percent / 100)
    return "▓" * filled + "░" * (length - filled)


def format_duration(seconds: int) -> str:
    """Format seconds as human-readable."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    if seconds < 86400:
        h, m = divmod(seconds, 3600)
        return f"{h}s {m}m"
    d, h = divmod(seconds, 86400)
    return f"{d}d {h}s"


def random_referral_code(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))