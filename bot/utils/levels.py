"""Level / XP calculation utilities."""

LEVEL_THRESHOLDS = [0, 100, 250, 500, 1000, 2000, 3500, 5500, 8500, 13000,
                   20000, 30000, 45000, 65000, 90000, 125000, 175000, 240000,
                   325000, 425000, 550000, 700000, 900000, 1150000, 1450000]


def calculate_level(xp: int) -> int:
    """Return level for given XP."""
    if not xp:
        return 1
    level = 1
    for threshold in LEVEL_THRESHOLDS:
        if xp >= threshold:
            level = LEVEL_THRESHOLDS.index(threshold) + 1
        else:
            break
    return min(level, len(LEVEL_THRESHOLDS))


def xp_for_level(level: int) -> int:
    """XP needed to reach this level."""
    if level <= 1:
        return 0
    if level > len(LEVEL_THRESHOLDS):
        return LEVEL_THRESHOLDS[-1]
    return LEVEL_THRESHOLDS[level - 1]


def progress_to_next_level(xp: int) -> tuple[int, int, float]:
    """Return (current_level_xp, next_level_xp, progress_percent)."""
    cur_lvl = calculate_level(xp)
    cur_xp = xp_for_level(cur_lvl)
    next_xp = xp_for_level(cur_lvl + 1) if cur_lvl < len(LEVEL_THRESHOLDS) else cur_xp
    if next_xp == cur_xp:
        return cur_xp, next_xp, 100.0
    progress = (xp - cur_xp) / (next_xp - cur_xp) * 100
    return cur_xp, next_xp, max(0.0, min(100.0, progress))