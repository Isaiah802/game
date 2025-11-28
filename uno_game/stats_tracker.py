"""Statistics tracker for game performance and achievements."""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class StatsTracker:
    """Tracks player statistics, win rates, and achievements."""
    
    def __init__(self, stats_file: str = "stats.json"):
        self.stats_file = stats_file
        self.stats = self.load_stats()
    
    def load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default structure
        return {
            'global': {
                'total_games': 0,
                'total_rounds': 0,
                'total_playtime': 0.0,
                'dice_rolled': 0,
                'items_purchased': 0,
                'items_used': 0
            },
            'players': {},
            'achievements': {},
            'high_scores': [],
            'longest_game': {'rounds': 0, 'timestamp': None},
            'quickest_win': {'rounds': float('inf'), 'timestamp': None}
        }
    
    def save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get statistics for a specific player."""
        if player_name not in self.stats['players']:
            self.stats['players'][player_name] = {
                'games_played': 0,
                'wins': 0,
                'losses': 0,
                'rounds_played': 0,
                'total_rolls': 0,
                'highest_roll': 0,
                'total_chips_won': 0,
                'total_chips_lost': 0,
                'items_bought': 0,
                'items_used': 0,
                'favorite_hand': {},
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            }
        return self.stats['players'][player_name]
    
    def record_game_start(self, player_names: List[str]):
        """Record the start of a new game."""
        self.stats['global']['total_games'] += 1
        for name in player_names:
            pstats = self.get_player_stats(name)
            pstats['games_played'] += 1
            pstats['last_seen'] = datetime.now().isoformat()
    
    def record_round(self, player: str, roll: List[int], hand_name: str, chips_won: int):
        """Record a round result."""
        self.stats['global']['total_rounds'] += 1
        self.stats['global']['dice_rolled'] += len(roll)
        
        pstats = self.get_player_stats(player)
        pstats['rounds_played'] += 1
        pstats['total_rolls'] += 1
        
        roll_sum = sum(roll)
        if roll_sum > pstats['highest_roll']:
            pstats['highest_roll'] = roll_sum
        
        if chips_won > 0:
            pstats['total_chips_won'] += chips_won
        else:
            pstats['total_chips_lost'] += abs(chips_won)
        
        # Track favorite hands
        if hand_name not in pstats['favorite_hand']:
            pstats['favorite_hand'][hand_name] = 0
        pstats['favorite_hand'][hand_name] += 1
    
    def record_game_end(self, winner: str, loser: str, rounds: int, duration: float):
        """Record game completion."""
        # Update winner stats
        winner_stats = self.get_player_stats(winner)
        winner_stats['wins'] += 1
        
        # Update loser stats
        loser_stats = self.get_player_stats(loser)
        loser_stats['losses'] += 1
        
        # Update global stats
        self.stats['global']['total_playtime'] += duration
        
        # Check for records
        if rounds > self.stats['longest_game']['rounds']:
            self.stats['longest_game'] = {
                'rounds': rounds,
                'timestamp': datetime.now().isoformat(),
                'winner': winner,
                'loser': loser
            }
        
        if rounds < self.stats['quickest_win']['rounds']:
            self.stats['quickest_win'] = {
                'rounds': rounds,
                'timestamp': datetime.now().isoformat(),
                'winner': winner,
                'loser': loser
            }
        
        # Update high scores
        self._update_high_scores(winner, rounds, duration)
        
        self.save_stats()
    
    def record_item_purchase(self, player: str, item: str, cost: int):
        """Record item purchase."""
        self.stats['global']['items_purchased'] += 1
        pstats = self.get_player_stats(player)
        pstats['items_bought'] += 1
        pstats['last_seen'] = datetime.now().isoformat()
    
    def record_item_use(self, player: str, item: str):
        """Record item usage."""
        self.stats['global']['items_used'] += 1
        pstats = self.get_player_stats(player)
        pstats['items_used'] += 1
    
    def _update_high_scores(self, player: str, rounds: int, duration: float):
        """Update high score leaderboard."""
        score_entry = {
            'player': player,
            'rounds': rounds,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        self.stats['high_scores'].append(score_entry)
        # Sort by fewest rounds (quickest wins) and keep top 10
        self.stats['high_scores'].sort(key=lambda x: x['rounds'])
        self.stats['high_scores'] = self.stats['high_scores'][:10]
    
    def get_win_rate(self, player: str) -> float:
        """Calculate win rate for a player."""
        pstats = self.get_player_stats(player)
        total = pstats['games_played']
        if total == 0:
            return 0.0
        return pstats['wins'] / total
    
    def get_leaderboard(self, sort_by: str = 'wins') -> List[Dict[str, Any]]:
        """Get leaderboard sorted by specified metric."""
        players = []
        for name, stats in self.stats['players'].items():
            entry = {
                'name': name,
                'wins': stats['wins'],
                'games': stats['games_played'],
                'win_rate': self.get_win_rate(name),
                'highest_roll': stats['highest_roll']
            }
            players.append(entry)
        
        # Sort based on criteria
        if sort_by == 'wins':
            players.sort(key=lambda x: x['wins'], reverse=True)
        elif sort_by == 'win_rate':
            players.sort(key=lambda x: x['win_rate'], reverse=True)
        elif sort_by == 'games':
            players.sort(key=lambda x: x['games'], reverse=True)
        
        return players
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all statistics."""
        return {
            'total_games': self.stats['global']['total_games'],
            'total_rounds': self.stats['global']['total_rounds'],
            'total_playtime': self.stats['global']['total_playtime'],
            'total_players': len(self.stats['players']),
            'longest_game': self.stats['longest_game'],
            'quickest_win': self.stats['quickest_win'],
            'top_players': self.get_leaderboard('wins')[:5]
        }
