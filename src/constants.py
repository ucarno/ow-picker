ROLES = ('tank', 'attack', 'support')
HERO_ROLES = {
    'tank': (
        'dva', 'orisa', 'reinhardt', 'roadhog', 'sigma', 'winston', 'wrecking_ball', 'zarya',
    ),
    'attack': (
        'ashe', 'bastion', 'cassidy', 'doomfist', 'echo', 'genji', 'hanzo', 'junkrat', 'mei',
        'pharah', 'reaper', 'soldier_76', 'sombra', 'symmetra', 'torbjorn', 'tracer', 'widowmaker',
    ),
    'support': (
        'ana', 'baptiste', 'brigitte', 'lucio', 'mercy', 'moira', 'zenyatta',
    )
}

POINT_COLOR = (255, 255, 255)
POINT_HEIGHT = 892
POINT_STEP = 54

POINT_TANK_START = 102
POINT_ATTACK_START = 557
POINT_SUPPORT_START = 1500

POINT_CHECK_INDEXES = (0, 2, 4, 6)


def get_points_tuple(width_start: int, count: int) -> tuple[tuple[int, int], ...]:
    step_total = 0
    points = []
    for i in range(count):
        points.append((width_start + step_total, POINT_HEIGHT))
        step_total += POINT_STEP
    return tuple(points)


ROLE_POINTS = {
    'tank': get_points_tuple(POINT_TANK_START, len(HERO_ROLES['tank'])),
    'attack': get_points_tuple(POINT_ATTACK_START, len(HERO_ROLES['attack'])),
    'support': get_points_tuple(POINT_SUPPORT_START, len(HERO_ROLES['support']))
}

LOCALES = (
    'en',
    'ru',
)

