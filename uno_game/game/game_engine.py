import random
from collections import Counter
from audio.audio import AudioManager
from ui.winner_page import *
import pygame
from .food_drink_methods import FoodDrinkMixin
from items.consumables import registry, Effect

audio = AudioManager(audio_folder=r"uno_game\assets")


class GameManager(FoodDrinkMixin):
    """Manages the state and logic of a Zanzibar dice game with food/drink support."""

    def __init__(self, player_names: list, starting_chips: int = 20, screen=None):
        """
        Initializes the Zanzibar game.

        Args:
            player_names: A list of names for the players.
            starting_chips: The number of chips each player starts with.
        """
        self.screen = screen

        if len(player_names) < 2:
            raise ValueError("Zanzibar requires at least 2 players.")

        self.players = {name: {
            'chips': starting_chips,
            'active_effects': {},  # {Effect: turns_remaining}
            'inventory': None  # Will be set from main.py
        } for name in player_names}
        self.player_order = player_names
        self.round_results = {}
        self.current_round = 0
        print(f"Zanzibar game started with players: {', '.join(player_names)}")
        self.print_scores()

    @staticmethod
    def _calculate_score(roll: list) -> dict:
        """
        Calculates the score of a roll based on Zanzibar rules.
        A higher 'rank' is always better. For rolls with the same rank (e.g., two
        different three-of-a-kinds), the 'value' is used to break ties.

        Args:
            roll: A list of 3 integers representing a dice roll.

        Returns:
            A dictionary containing the comparable score and the chip payout value.
        """
        roll.sort()

        # Zanzibar (4,5,6) - highest
        if roll == [4, 5, 6]:
            return {'score': (4, 0), 'payout': 4, 'name': "Zanzibar!"}

        # Three-of-a-kind - second highest. Rules rank 1-1-1 above 2-2-2 ... above 6-6-6.
        if roll[0] == roll[1] == roll[2]:
            # invert the pip value so that triple 1 > triple 2 > ... > triple 6
            triple_rank = 7 - roll[0]
            return {'score': (3, triple_rank), 'payout': 3, 'name': f"Three of a kind ({roll[0]}s)"}

        # 1,2,3 - next best
        if roll == [1, 2, 3]:
            return {'score': (2, 0), 'payout': 2, 'name': "1-2-3"}

        # Points total - lowest rank. Per common Zanzibar rules, 1s count as 100, 6s as 60,
        # other faces count as their pip value.
        def pip_value(d):
            if d == 1:
                return 100
            if d == 6:
                return 60
            return d

        pts = sum(pip_value(d) for d in roll)
        return {'score': (1, pts), 'payout': 1, 'name': f"Points total ({pts})"}

    def _simulate_player_turn(self, max_rolls: int, player_name: str = None) -> dict:
        """Simulates a single player's turn, trying to get the best score.
        
        Args:
            max_rolls: Maximum number of rolls allowed
            player_name: Name of the player (used for applying effects)
        """
        # Apply LUCK_BOOST: small chance to get a perfect roll
        if player_name and self.has_effect(player_name, Effect.LUCK_BOOST):
            if random.random() < 0.15:  # 15% chance with luck boost
                print(f"✨ {player_name}'s LUCK shines! Getting a great roll...")
                current_roll = [4, 5, 6]  # Zanzibar!
                return {'final_roll': current_roll, 'rolls_taken': 1}
        
        # initial roll
        current_roll = [random.randint(1, 6) for _ in range(3)]

        # roll_count tracks how many rolls have been used (1..max_rolls)
        for roll_num in range(1, max_rolls + 1):
            score_info = self._calculate_score(current_roll)
            # Simple AI: Stop if score is high, otherwise re-roll.
            # A good hand (rank > 1) is worth keeping.
            if score_info['score'][0] > 1:
                return {'final_roll': current_roll, 'rolls_taken': roll_num}

            # AI: Decide which dice to re-roll. Keep pairs or high dice.
            counts = Counter(current_roll)
            if 3 in counts.values():  # Three of a kind
                return {'final_roll': current_roll, 'rolls_taken': roll_num}

            # if we've already used the last roll, stop and return
            if roll_num == max_rolls:
                break

            kept_dice = []
            # Keep pairs
            for val, count in counts.items():
                if count == 2:
                    kept_dice.extend([val, val])
                    break

            # If no pair, keep the highest die
            if not kept_dice:
                kept_dice.append(max(current_roll))

            num_to_reroll = 3 - len(kept_dice)
            new_dice = [random.randint(1, 6) for _ in range(num_to_reroll)]
            current_roll = kept_dice + new_dice

        return {'final_roll': current_roll, 'rolls_taken': max_rolls}

    def play_round(self):
        """Plays one full round of Zanzibar."""
        print("\n--- Starting New Round ---")
        audio.play_sound_effect("dice_b.wav", volume=0.8)
        self.round_results = {}

        # First player's turn sets the roll limit for others
        first_player = self.player_order[0]
        print(f"\n{first_player}'s turn (first player):")
        turn_result = self._simulate_player_turn(max_rolls=3, player_name=first_player)
        self.round_results[first_player] = turn_result
        roll_limit = turn_result['rolls_taken']
        print(f"{first_player} finished in {roll_limit} roll(s) with {turn_result['final_roll']}")

        # Other players' turns
        for i in range(1, len(self.player_order)):
            player = self.player_order[i]
            print(f"\n{player}'s turn (must finish in {roll_limit} roll(s) or fewer):")
            turn_result = self._simulate_player_turn(max_rolls=roll_limit, player_name=player)
            self.round_results[player] = turn_result
            print(f"{player} finished in {turn_result['rolls_taken']} roll(s) with {turn_result['final_roll']}")

        self._resolve_round()
        
        # Update effects for all players after the round
        for player in self.player_order:
            self.update_effects(player)
        
        self.current_round += 1
        winner = self.check_for_winner()
        if winner:
            self.winner_found(winner)

    def _resolve_round(self):
        """Determines loser and winner, and handles chip payout."""
        print("\n--- Round Results ---")

        # Calculate scores for all players
        scores = {player: self._calculate_score(result['final_roll']) for player, result in self.round_results.items()}

        for player, score_info in scores.items():
            print(f"{player}: {score_info['name']}")

        # Find the loser (lowest score) and winner (highest score)
        loser = min(scores, key=lambda p: scores[p]['score'])
        winner = max(scores, key=lambda p: scores[p]['score'])

        # The payout is determined by the WINNER's hand
        payout_amount = scores[winner]['payout']

        print(f"\n{winner} had the highest hand ({scores[winner]['name']}).")
        print(f"{loser} had the lowest hand and receives {payout_amount} chips from every other player.")

        # Distribute chips
        for player in self.players:
            if player != loser:
                self.players[player]['chips'] -= payout_amount
                self.players[loser]['chips'] += payout_amount

        self.print_scores()

        # Per rules: winner of the round rolls first next round. Rotate player_order
        try:
            idx = self.player_order.index(winner)
            self.player_order = self.player_order[idx:] + self.player_order[:idx]
        except ValueError:
            # if something odd happened, leave order as-is
            pass

    def print_scores(self):
        """Prints the current chip counts for all players."""
        print("\n--- Current Chip Counts ---")
        for player, data in self.players.items():
            print(f"{player}: {data['chips']} chips")
        print("---------------------------")

    def check_for_winner(self):
        """Checks if any player has run out of chips."""
        for player, data in self.players.items():
            if data['chips'] <= 0:
                print(f"\n🎉 {player} has lost all their chips and is the winner! 🎉")
                return player
        return None

    def use_item(self, player_name: str, item_name: str) -> bool:
        """Use a consumable item and apply its effects to the player.
        
        Args:
            player_name: Name of the player using the item
            item_name: Name of the item to use
            
        Returns:
            True if item was successfully used, False otherwise
        """
        if player_name not in self.players:
            return False
            
        player_data = self.players[player_name]
        inventory = player_data.get('inventory')
        
        if not inventory or inventory.get_item_quantity(item_name) <= 0:
            print(f"[USE_ITEM] {player_name} doesn't have {item_name}")
            return False
            
        # Get the item from registry
        item = registry.get_item(item_name)
        if not item:
            return False
            
        # Remove from inventory
        if not inventory.remove_item(item):
            return False
        
        # Apply effects
        if 'active_effects' not in player_data:
            player_data['active_effects'] = {}
            
        for effect in item.effects:
            player_data['active_effects'][effect] = item.duration
            print(f"[EFFECT] {player_name} gained {effect.value} for {item.duration} turns!")
            
        return True
    
    def update_effects(self, player_name: str):
        """Decrease duration of active effects and remove expired ones.
        Called at the end of each player's turn.
        
        Args:
            player_name: Name of the player whose effects to update
        """
        if player_name not in self.players:
            return
            
        player_data = self.players[player_name]
        if 'active_effects' not in player_data:
            player_data['active_effects'] = {}
            return
            
        active_effects = player_data['active_effects']
        expired = []
        
        for effect, turns_left in active_effects.items():
            active_effects[effect] = turns_left - 1
            if active_effects[effect] <= 0:
                expired.append(effect)
                print(f"[EFFECT] {player_name}'s {effect.value} has worn off")
        
        for effect in expired:
            del active_effects[effect]
    
    def get_active_effects(self, player_name: str) -> dict:
        """Get all active effects for a player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            Dictionary of {Effect: turns_remaining}
        """
        if player_name not in self.players:
            return {}
            
        player_data = self.players[player_name]
        return player_data.get('active_effects', {})
    
    def has_effect(self, player_name: str, effect: Effect) -> bool:
        """Check if a player has a specific effect active.
        
        Args:
            player_name: Name of the player
            effect: The effect to check for
            
        Returns:
            True if player has the effect active
        """
        active_effects = self.get_active_effects(player_name)
        return effect in active_effects and active_effects[effect] > 0

    def winner_found(self, player):
        print(f"Congratulations {player}")
        winner_screen = WinnerScreen(
            winner_name=player,
            message="Master of Dice!"
        )
        winner_screen.run(self.screen, audio_manager=audio)
        pygame.time.delay(2000)
        pygame.quit()
        raise SystemExit

