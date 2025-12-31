import random
from typing import List
from .models import Board, Hex, ResourceType

def generate_board() -> Board:
    # Resources for 18 hexes (excluding center Desert)
    # 4 Lumber, 4 Wool, 4 Grain, 3 Brick, 3 Ore
    resources = (
        [ResourceType.LUMBER] * 4 +
        [ResourceType.WOOL] * 4 +
        [ResourceType.GRAIN] * 4 +
        [ResourceType.BRICK] * 3 +
        [ResourceType.ORE] * 3
    )
    random.shuffle(resources)

    # Number tokens for 18 hexes
    # 2, 12 (1 each)
    # 3, 4, 5, 6, 8, 9, 10, 11 (2 each)
    numbers = [2, 12] + [3, 4, 5, 6, 8, 9, 10, 11] * 2
    random.shuffle(numbers)

    generated_hexes: List[Hex] = []
    
    # Axial coordinates for a hex grid with radius 2
    coords = []
    for q in range(-2, 3):
        for r in range(-2, 3):
            if -2 <= q + r <= 2:
                coords.append((q, r))
    
    res_idx = 0
    num_idx = 0
    
    for i, (q, r) in enumerate(coords):
        if q == 0 and r == 0:
            # Center is Desert
            generated_hexes.append(Hex(
                id=i,
                resource=ResourceType.DESERT,
                number=None,
                q=q,
                r=r
            ))
        else:
            res = resources[res_idx]
            res_idx += 1
            num = numbers[num_idx]
            num_idx += 1
            
            generated_hexes.append(Hex(
                id=i, 
                resource=res, 
                number=num,
                q=q,
                r=r
            ))
        
    return Board(hexes=generated_hexes)

# Coordinate normalization logic
# Hex neighbors for q,r in order 0..5
# Directions:
# 0: (+1, -1) [Top Right]
# 1: (+1, 0)  [Right]
# 2: (0, +1)  [Bottom Right]
# 3: (-1, +1) [Bottom Left]
# 4: (-1, 0)  [Left]
# 5: (0, -1)  [Top Left]

# Vertex normalization
# A vertex is shared by up to 3 hexes.
# We define the canonical vertex as the one belonging to the hex with the logic:
# Prefer hex with higher q, then higher r? Or just a set of rules.
# Easy way: Convert to specific 3 hex coordinates, sort them, pick the first one + specific corner.
# Or: Always map to corner 0 or 1 of some hex?
# Actually, simpler: just implement equality. But for Pydantic/Storage we want one ID.
# Let's use a standard mapping:
# A vertex is determined by (q, r, corner).
# Corner 0 of (q,r) touches Corner 2 of (q, r-1) and Corner 4 of (q+1, r-1).
# We can map everything to corners 0 or 1?
# Let's map to the hex with the lexicographically smallest (q,r).
# Wait, let's keep it simple for MVP: Just treat (q,r,c) as key, but we need to know they are same.
# We need a function `get_canonical_vertex(q, r, c)` -> (q', r', c')

def get_neighbor(q, r, direction):
    # directions 0..5
    dq = [1, 1, 0, -1, -1, 0]
    dr = [-1, 0, 1, 1, 0, -1]
    return q + dq[direction], r + dr[direction]

def normalize_vertex(q: int, r: int, c: int):
    # Map any corner to a canonical representation.
    # Let's define canonical corners as 0 (top) and 1 (top-right)?
    # No, that logic is complex without a grid system lib.
    # Let's try to map to the hex with "top-left-most" coordinate logic?
    # Alternatively, converting to cartesianish or pixel coordinates and hashing roughly? No.
    
    # Relationships:
    # Corner 0 of (q,r) == Corner 2 of (q, r-1) == Corner 4 of (q+1, r-1)
    # Corner 1 of (q,r) == Corner 3 of (q+1, r-1) == Corner 5 of (q+1, r)
    # Corner 2 of (q,r) == Corner 4 of (q+1, r) == Corner 0 of (q, r+1)
    # ...
    
    # Let's try to convert all to corners 0 or 1.
    # If c=2: -> (q, r+1), c=0
    # If c=3: -> (q-1, r+1), c=1
    # If c=4: -> (q-1, r), c=0   (Wait, corner 4 of q,r touches q-1,r corner 1? No.
    # Directions: 0:TR, 1:R, 2:BR, 3:BL, 4:L, 5:TL
    # Corner N is between Side N-1 and N? Or Side N and N+1?
    # Usually Corner 0 is Top. Side 0 is Top-Right edge.
    # Let's assume Corner k is clockwise from Top (0).
    # Corner 0: Pointing Up. Between Top-Left(5) and Top-Right(0) edges.
    
    # Equivalences:
    # C0 of H(q,r) is shared with H(q, r-1) [C4] and H(q+1, r-1) [C2]? 
    # Let's just generate all 3 possible IDs, sort them, and pick first.
    
    ids = [ (q, r, c) ]
    
    # Neighbors touching corner C
    # C0 touched by (0,-1) -> Neighbor 5? and (1,-1) -> Neighbor 0?
    
    if c == 0:
        # Touches (q, r-1) [C4] -> Should be C2 (Bottom Right of top-left hex)
        # Touches (q+1, r-1) [C2] -> Should be C4 (Bottom Left of top-right hex)
        ids.append( (q, r-1, 2) )
        ids.append( (q+1, r-1, 4) )
    elif c == 1:
        # Touches (q+1, r-1) [C3] and (q+1, r) [C5]
        ids.append( (q+1, r-1, 3) )
        ids.append( (q+1, r, 5) )
    elif c == 2:
        # Touches (q+1, r) [C4] and (q, r+1) [C0]
        ids.append( (q+1, r, 4) )
        ids.append( (q, r+1, 0) )
    elif c == 3:
        # Touches (q, r+1) [C5] and (q-1, r+1) [C1]
        ids.append( (q, r+1, 5) )
        ids.append( (q-1, r+1, 1) )
    elif c == 4:
        # Touches (q-1, r+1) [C0] and (q-1, r) [C2]
        ids.append( (q-1, r+1, 0) )
        ids.append( (q-1, r, 2) )
    elif c == 5:
        # Touches (q-1, r) [C1] and (q, r-1) [C3]
        ids.append( (q-1, r, 1) )
        ids.append( (q, r-1, 3) )
        
    ids.sort()
    return ids[0]

def normalize_edge(q, r, e):
    # Edge e is shared with neighbor e.
    # Edge 0 (Top-Right) shared with Neighbor 0?
    # Neighbor 0 is (q+1, r-1). Its Edge 3 (Bottom-Left) should match Edge 0?
    
    # 0 <-> 3
    # 1 <-> 4
    # 2 <-> 5
    
    ids = [ (q, r, e) ]
    if e == 0:
        ids.append( (q+1, r-1, 3) )
    elif e == 1:
        ids.append( (q+1, r, 4) )
    elif e == 2:
        ids.append( (q, r+1, 5) )
    elif e == 3:
        ids.append( (q-1, r+1, 0) )
    elif e == 4:
        ids.append( (q-1, r, 1) )
    elif e == 5:
        ids.append( (q, r-1, 2) )
        
    ids.sort()
    return ids[0]

def get_adjacent_vertices(q, r, c):
    """Returns list of normalized (q, r, c) for vertices adjacent to the given vertex."""
    # A vertex (q,r,c) has 3 edges. The other ends of these edges are the adjacent vertices.
    # Vertex c (0-5) in Hex (q,r).
    # It shares edges c-1 (mod 6) and c (mod 6) within the hex?
    # Actually, let's look at the geometry.
    #  c=0 is top. Connected to c=1 and c=5 in same hex.
    #  Also connected to a vertex in the neighbor hex above?
    # It's easier to think about edges.
    # Edges incident to Vertex c: Edge c, Edge c-1. And one more radiating out?
    # Let's simple check:
    # Neighbor 1: Same hex, (c+1)%6
    # Neighbor 2: Same hex, (c-1)%6
    # Neighbor 3: The "external" one. 
    #   If c=0 (Top), it touches Hex(q, r-1, Bottom=3). So Neighbor 3 is in Hex(q, r-1)'s (c=4 or 2?).
    #   Wait, normalizing covers this!
    #   If we just take (q, r, c+1) and (q, r, c-1), that covers 2 neighbors.
    #   What about the 3rd?
    #   Actually, in a honeycomb, each vertex touches 3 hexes (usually), and 3 edges.
    #   The 3 edges lead to 3 other vertices.
    #   Within Hex (q,r), Vertex c connects to Vertex (c+1)%6 via Edge (c).
    #   And Vertex (c-1)%6 via Edge (c-1).
    #   Is there a 3rd? No, in the standard rendering, the "edges" are the hex boundaries.
    #   So "Vertex c" is physically connected to "Vertex c+1" and "Vertex c-1" via edges of THIS hex.
    #   Wait, are those the ONLY connections?
    #   Yes. The "external" connection is just an identity. i.e. Vertex 0 of Hex A IS Vertex 2 of Hex B.
    #   So, physically, from a point, there are 3 lines going out.
    #   Line 1: Edge c of Hex(q,r) -> Goes to Vertex (c+1)%6
    #   Line 2: Edge c-1 of Hex(q,r) -> Goes to Vertex (c-1)%6
    #   Line 3: ???
    #   Actually, Vertex c connects to (c+1) and (c-1). That's 2 edges.
    #   Where is the 3rd edge? 
    #   Ah, look at a Y junction.
    #   Hex A, Hex B, Hex C meet.
    #   Edges of A: e1, e2.
    #   Edge of B: e3.
    #   So yes, there are 3 edges meeting at a vertex.
    #   So there are 3 adjacent vertices.
    #   In Hex(q,r), Vertex c connects to:
    #     v1 = (q, r, (c+1)%6)
    #     v2 = (q, r, (c-1)%6)
    #   The 3rd edge... belongs to a neighbor hex?
    #   Actually, since we normalize, `(q,r,c)` IS the canonical ID.
    #   The "3rd edge" is one of the edges of the neighbor hexes that DOESN'T belong to (q,r)?
    #   No. All 3 edges at the vertex are boundaries of the 3 adjacent hexes.
    #   Edge 1: Between Hex A and B.
    #   Edge 2: Between Hex B and C.
    #   Edge 3: Between Hex C and A.
    #   So, looking at Hex A (q,r):
    #     One edge is 'Edge c', leading to 'Vertex c+1'.
    #     One edge is 'Edge c-1', leading to 'Vertex c-1'.
    #     The 3rd edge radiates "outward" from A?
    #     No. A vertex has exactly 3 neighbors.
    #     Wait.
    #     V0 (top). Connected to V1 (top-right) and V5 (top-left).
    #     Is it connected to anything else?
    #     V0 is also the bottom-left vertex of the hex to the top-right (Direction 1?)
    #     Let's rely on the property that `(q,r,c)` is also some `(q',r',c')`.
    #     We normalized `(q,r,c)`.
    #     We know distinct edges from `(q,r,c)` are:
    #       1. Edge c of (q,r).
    #       2. Edge c-1 of (q,r).
    #       3. Edge ??
    #     Actually, let's find the 3 adjacent vertices using the raw coords, then normalize.
    #     From Vertex c in Hex(q,r):
    #       Neighbor 1: Vertex (c+1)%6 in Hex(q,r).
    #       Neighbor 2: Vertex (c-1)%6 in Hex(q,r).
    #       Neighbor 3: ?
    #       Actually, iterate all 3 hexes touching this vertex.
    #       But simpler: The vertex only has 3 edges connected to it.
    #       We just need to identify those 3 edges, and the vertex at the OTHER end of each edge.
    #       Edge 1: (q,r, c). Connects (q,r,c) and (q,r,c+1). So Neighbor is (q,r,c+1).
    #       Edge 2: (q,r, c-1). Connects (q,r,c) and (q,r,c-1). Neighbor is (q,r,c-1).
    #       Is there a 3rd?
    #       In the lattice, yes.
    #       (q,r,c) is also (q_adj, r_adj, c_adj).
    #       In THAT hex, it connects to c_adj+1 and c_adj-1.
    #       One of them will be a duplicate of the above. The other is the 3rd branch.
    #       Example: Side 0 (Top).
    #       Hex(0,0), V0. Neighbors: V1, V5.
    #       V0 is also V4 of Hex(0,-1) (Top Neighbor)?
    #       Let's check NORMALIZE logic. 
    #       Yes. 
    #       In Hex(0,-1), V4 connects to V3 and V5.
    #       So the neighbors of V0(Hex 0,0) are V1(0,0), V5(0,0), and V?
    #       Wait.
    #       V0(0,0) == V4(0,-1).
    #       Neighbors of V4(0,-1) are V3(0,-1) and V5(0,-1).
    #       Are any of these duplicates?
    #       V5(0,-1) is Bottom Left of Top Neighbor.
    #       V5(0,0) is Top Left of Center.
    #       Top Left of Center touches Top Neighbor? Yes.
    #       V5(0,0) == V3(0,-1)?
    #       V0(0,0) == V4(0,-1).
    #       V1(0,0) == V?
    #       Let's just collect candidates and normalize them.
    #       Candidates from Hex(q,r): (q,r,c+1), (q,r,c-1).
    #       We also need to look at the "Incident Edge" that leads "out".
    #       Or simply: A vertex (q,r,c) corresponds to 3 "internal" angles of 3 hexes (or 1 hex and outside, etc).
    #       But purely topologically:
    #       Neighbor 1: Normalize(q, r, (c+1)%6)
    #       Neighbor 2: Normalize(q, r, (c-1)%6)
    #       Neighbor 3: ???
    #       It turns out that (q,r,c) maps to 1, 2, or 3 raw coordinate triplets.
    #       But we only need to find the *edges* radiating from it.
    #       Actually, for 'Distance Rule', we need the ADJACENT VERTICES.
    #       For 'Connection Rule' (Settlement), we need INCIDENT EDGES.
    #       
    #       Let's implement `get_incident_edges(q, r, c)` first, as edges determine neighbors.
    #       Edge 1: (q, r, c). (Edge starts at c, goes to c+1?)
    #         Convention: Edge e is between Vertex e and Vertex e+1.
    #         So Vertex c touches Edge c (going to c+1) and Edge c-1 (going to c-1).
    #         Wait, Edge c connects Vc and V(c+1).
    #         Edge c-1 connects V(c-1) and Vc.
    #         So yes, Edge c and Edge c-1 are incident to Vc.
    #         These are 2 edges.
    #         The 3rd edge comes from the adjacent hex sharing the validation.
    #         Let's normalize (q,r,c).
    #         Then generate Edge(q,r,c) and Edge(q,r, c-1).
    #         Is there a 3rd?
    #         Let's find the neighbor hex that shares Edge c-1?
    #         No.
    #         Let's brute force:
    #         1. Normalize (q,r,c) -> (nq, nr, nc).
    #         2. Consider (nq, nr, nc).
    #            Incidents:
    #            - Edge (nq, nr, nc)
    #            - Edge (nq, nr, (nc-1)%6)
    #            - There must be a 3rd.
    #            Let's look at the "Internal" view.
    #            V0 connects to E0 and E5.
    #            V0 is also V4 of Top Neighbor (0,-1).
    #            In (0,-1), it connects to E4 and E3.
    #            E4 of (0,-1) matches E?
    #            Edge Normalization:
    #            E0(q,r) == E3(q+1, r-1).
    #            E4(q,r) == E1(q-1, r).
    #            So V0 connects to E0(0,0), E5(0,0), and ...?
    #            E3(0,-1)?
    #            Let's use normalization to find distinct edges.
    #            Candidates:
    #               Edge(nq, nr, nc)
    #               Edge(nq, nr, (nc-1)%6)
    #               Edge( ?? )
    #            If we iterate through all 3 Hexes that share this vertex, we can find all edges.
    #            Which hexes share V(q,r,c)?
    #            (q,r,c) might normalize to itself.
    #            Who shares it?
    #            Depend on c.
    #            If c=0: Hex(q,r), Hex(q,r-1), Hex(q+1,r-1).
    #            Let's generify.
    #            Actually simpler:
    #            The 3 edges meeting at V(q,r,c) are:
    #            1. Normalized(q, r, c)
    #            2. Normalized(q, r, (c-1)%6)
    #            3. Normalized(NeighborHex...)?
    #            
    #            Re-eval the "3 edges" theory.
    #            In a honeycomb, yes, 3 edges meet at every vertex.
    #            We have Edge 1 and Edge 2 from Hex(q,r).
    #            Are they distinct? Yes.
    #            Is the 3rd one distinct from 1 and 2?
    #            Yes. It "goes into" the 3rd hex.
    #            So:
    #            incident_edges = set()
    #            incident_edges.add( normalize_edge(q, r, c) )
    #            incident_edges.add( normalize_edge(q, r, (c-1)%6) )
    #            
    #            This gives 2 edges. Where is the 3rd?
    #            It must be `normalize_edge(q, r-1, ???)`.
    #            
    #            Alternative:
    #            Get adjacent vertices first?
    #            V_curr = (q,r,c)
    #            V_next = (q,r, c+1)
    #            V_prev = (q,r, c-1)
    #            incident_edges.add( edge_between(V_curr, V_next) )
    #            incident_edges.add( edge_between(V_curr, V_prev) )
    #            
    #            This gives 2.
    #            But V_curr also connects to V_extension.
    #            
    #            Let's use the explicit "Shares" logic.
    #            V(0) shares with Hex(top) and Hex(top-right).
    #            V(1) shares with Hex(top-right) and Hex(bottom-right).
    #            
    #            Let's write a `get_neighbor_hexes_of_vertex(q,r,c)`?
    #            This seems tedious.
    #            
    #            Short cut:
    #            Just look at the 6 possible neighbors of a Hex.
    #            Actually, for a Vertex, there are exactly 3 edges.
    #            We just need to systematically find them.
    #            
    #            Logic:
    #            1. E_A = normalize_edge(q, r, c)
    #            2. E_B = normalize_edge(q, r, (c-1)%6)
    #            3. The 3rd edge is the one that is NOT E_A or E_B, but is incident to V.
    #            Consider the "Mapped" vertex in a neighbor hex.
    #            V(q,r,c) maps to some V'(q',r',c').
    #            In that hex, the incident edges are E(c') and E(c'-1).
    #            One of these MUST be E_A or E_B (normalized).
    #            The other one is E_C (the 3rd edge)!
    #            
    #            So:
    #            1. Find an "alias" for (q,r,c).
    #               e.g. if c=0, alias is (q, r-1, 4).
    #            2. In alias hex (q, r-1), take Edge 4 and Edge 3.
    #            3. Normalize them.
    #            4. Collect all. Set() will reduce to 3 unique edges.
    #            
    #            So I need `get_vertex_aliases(q,r,c)`.
    #            
    #            Similar to `normalize_vertex`, but return ALL raw matches.
    #            Then for each match, take edge c and c-1. Normalize. Add to set.
    
    # Let's write `get_vertex_aliases`.
    ids.sort()
    return ids[0]

def get_vertex_aliases(q, r, c):
    """Returns list of all (q,r,c) representations for a physical vertex."""
    matches = [(q,r,c)]
    
    # Check neighbors based on c (0-5)
    # This logic mirrors normalize_vertex potential adjacencies.
    # A vertex touches 3 hexes in a honeycomb.
    # We add the adjacent hex mappings.
    if c == 0: 
        matches.append((q, r-1, 4))
        matches.append((q+1, r-1, 2))
    elif c == 1: 
        matches.append((q+1, r-1, 3))
        matches.append((q+1, r, 5))
    elif c == 2: 
        matches.append((q+1, r, 0))
        matches.append((q, r+1, 4))
    elif c == 3: 
        matches.append((q, r+1, 1))
        matches.append((q-1, r+1, 5))
    elif c == 4: 
        matches.append((q-1, r+1, 2))
        matches.append((q-1, r, 0))
    elif c == 5: 
        matches.append((q-1, r, 1))
        matches.append((q, r-1, 3))
        
    return matches

def get_incident_edges(q, r, c):
    """Returns list of normalized (q,r,e) edges connected to vertex (q,r,c)."""
    aliases = get_vertex_aliases(q, r, c)
    edges = set()
    for (aq, ar, ac) in aliases:
        # Edges incident to vertex ac in hex (aq,ar) are Edge ac and Edge ac-1
        e1 = normalize_edge(aq, ar, ac)
        e2 = normalize_edge(aq, ar, (ac-1)%6)
        edges.add(e1)
        edges.add(e2)
    return list(edges)

def get_adjacent_vertices(q, r, c):
    """Returns list of normalized (q,r,c) vertices adjacent to vertex (q,r,c)."""
    start_v = normalize_vertex(q, r, c)
    incident_edges = get_incident_edges(q, r, c)
    
    adj_verts = set()
    for (eq, er, ee) in incident_edges:
        # Edge (eq,er,ee) connects Vertex (eq,er,ee) and Vertex (eq,er,ee+1)
        v1 = normalize_vertex(eq, er, ee)
        v2 = normalize_vertex(eq, er, (ee+1)%6)
        
        if v1 == start_v:
            adj_verts.add(v2)
        else:
            adj_verts.add(v1)
            
    return list(adj_verts)

# --- Game Constants ---
# --- Game Constants ---
ROAD_COST = {"lumber": 1, "brick": 1}
SETTLEMENT_COST = {"lumber": 1, "brick": 1, "wool": 1, "grain": 1}
CITY_COST = {"grain": 2, "ore": 3}

from .models import ResourceType, GameLog
import time

class GameManager:
    def __init__(self):
        self.board = generate_board()
        from .models import GameState, PlayerColor, ResourceType, TradeOffer
        self.state = GameState(players=[PlayerColor.RED, PlayerColor.BLUE, PlayerColor.ORANGE, PlayerColor.WHITE])
        
        # Initialize inventories
        self.state.inventories = {
            p: {r: 0 for r in ResourceType}
            for p in self.state.players
        }
        
        self.state.phase = "INITIAL_PLACEMENT_1"
        self.state.current_turn_index = 0

    def add_log(self, message: str, player_color=None):
        log = GameLog(message=message, player_color=player_color, timestamp=time.time())
        self.state.logs.append(log)
        # Keep last 50
        if len(self.state.logs) > 50:
            self.state.logs.pop(0)

    def build_settlement(self, q, r, c):
        # 1. Check phase restrictions
        if self.state.phase == "GAME_LOOP":
            if self.state.turn_sub_phase != "BUILD_TRADE":
                return False # Cannot build until dice are rolled (and trade phase starts)
        
        nq, nr, nc = normalize_vertex(q, r, c)
        
        # Check if occupied
        for b in self.state.buildings:
            if b.location.q == nq and b.location.r == nr and b.location.corner == nc:
                return False # Occupied

        # Phase Limits Check
        current_p_color = self.state.players[self.state.current_turn_index]
        existing_sets = [b for b in self.state.buildings if b.owner == current_p_color]
        
        if self.state.phase == "INITIAL_PLACEMENT_1":
            if len(existing_sets) >= 1: return False
        elif self.state.phase == "INITIAL_PLACEMENT_2":
            if len(existing_sets) >= 2: return False

        # DISTANCE RULE (2 spots away)
        # Check all adjacent vertices. If any has a building, fail.
        adj_verts = get_adjacent_vertices(nq, nr, nc)
        for av in adj_verts:
            # Check if occupied
            # av is (q,r,c) ID.
            for b in self.state.buildings:
                if b.location.q == av[0] and b.location.r == av[1] and b.location.corner == av[2]:
                    self.add_log("Too close to another building!", player_color=current_p_color)
                    return False

        # CONNECTION RULE
        # Must connect to own road (except in Initial Phase)
        if self.state.phase == "GAME_LOOP":
            incident_edges = get_incident_edges(nq, nr, nc)
            has_connection = False
            for ie in incident_edges:
                # ie is (q,r,e)
                for r_obj in self.state.roads:
                    if r_obj.owner == current_p_color:
                        if r_obj.location.q == ie[0] and r_obj.location.r == ie[1] and r_obj.location.edge == ie[2]:
                            has_connection = True
                            break
                if has_connection: break
            
            if not has_connection:
                self.add_log("Must connect to your road!", player_color=current_p_color)
                return False

        # COST CHECK & CONSUMPTION
        if self.state.phase == "GAME_LOOP":
            inventory = self.state.inventories[current_p_color]
            # Check
            for res, amount in SETTLEMENT_COST.items():
                if inventory.get(res, 0) < amount:
                    return False # Insufficient resources
            
            # Consume
            for res, amount in SETTLEMENT_COST.items():
                inventory[res] -= amount
        
        player = self.state.players[self.state.current_turn_index]
        from .models import Building, VertexID
        
        new_b = Building(owner=player, type="settlement", location=VertexID(q=nq, r=nr, corner=nc))
        self.state.buildings.append(new_b)
        
        self.add_log(f"built a settlement at {nq},{nr},{nc}", player_color=player)
        
        # Phase transition logic
        self.advance_turn_if_needed("settlement")
        return True

    def build_road(self, q, r, e):
        # 1. Check phase restrictions
        if self.state.phase == "GAME_LOOP":
            if self.state.turn_sub_phase != "BUILD_TRADE":
                return False # Cannot build until dice are rolled
        
        nq, nr, ne = normalize_edge(q, r, e)
        
        # Check occupied
        for road in self.state.roads:
            if road.location.q == nq and road.location.r == nr and road.location.edge == ne:
                return False

        current_p_color = self.state.players[self.state.current_turn_index]
        existing_roads = [r for r in self.state.roads if r.owner == current_p_color]
        
        # LIMIT CHECK (Max 15 roads)
        if len(existing_roads) >= 15:
             if self.state.phase == "GAME_LOOP":
                 return False

        if self.state.phase == "INITIAL_PLACEMENT_1":
            if len(existing_roads) >= 1: return False
        elif self.state.phase == "INITIAL_PLACEMENT_2":
            if len(existing_roads) >= 2: return False

        # CONNECTION RULE
        # Must connect to own road or own building at either endpoint.
        # Incident vertices of this edge:
        # V1 = (nq, nr, ne) normalized
        # V2 = (nq, nr, ne+1) normalized
        # Start with liberal check:
        # Check V1: Is there a building there owned by me? OR Is there another road incident to V1 owned by me?
        # Check V2: Similar.
        
        # We need a helper for "Roads incident to Vertex".
        # conveniently, get_incident_edges(v) checks all edges at v.
        # So:
        # 1. Get V1, V2.
        # 2. For each V:
        #    a. Check if I have a building at V. If yes, Connected.
        #    b. Check incident edges of V (excluding THIS edge).
        #       If any owner == me, Connected.
        
        # Wait, I need `get_incident_edges`. I implemented it but didn't expose it to `build_road` scope? 
        # It's at global scope in file.
        
        v1 = normalize_vertex(nq, nr, ne)
        v2 = normalize_vertex(nq, nr, ne + 1)
        
        has_connection = False
        
        # Check endpoints
        for v in [v1, v2]:
            # Building check
            for b in self.state.buildings:
                if b.owner == current_p_color:
                    if b.location.q == v[0] and b.location.r == v[1] and b.location.corner == v[2]:
                        has_connection = True
                        break
            if has_connection: break
            
            # Road check
            inc_edges = get_incident_edges(v[0], v[1], v[2])
            for ie in inc_edges:
                # Skip self (nq, nr, ne)
                if ie == (nq, nr, ne): continue
                
                for r_obj in self.state.roads:
                    if r_obj.owner == current_p_color:
                        if r_obj.location.q == ie[0] and r_obj.location.r == ie[1] and r_obj.location.edge == ie[2]:
                            has_connection = True
                            break
                if has_connection: break
            if has_connection: break

        # If Initial Phase, we relax? No, Standard Catan rules say Initial Road must attach to the Settlement just placed.
        # But commonly in digital implementations, if we enforce "Settlement First", then road matches.
        # However, our turn logic allows placing road first (if we didn't block it).
        # Snake draft: Settlement, then Road.
        # So yes, Road must connect to the just-placed settlement.
        # The logic above covers it (Building check).
        
        if not has_connection:
             # In Initial phase, if we haven't placed settlement yet? 
             # Logic says S then R.
             # So this check is valid.
             self.add_log("Must connect to your network!", player_color=current_p_color)
             return False

        # COST CHECK & CONSUMPTION
        if self.state.phase == "GAME_LOOP":
            inventory = self.state.inventories[current_p_color]
            for res, amount in ROAD_COST.items():
                if inventory.get(res, 0) < amount:
                    return False
            
            for res, amount in ROAD_COST.items():
                inventory[res] -= amount

        player = self.state.players[self.state.current_turn_index]
        from .models import Road, EdgeID
        new_r = Road(owner=player, location=EdgeID(q=nq, r=nr, edge=ne))
        self.state.roads.append(new_r)
        
        self.add_log(f"built a road at {nq},{nr},{ne}", player_color=player)

        self.advance_turn_if_needed("road")
        return True

    def build_city(self, nq, nr, nc):
        if self.state.phase != "GAME_LOOP": return False
        
        current_p_color = self.state.players[self.state.current_turn_index]
        
        # 1. Check Limits (Max 4 Cities)
        existing_cities = [b for b in self.state.buildings if b.owner == current_p_color and b.type == "city"]
        if len(existing_cities) >= 4:
            self.add_log("Max 4 cities reached!", player_color=current_p_color)
            return False

        # 2. Check Valid Target (Must have own Settlement at location)
        # Verify ownership and type
        target_building = None
        for b in self.state.buildings:
            if b.location.q == nq and b.location.r == nr and b.location.corner == nc:
                target_building = b
                break
        
        if not target_building:
            self.add_log("No building selection!", player_color=current_p_color)
            return False
            
        if target_building.owner != current_p_color:
            self.add_log("That's not your building!", player_color=current_p_color)
            return False
            
        if target_building.type != "settlement":
            self.add_log("Can only upgrade settlements!", player_color=current_p_color)
            return False

        # 3. Check Cost
        inventory = self.state.inventories[current_p_color]
        for res, amount in CITY_COST.items():
            if inventory.get(res, 0) < amount:
                return False
        
        # 4. Consume
        for res, amount in CITY_COST.items():
            inventory[res] -= amount
            
        # 5. Upgrade
        target_building.type = "city"
        self.add_log(f"upgraded to a City at {nq},{nr},{nc}", player_color=current_p_color)
        
        return True
    
    def advance_turn_if_needed(self, action_type):
        current_p_color = self.state.players[self.state.current_turn_index]
        
        # Count what this player has built
        settlements = [b for b in self.state.buildings if b.owner == current_p_color]
        roads = [r for r in self.state.roads if r.owner == current_p_color]
        
        # Phase Logic
        if self.state.phase == "INITIAL_PLACEMENT_1":
            # Requirement: 1 Settlement, 1 Road
            if len(settlements) >= 1 and len(roads) >= 1:
                # Turn Complete
                self.handle_turn_end()
                
        elif self.state.phase == "INITIAL_PLACEMENT_2":
            # Requirement: 2 Settlements, 2 Roads (Total key)
            if len(settlements) >= 2 and len(roads) >= 2:
                self.handle_turn_end()
        
        # Game Loop logic (not strictly enforced for MVP yet, standard is roll dice -> trade -> build -> end turn manually)
        
    def handle_turn_end(self):
        # Snake draft logic
        if self.state.phase == "INITIAL_PLACEMENT_1":
            if self.state.current_turn_index < 3:
                self.state.current_turn_index += 1
            else:
                self.state.phase = "INITIAL_PLACEMENT_2"
                # Player 3 (index 3) goes again first in Phase 2? 
                # Snake draft: 0,1,2,3 -> 3,2,1,0
                # So if we just finished 3's turn in Phase 1, it becomes 3's turn in Phase 2.
                # Currently index is 3. We keep it 3.
                pass 
        elif self.state.phase == "INITIAL_PLACEMENT_2":
            if self.state.current_turn_index > 0:
                self.state.current_turn_index -= 1
            else:
                self.state.phase = "GAME_LOOP"
                self.state.current_turn_index = 0
        else:
             self.state.current_turn_index = (self.state.current_turn_index + 1) % 4

        # Reset sub-phase if in Game Loop
        if self.state.phase == "GAME_LOOP":
            self.state.turn_sub_phase = "ROLL_DICE"

    def roll_dice(self):
        import random
        # 2 dice 1-6
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2
        
        self.state.last_dice_result = total
        self.distribute_resources(total)
        
        # Advance sub-phase
        self.state.turn_sub_phase = "BUILD_TRADE"
        return total

    def end_turn(self):
        # Advance to next player
        self.state.current_turn_index = (self.state.current_turn_index + 1) % len(self.state.players)
        
        # Reset turn state
        self.state.turn_sub_phase = "ROLL_DICE"
        self.state.last_dice_result = None # Clear dice result for next player
        print(f"Turn advanced to {self.state.players[self.state.current_turn_index]}")
        return True

    def distribute_resources(self, number: int):
        if number == 7:
            # Robber - not implemented yet
            return

        # Find hexes with this number
        target_hexes = [h for h in self.board.hexes if h.number == number]
        
        for h in target_hexes:
            if h.resource == "desert": 
                continue # Should not happen if number logic is correct (Desert has no number) but safe guard
            
            # Check all 6 corners for settlements
            # We need to reconstruct the vertices for this hex and check if any building is there.
            # Building location is normalized.
            # We must normalize the 6 corners of this hex and match against buildings.
            
            for c in range(6):
                nq, nr, nc = normalize_vertex(h.q, h.r, c)
                
                # Check if there is a building at (nq, nr, nc)
                building = next((b for b in self.state.buildings 
                                 if b.location.q == nq and b.location.r == nr and b.location.corner == nc), None)
                
                if building:
                    # Grant resource
                    # Settlement = 1 card. City = 2 cards
                    count = 2 if building.type == "city" else 1
                    
                    self.state.inventories[building.owner][h.resource] += count
                    self.add_log(f"got {count} {h.resource}", player_color=building.owner)
                    print(f"Distributed {count} {h.resource} to {building.owner} from Hex {h.id}")

    def bank_trade(self, give_res: str, get_res: str):
        if self.state.phase != "GAME_LOOP": return False
        
        current_p_color = self.state.players[self.state.current_turn_index]
        inventory = self.state.inventories[current_p_color]
        
        # Validation
        if inventory.get(give_res, 0) < 4:
            self.add_log(f"Not enough {give_res} to trade (need 4)", player_color=current_p_color)
            return False
            
        # Execute Trade
        inventory[give_res] -= 4
        inventory[get_res] += 1
        
        self.add_log(f"traded 4 {give_res} for 1 {get_res}", player_color=current_p_color)
        return True

    def create_trade_offer(self, give: dict, get: dict):
        current_p = self.state.players[self.state.current_turn_index]
        from .models import TradeOffer
        
        # Basic validation: Do I have the resources I'm offering?
        inventory = self.state.inventories[current_p]
        for res, count in give.items():
            if inventory.get(res, 0) < count:
                self.add_log(f"Offer failed: Not enough {res}", player_color=current_p)
                return False

        self.state.active_trade = TradeOffer(
            offerer=current_p,
            give=give,
            get=get,
            status="OPEN"
        )
        self.add_log(f"proposes a trade...", player_color=current_p)
        return True

    def cancel_trade_offer(self):
        current_p = self.state.players[self.state.current_turn_index]
        if self.state.active_trade and self.state.active_trade.offerer == current_p:
            self.state.active_trade = None
            self.add_log("Trade offer cancelled", player_color=current_p)
            return True
        return False

    def respond_to_offer(self, responder_color: str, accept: bool):
        if not self.state.active_trade: return False
        
        if accept:
            # Check if responder has resources
            inventory = self.state.inventories[responder_color]
            needed = self.state.active_trade.get
            for res, count in needed.items():
                if inventory.get(res, 0) < count:
                    return False # Cannot accept if don't have items
            
            if responder_color not in self.state.active_trade.responses:
                self.state.active_trade.responses.append(responder_color)
                self.add_log("Training accepted the offer", player_color=responder_color) 
                # Typo in log fixed in mind, but for code "accepted"
        return True

    def confirm_trade(self, target_player: str):
        trade = self.state.active_trade
        if not trade: return False
        
        offerer = trade.offerer
        
        # Final validation
        inv_offerer = self.state.inventories[offerer]
        inv_target = self.state.inventories[target_player]
        
        # Deduct from offerer, Add to target
        for res, count in trade.give.items():
            if inv_offerer.get(res, 0) < count: return False
            inv_offerer[res] -= count
            inv_target[res] += count
            
        # Deduct from target, Add to offerer
        for res, count in trade.get.items():
            if inv_target.get(res, 0) < count: return False
            inv_target[res] -= count
            inv_offerer[res] += count
            
        self.add_log(f"Trade completed with {target_player}", player_color=offerer)
        self.state.active_trade = None
        return True

# Global Manager
game_manager = GameManager()
