"""Replay system for recording and playing back game sessions."""

import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime


class GameReplay:
    """Records and replays game sessions."""
    
    def __init__(self, replay_dir: str = "replays"):
        self.replay_dir = replay_dir
        self.current_recording = None
        self.is_recording = False
        self.is_playing = False
        self.playback_data = None
        self.playback_index = 0
        
        # Create replay directory if it doesn't exist
        if not os.path.exists(replay_dir):
            os.makedirs(replay_dir)
    
    def start_recording(self, player_names: List[str], starting_chips: int):
        """Start recording a new game session."""
        self.current_recording = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'players': player_names,
            'starting_chips': starting_chips,
            'events': [],
            'metadata': {
                'duration': 0,
                'rounds': 0,
                'winner': None
            }
        }
        self.is_recording = True
        self.recording_start_time = time.time()
    
    def record_event(self, event_type: str, data: Dict[str, Any]):
        """Record a game event."""
        if not self.is_recording or self.current_recording is None:
            return
        
        elapsed = time.time() - self.recording_start_time
        event = {
            'timestamp': elapsed,
            'type': event_type,
            'data': data
        }
        self.current_recording['events'].append(event)
    
    def record_round(self, round_num: int, current_player: str, roll_result: List[int], 
                    chip_changes: Dict[str, int], item_used: Optional[str] = None):
        """Record a complete round."""
        self.record_event('round', {
            'round_number': round_num,
            'player': current_player,
            'roll': roll_result,
            'chip_changes': chip_changes,
            'item_used': item_used
        })
        self.current_recording['metadata']['rounds'] = round_num
    
    def record_item_purchase(self, player: str, item: str, cost: int):
        """Record item purchase."""
        self.record_event('item_purchase', {
            'player': player,
            'item': item,
            'cost': cost
        })
    
    def record_item_use(self, player: str, item: str):
        """Record item usage."""
        self.record_event('item_use', {
            'player': player,
            'item': item
        })
    
    def stop_recording(self, winner: Optional[str] = None) -> str:
        """Stop recording and save the replay file. Returns the filepath."""
        if not self.is_recording or self.current_recording is None:
            return ""
        
        self.is_recording = False
        self.current_recording['metadata']['duration'] = time.time() - self.recording_start_time
        self.current_recording['metadata']['winner'] = winner
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"replay_{timestamp}.json"
        filepath = os.path.join(self.replay_dir, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.current_recording, f, indent=2)
        
        self.current_recording = None
        return filepath
    
    def load_replay(self, filepath: str) -> bool:
        """Load a replay file for playback."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.playback_data = json.load(f)
            self.playback_index = 0
            self.is_playing = True
            return True
        except Exception as e:
            print(f"Error loading replay: {e}")
            return False
    
    def get_replay_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a replay without loading it fully."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {
                'timestamp': data.get('timestamp', ''),
                'players': data.get('players', []),
                'rounds': data['metadata'].get('rounds', 0),
                'duration': data['metadata'].get('duration', 0),
                'winner': data['metadata'].get('winner', None)
            }
        except Exception:
            return None
    
    def list_replays(self) -> List[Dict[str, Any]]:
        """List all available replays with their metadata."""
        replays = []
        try:
            for filename in os.listdir(self.replay_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.replay_dir, filename)
                    info = self.get_replay_info(filepath)
                    if info:
                        info['filepath'] = filepath
                        info['filename'] = filename
                        replays.append(info)
            # Sort by timestamp, newest first
            replays.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        except Exception as e:
            print(f"Error listing replays: {e}")
        return replays
    
    def get_next_event(self) -> Optional[Dict[str, Any]]:
        """Get the next event in the playback sequence."""
        if not self.is_playing or self.playback_data is None:
            return None
        
        events = self.playback_data.get('events', [])
        if self.playback_index >= len(events):
            return None
        
        event = events[self.playback_index]
        self.playback_index += 1
        return event
    
    def reset_playback(self):
        """Reset playback to the beginning."""
        self.playback_index = 0
    
    def stop_playback(self):
        """Stop current playback."""
        self.is_playing = False
        self.playback_data = None
        self.playback_index = 0
    
    def get_playback_progress(self) -> float:
        """Get playback progress as a percentage (0.0 to 1.0)."""
        if not self.is_playing or self.playback_data is None:
            return 0.0
        events = self.playback_data.get('events', [])
        if not events:
            return 0.0
        return self.playback_index / len(events)
