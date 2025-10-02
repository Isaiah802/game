import random
from collections import Counter
from audio.audio import AudioManager
audio = AudioManager(audio_folder=r"uno_game\assets")


class GameManager:
    """Manages the state and logic of a Zanzibar dice game."""

    def __init__(self, player_names: list, starting_chips: int = 20):
        """
        Initializes the Zanzibar game.

        Args:
            player_names: A list of names for the players.
            starting_chips: The number of chips each player starts with.
        """
        if len(player_names) < 2:
            raise ValueError("Zanzibar requires at least 2 players.")

        self.players = {name: {'chips': starting_chips} for name in player_names}
        self.player_order = player_names
        self.round_results = {}
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

    def _simulate_player_turn(self, max_rolls: int) -> dict:
        """Simulates a single player's turn, trying to get the best score."""
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
        turn_result = self._simulate_player_turn(max_rolls=3)
        self.round_results[first_player] = turn_result
        roll_limit = turn_result['rolls_taken']
        print(f"{first_player} finished in {roll_limit} roll(s) with {turn_result['final_roll']}")

        # Other players' turns
        for i in range(1, len(self.player_order)):
            player = self.player_order[i]
            print(f"\n{player}'s turn (must finish in {roll_limit} roll(s) or fewer):")
            turn_result = self._simulate_player_turn(max_rolls=roll_limit)
            self.round_results[player] = turn_result
            print(f"{player} finished in {turn_result['rolls_taken']} roll(s) with {turn_result['final_roll']}")

        self._resolve_round()
        self.check_for_winner()

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
        print("Check for winner")
        """Checks if any player has run out of chips."""
        for player, data in self.players.items():
            if data['chips'] <= 0:
                print(f"\n🎉 {player} has lost all their chips and is the winner! 🎉")
                return player
        return None

    def winner_found(player):
        print(f"congradulations{player}")