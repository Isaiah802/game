"""
Module for handling consumable items in the game (food and drinks).
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict

class ItemType(Enum):
    """Enumeration of consumable item types."""
    FOOD = "food"
    DRINK = "drink"

class Effect(Enum):
    """Enumeration of effects that consumable items can provide."""
    ENERGY_BOOST = "energy_boost"      # Gives extra energy
    LUCK_BOOST = "luck_boost"          # Temporary luck boost
    FOCUS_BOOST = "focus_boost"        # Better card visibility/memory
    MOOD_BOOST = "mood_boost"          # Happy mood effects

@dataclass
class ConsumableItem:
    """Represents a food or drink item that can be consumed during the game."""
    name: str
    item_type: ItemType
    description: str
    energy_value: int  # How much energy it provides
    effects: List[Effect]  # Special effects the item provides
    duration: int  # How long effects last (in turns)
    cost: int  # Cost in game currency
    image_path: Optional[str] = None  # Path to item's image

class ItemRegistry:
    """Registry of all available food and drink items in the game."""
    
    def __init__(self):
        """Initialize the item registry with default items."""
        self.items: Dict[str, ConsumableItem] = {}
        self._initialize_items()
    
    def _initialize_items(self):
        """Initialize the default food and drink items."""
        # Foods
        self.add_item(ConsumableItem(
            name="Pizza Slice",
            item_type=ItemType.FOOD,
            description="A tasty slice of pizza. Boosts energy significantly!",
            energy_value=50,
            effects=[Effect.ENERGY_BOOST],
            duration=3,
            cost=1
        ))
        
        self.add_item(ConsumableItem(
            name="Lucky Cookie",
            item_type=ItemType.FOOD,
            description="A fortune cookie that might bring you luck!",
            energy_value=20,
            effects=[Effect.LUCK_BOOST],
            duration=2,
            cost=1
        ))
        
        self.add_item(ConsumableItem(
            name="Brain Snack",
            item_type=ItemType.FOOD,
            description="A healthy snack that helps you focus.",
            energy_value=30,
            effects=[Effect.FOCUS_BOOST],
            duration=2,
            cost=120
        ))
        
        # Drinks
        self.add_item(ConsumableItem(
            name="Energy Drink",
            item_type=ItemType.DRINK,
            description="A fizzy drink that boosts your energy!",
            energy_value=40,
            effects=[Effect.ENERGY_BOOST, Effect.FOCUS_BOOST],
            duration=2,
            cost=80
        ))
        
        self.add_item(ConsumableItem(
            name="Happy Juice",
            item_type=ItemType.DRINK,
            description="A fruity drink that puts you in a good mood!",
            energy_value=25,
            effects=[Effect.MOOD_BOOST],
            duration=3,
            cost=90
        ))
        
        self.add_item(ConsumableItem(
            name="Focus Tea",
            item_type=ItemType.DRINK,
            description="A special tea that helps you concentrate.",
            energy_value=15,
            effects=[Effect.FOCUS_BOOST],
            duration=4,
            cost=70
        ))
    
    def add_item(self, item: ConsumableItem):
        """Add a new item to the registry."""
        self.items[item.name] = item
    
    def get_item(self, name: str) -> Optional[ConsumableItem]:
        """Get an item by name."""
        return self.items.get(name)
    
    def get_all_items(self) -> List[ConsumableItem]:
        """Get all registered items."""
        return list(self.items.values())
    
    def get_items_by_type(self, item_type: ItemType) -> List[ConsumableItem]:
        """Get all items of a specific type."""
        return [item for item in self.items.values() if item.item_type == item_type]

# Global registry instance
registry = ItemRegistry()