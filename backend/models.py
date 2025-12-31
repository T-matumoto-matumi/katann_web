from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Dict

class ResourceType(str, Enum):
    BRICK = "brick"
    LUMBER = "lumber"
    WOOL = "wool"
    GRAIN = "grain"
    ORE = "ore"
    DESERT = "desert"

class PlayerColor(str, Enum):
    RED = "red"
    BLUE = "blue"
    ORANGE = "orange"
    WHITE = "white"

class Hex(BaseModel):
    id: int
    resource: ResourceType
    number: Optional[int] = None
    q: int
    r: int

class VertexID(BaseModel):
    q: int
    r: int
    corner: int # 0-5

    def __hash__(self):
        return hash((self.q, self.r, self.corner))
    
    def __eq__(self, other):
        return (self.q, self.r, self.corner) == (other.q, other.r, other.corner)

class EdgeID(BaseModel):
    q: int
    r: int
    edge: int # 0-5

    def __hash__(self):
        return hash((self.q, self.r, self.edge))

class Building(BaseModel):
    owner: PlayerColor
    type: str = "settlement" # settlement, city
    location: VertexID

class Road(BaseModel):
    owner: PlayerColor
    location: EdgeID

class Board(BaseModel):
    hexes: List[Hex]

class GameLog(BaseModel):
    message: str
    player_color: Optional[PlayerColor] = None
    timestamp: float

class TradeOffer(BaseModel):
    offerer: PlayerColor
    give: Dict[str, int] # Resource -> count
    get: Dict[str, int] # Resource -> count
    responses: List[PlayerColor] = [] # Players who accepted
    status: str = "OPEN" # OPEN, ACCEPTED, COMPLETED (or just handled by clearing)

class GameState(BaseModel):
    players: List[PlayerColor]
    current_turn_index: int = 0
    phase: str = "INITIAL_PLACEMENT_1" # INITIAL_PLACEMENT_1, INITIAL_PLACEMENT_2, GAME_LOOP
    buildings: List[Building] = []
    roads: List[Road] = []
    
    # New fields for Resources & Dice
    inventories: Dict[PlayerColor, Dict[ResourceType, int]] = {}
    last_dice_result: Optional[int] = None
    turn_sub_phase: Optional[str] = None # ROLL_DICE, BUILD_TRADE
    logs: List[GameLog] = [] # New logs field
    
    # Trading
    active_trade: Optional[TradeOffer] = None

    # We use lists for Pydantic serialization, but logic might use dicts.
    # We will map them in logic.
