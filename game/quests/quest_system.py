"""
Quest system for objectives and rewards
"""

import random
from typing import List, Dict, Any, Optional
from game.core.settings import Settings

class Quest:
    """Individual quest with objectives and rewards"""
    
    def __init__(self, quest_id: str, title: str, description: str, 
                 quest_type: str, target_count: int, reward_exp: int, reward_items: List[str] = None):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.quest_type = quest_type  # 'kill', 'collect', 'explore', 'reach_level'
        self.target_count = target_count
        self.current_count = 0
        self.reward_exp = reward_exp
        self.reward_items = reward_items or []
        self.completed = False
        self.accepted = False
    
    def update_progress(self, count: int = 1):
        """Update quest progress"""
        if not self.completed and self.accepted:
            self.current_count += count
            if self.current_count >= self.target_count:
                self.completed = True
                return True
        return False
    
    def get_progress_text(self) -> str:
        """Get progress text for quest"""
        return f"{self.current_count}/{self.target_count}"
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage"""
        return min(1.0, self.current_count / self.target_count)

class QuestSystem:
    """Manages quests and objectives"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.active_quests: List[Quest] = []
        self.completed_quests: List[Quest] = []
        self.available_quests: List[Quest] = []
        
        # Quest tracking
        self.enemies_killed = 0
        self.items_collected = 0
        self.areas_explored = 0
        
        # Initialize quests
        self._initialize_quests()
    
    def _initialize_quests(self):
        """Initialize available quests"""
        self.available_quests = [
            Quest("quest_1", "First Blood", "Defeat 5 enemies", "kill", 5, 50, ["Health Potion"]),
            Quest("quest_2", "Collector", "Collect 10 items", "collect", 10, 75, ["Iron Sword"]),
            Quest("quest_3", "Explorer", "Explore 3 different areas", "explore", 3, 100, ["Chain Mail"]),
            Quest("quest_4", "Warrior", "Reach level 5", "reach_level", 5, 150, ["Steel Sword"]),
            Quest("quest_5", "Slayer", "Defeat 20 enemies", "kill", 20, 200, ["Magic Sword"]),
            Quest("quest_6", "Treasure Hunter", "Collect 25 items", "collect", 25, 250, ["Plate Armor"]),
            Quest("quest_7", "Master Explorer", "Explore 10 areas", "explore", 10, 300, ["Legendary Blade"]),
            Quest("quest_8", "Legend", "Reach level 10", "reach_level", 10, 500, ["Dragon Scale"])
        ]
    
    def get_available_quests(self) -> List[Quest]:
        """Get quests available for acceptance"""
        return [q for q in self.available_quests if not q.accepted and not q.completed]
    
    def accept_quest(self, quest_id: str) -> bool:
        """Accept a quest"""
        for quest in self.available_quests:
            if quest.quest_id == quest_id and not quest.accepted:
                quest.accepted = True
                self.active_quests.append(quest)
                return True
        return False
    
    def complete_quest(self, quest_id: str, player) -> bool:
        """Complete a quest and give rewards"""
        for quest in self.active_quests:
            if quest.quest_id == quest_id and quest.completed:
                # Give rewards
                player.gain_experience(quest.reward_exp)
                
                # Give items (placeholder - would need item factory)
                for item_name in quest.reward_items:
                    # TODO: Create actual items from names
                    pass
                
                # Move to completed
                self.active_quests.remove(quest)
                self.completed_quests.append(quest)
                return True
        return False
    
    def update_quest_progress(self, quest_type: str, count: int = 1):
        """Update progress for all active quests of a type"""
        completed_quests = []
        
        for quest in self.active_quests:
            if quest.quest_type == quest_type:
                if quest.update_progress(count):
                    completed_quests.append(quest)
        
        return completed_quests
    
    def on_enemy_killed(self, enemy_type: str):
        """Called when an enemy is killed"""
        self.enemies_killed += 1
        self.update_quest_progress("kill")
    
    def on_item_collected(self, item_name: str):
        """Called when an item is collected"""
        self.items_collected += 1
        self.update_quest_progress("collect")
    
    def on_area_explored(self, area_name: str):
        """Called when a new area is explored"""
        self.areas_explored += 1
        self.update_quest_progress("explore")
    
    def on_level_up(self, new_level: int):
        """Called when player levels up"""
        self.update_quest_progress("reach_level", new_level)
    
    def get_quest_summary(self) -> Dict[str, Any]:
        """Get quest summary for UI"""
        return {
            'active': len(self.active_quests),
            'completed': len(self.completed_quests),
            'available': len(self.get_available_quests()),
            'total_enemies_killed': self.enemies_killed,
            'total_items_collected': self.items_collected,
            'total_areas_explored': self.areas_explored
        }
    
    def generate_random_quest(self) -> Optional[Quest]:
        """Generate a random quest based on player progress"""
        quest_types = ['kill', 'collect', 'explore']
        quest_type = random.choice(quest_types)
        
        if quest_type == 'kill':
            target = random.randint(5, 20)
            exp_reward = target * 10
            title = f"Defeat {target} Enemies"
            description = f"Defeat {target} enemies to earn {exp_reward} experience"
        
        elif quest_type == 'collect':
            target = random.randint(8, 15)
            exp_reward = target * 8
            title = f"Collect {target} Items"
            description = f"Collect {target} items to earn {exp_reward} experience"
        
        else:  # explore
            target = random.randint(2, 5)
            exp_reward = target * 25
            title = f"Explore {target} Areas"
            description = f"Explore {target} new areas to earn {exp_reward} experience"
        
        quest_id = f"random_quest_{random.randint(1000, 9999)}"
        return Quest(quest_id, title, description, quest_type, target, exp_reward)
