"""
Module for food and drink methods that extend GameManager functionality.
"""
import random
from items import registry, Effect, Inventory


class FoodDrinkMixin:
    """Mixin class that adds food and drink functionality to GameManager."""
    
    def use_item(self, player_name: str, item_name: str) -> bool:
        """Have a player use a food/drink item."""
        if player_name not in self.players:
            return False
            
        player_data = self.players[player_name]
        
        # Initialize inventory if not present
        if 'inventory' not in player_data:
            player_data['inventory'] = Inventory()
        
        # Initialize energy if not present
        if 'energy' not in player_data:
            player_data['energy'] = 100
            
        item = registry.get_item(item_name)
        if not item:
            return False
            
        if player_data['inventory'].use_item(item):
            # Apply energy boost
            player_data['energy'] = min(100, player_data['energy'] + item.energy_value)
            return True
        return False
    

    def update_effects(self):
        """Update effects for all players (call each turn)."""
        for player_data in self.players.values():
            # Initialize inventory if not present
            if 'inventory' not in player_data:
                player_data['inventory'] = Inventory()
            
            # Initialize energy if not present
            if 'energy' not in player_data:
                player_data['energy'] = 100
                
            player_data['inventory'].update_effects()
            
            # Decrease energy over time
            player_data['energy'] = max(0, player_data['energy'] - 5)
    
    def get_player_effects(self, player_name: str) -> list:
        """Get all active effects for a player."""
        if player_name not in self.players:
            return []
        
        player_data = self.players[player_name]
        
        # Initialize inventory if not present
        if 'inventory' not in player_data:
            player_data['inventory'] = Inventory()
            
        return [effect for effect in Effect 
                if player_data['inventory'].has_effect(effect)]
    
    def get_player_energy(self, player_name: str) -> int:
        """Get a player's current energy level."""
        if player_name not in self.players:
            return 0
            
        player_data = self.players[player_name]
        
        # Initialize energy if not present
        if 'energy' not in player_data:
            player_data['energy'] = 100
            
        return player_data['energy']
    
    def apply_effect_bonuses(self, player_name: str, roll_result: int) -> int:
        """Apply any effect bonuses to a roll result."""
        if player_name not in self.players:
            return roll_result
            
        player_data = self.players[player_name]
        
        # Initialize inventory if not present
        if 'inventory' not in player_data:
            player_data['inventory'] = Inventory()
            
        modified_result = roll_result
        
        # Apply luck boost if active
        if player_data['inventory'].has_effect(Effect.LUCK_BOOST):
            if random.random() < 0.3:  # 30% chance of luck boost
                modified_result = min(6, modified_result + 1)
        
        # Apply focus boost if active
        if player_data['inventory'].has_effect(Effect.FOCUS_BOOST):
            # Focus boost prevents very low rolls
            modified_result = max(2, modified_result)
        
        return modified_result
    
    def add_item_to_player(self, player_name: str, item_name: str, quantity: int = 1) -> bool:
        """Add an item to a player's inventory."""
        if player_name not in self.players:
            return False
            
        player_data = self.players[player_name]
        
        # Initialize inventory if not present
        if 'inventory' not in player_data:
            player_data['inventory'] = Inventory()
            
        item = registry.get_item(item_name)
        if not item:
            return False
            
        player_data['inventory'].add_item(item, quantity)
        return True