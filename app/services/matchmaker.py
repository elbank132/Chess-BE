from typing import Callable, Optional

class Matchmaker:
    def __init__(self, on_match_found_callback: Callable):
        self._queue = []
        self._on_match_found_callback = on_match_found_callback

    async def add_player(self, player_id: str):
        """Adds a player to the waiting list."""
        self._queue.append(player_id)
        await self.find_match()

    async def find_match(self):
        """Finds a match for two players if available."""
        if len(self._queue) >= 2:
            white_player = self._queue.pop(0)
            black_player = self._queue.pop(0)
            await self._on_match_found_callback(white_player, black_player)
            
