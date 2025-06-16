from enum import Enum


class State(Enum):
    ZOMBIE = "zombie"
    HEALTHY = "healthy"
    INJURED = "injured"
    CORPSE = "corpse"

class ActionState(Enum):
    SAVE = 'save'
    SQUISH = 'squish'
    SKIP = 'skip'
    SCRAM = 'scram'
    
class ActionCost(Enum):
    SAVE = 30
    SQUISH = 5
    SKIP = 15
    SCRAM = 120