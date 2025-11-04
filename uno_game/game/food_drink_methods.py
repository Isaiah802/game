    def use_item(self, player_name: str, item_name: str) -> bool:
        """Have a player use a food/drink item."""
        if player_name not in self.players:
            return False
            
        player_data = self.players[player_name]
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
            player_data['inventory'].update_effects()
            
            # Decrease energy over time
            player_data['energy'] = max(0, player_data['energy'] - 5)
    
    def get_player_effects(self, player_name: str) -> list:
        """Get all active effects for a player."""
        if player_name not in self.players:
            return []
        return [effect for effect in Effect 
                if self.players[player_name]['inventory'].has_effect(effect)]
    
    def get_player_energy(self, player_name: str) -> int:
        """Get a player's current energy level."""
        if player_name not in self.players:
            return 0
        return self.players[player_name]['energy']
    
    def apply_effect_bonuses(self, player_name: str, roll_result: int) -> int:
        """Apply any effect bonuses to a roll result."""
        if player_name not in self.players:
            return roll_result
            
        player_data = self.players[player_name]
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