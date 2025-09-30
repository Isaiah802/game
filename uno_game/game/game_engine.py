
import random


class GameManager:
    import random

    class GameManager:
        """Manages the state and logic of a simple dice game."""

        def __init__(self):
            """Initializes the game by setting up a place to store player rolls."""
            self.player_rolls = {}

        def add_player(self, player_name: str):
            """
            Adds a player to the game.

            Args:
                player_name: The name of the player to add.
            """
            if player_name not in self.player_rolls:
                self.player_rolls[player_name] = []
                print(f"Player '{player_name}' has joined the game.")
            else:
                print(f"Player '{player_name}' is already in the game.")

        @staticmethod
        def _roll_dice(num_dice: int) -> list[int]:
            """
            A private static method to generate a list of random dice rolls.

            Args:
                num_dice: The number of dice to roll.

            Returns:
                A list of integers representing the outcome of each die roll.
            """
            # A standard die has 6 sides (1-6)
            return [random.randint(1, 6) for _ in range(num_dice)]

        def play_turn(self, player_name: str, num_dice: int = 2):
            """
            Simulates a player's turn by rolling a set number of dice and
            updating their state in the game.

            Args:
                player_name: The name of the player whose turn it is.
                num_dice: The number of dice they will roll. Defaults to 2.
            """
            if player_name not in self.player_rolls:
                print(f"Error: Cannot play turn for '{player_name}' because they are not in the game.")
                return None

            roll_result = self._roll_dice(num_dice)
            self.player_rolls[player_name] = roll_result

            total = sum(roll_result)
            print(f"{player_name} rolled {num_dice} dice: {roll_result} (Total: {total})")
            return roll_result