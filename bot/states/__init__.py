"""FSM states for multi-step user flows."""
from aiogram.fsm.state import State, StatesGroup


class AIStates(StatesGroup):
    """AI feature input states."""
    chat          = State()
    image_prompt  = State()
    code          = State()
    code_review   = State()
    write         = State()
    translate     = State()
    resume        = State()
    ads           = State()
    seo           = State()
    prompt_gen    = State()


class ToolStates(StatesGroup):
    """Utility tool states."""
    qr        = State()
    base64    = State()
    json      = State()
    hash      = State()
    urlshort  = State()


class CyberStates(StatesGroup):
    """Cyber tools states."""
    ip      = State()
    dns     = State()
    whois   = State()
    ssl     = State()
    headers = State()
    status  = State()
    ua      = State()


class DownloadStates(StatesGroup):
    """Downloader flow."""
    waiting_url = State()


class PremiumStates(StatesGroup):
    """Premium / promo flow."""
    waiting_promo = State()


class AdminStates(StatesGroup):
    """Admin panel states."""
    broadcast_text     = State()
    broadcast_confirm  = State()
    ban_user           = State()
    unban_user         = State()
    give_premium       = State()
    create_promo       = State()