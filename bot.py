import enum
import random
from typing import List, Optional


class Direction(enum.Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


modifier = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
    Direction.RIGHT: (0, 1),
}

orient = {
    'v': {Direction.UP, Direction.DOWN},
    'h': {Direction.LEFT, Direction.RIGHT},
}


class Bot:
    # Percentage of changing course from a non-collision orientation
    LIKES_TO_MOVE_MIN = 0
    LIKES_TO_MOVE_MAX = 30

    # The cell length of rays that check for collisions
    COLLISION_CHECK_RANGE_MIN = 3
    COLLISION_CHECK_RANGE_MAX = 5

    def __init__(self, bot_id: str):
        self.bot_id = bot_id
        self.likes_to_move = random.randint(self.LIKES_TO_MOVE_MIN, self.LIKES_TO_MOVE_MAX)

    def any_collisions(self, head: List[int], direction: Direction, board: List[List[int]]) -> bool:
        """
        Check if the given head collides with the board borders or any other snakes (in the current
        direction).
        """
        collision_range = random.randint(
            self.COLLISION_CHECK_RANGE_MIN, self.COLLISION_CHECK_RANGE_MAX
        )
        look = head[:]
        for i in range(collision_range):
            look[0] += modifier[direction][0]
            look[1] += modifier[direction][1]

            if (
                look[0] < 0 or look[0] >= len(board) or
                look[1] < 0 or look[1] >= len(board[0]) or
                board[look[0]][look[1]] == 1
            ):
                return True
        return False

    def move(
        self,
        direction: Direction,
        cells: List[List[int]],
        board: List[List[int]]
    ) -> Optional[Direction]:
        """
        Get the direction of movement of the bot.
        If no move needed, returns None.
        """
        # Check current direction and direction candidates for collisions
        direction_candidates = list(orient['h'] if direction in orient['v'] else orient['v'])
        random.shuffle(direction_candidates)

        is_safe = {}
        for direction_candidate in [direction] + direction_candidates:
            is_safe[direction_candidate] = not self.any_collisions(
                cells[-1], direction_candidate, board
            )
        safe_candidates = [candidate for candidate, safe in is_safe.items() if safe]

        for candidate in safe_candidates:
            # If current direction is safe, and we have other candidates to choose from, we still
            # want to have a chance to turn (for a more human-like bot)
            if candidate == direction and len(safe_candidates) > 1:
                if random.randint(0, 100) + self.likes_to_move > 100:
                    return safe_candidates[1]
                else:
                    return None

            # We found a safe direction
            return candidate

        return None
