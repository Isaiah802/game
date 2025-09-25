
import random


class GameManager:
    """Manages the state and logic of an UNO game."""

    def __init__(self):
        self.deck = self._create_uno_deck()
        random.shuffle(self.deck)
        self.discard_pile = []
        self.player_hands = {}

    @staticmethod
    def _create_uno_deck():
        """A private method to create the deck, used only by the class."""
        colors = ['Red', 'Yellow', 'Green', 'Blue']
        card_types = {
            '0': 1, '1': 2, '2': 2, '3': 2, '4': 2, '5': 2,
            '6': 2, '7': 2, '8': 2, '9': 2, 'Skip': 2,
            'Reverse': 2, 'Draw Two': 2
        }
        wild_cards = {'Wild': 4, 'Wild Draw Four': 4}
        deck = []
        for color in colors:
            for card_type, count in card_types.items():
                for _ in range(count):
                    deck.append({'color': color, 'type': card_type})
        for card_type, count in wild_cards.items():
            for _ in range(count):
                deck.append({'color': 'Wild', 'type': card_type})
        return deck

    def deal_cards(self, num_players=1, cards_per_hand=7):
        """Deals cards to the specified number of players."""
        for i in range(num_players):
            player_name = f"Player {i + 1}"
            hand = [self.deck.pop() for _ in range(cards_per_hand)]
            self.player_hands[player_name] = hand

    def start_game(self):
        """Deals cards and starts the discard pile."""
        self.deal_cards()  # Deals to 1 player by default
        self.discard_pile.append(self.deck.pop())