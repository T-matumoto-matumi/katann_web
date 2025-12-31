export const ResourceType = {
    BRICK: "brick",
    LUMBER: "lumber",
    WOOL: "wool",
    GRAIN: "grain",
    ORE: "ore",
    DESERT: "desert",
} as const;

export type ResourceType = typeof ResourceType[keyof typeof ResourceType];

export interface Hex {
    id: number;
    resource: ResourceType;
    number: number | null;
    q: number;
    r: number;
}

export const PlayerColor = {
    RED: "red",
    BLUE: "blue",
    ORANGE: "orange",
    WHITE: "white",
} as const;

export type PlayerColor = typeof PlayerColor[keyof typeof PlayerColor];

export interface VertexID {
    q: number;
    r: number;
    corner: number;
}

export interface EdgeID {
    q: number;
    r: number;
    edge: number;
}

export interface Building {
    owner: PlayerColor;
    type: string;
    location: VertexID;
}

export interface Road {
    owner: PlayerColor;
    location: EdgeID;
}

export interface GameLog {
    message: string;
    player_color?: PlayerColor;
    timestamp: number;
}

export interface GameState {
    players: PlayerColor[];
    current_turn_index: number;
    phase: string;
    buildings: Building[];
    roads: Road[];
    inventories: Record<PlayerColor, Record<ResourceType, number>>;
    last_dice_result: number | null;
    turn_sub_phase: string | null;
    logs: GameLog[];
    // active_trade removed for revert
}

export interface BoardData {
    hexes: Hex[];
}
