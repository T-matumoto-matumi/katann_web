export interface UnifiedVertexID {
    q: number;
    r: number;
    c: number;
    id: string; // "q,r,c"
}

export interface UnifiedEdgeID {
    q: number;
    r: number;
    e: number;
    id: string; // "q,r,e"
}

export function normalizeVertex(q: number, r: number, c: number): UnifiedVertexID {
    const ids = [{ q, r, c }];

    if (c === 0) {
        ids.push({ q, r: r - 1, c: 2 });
        ids.push({ q: q + 1, r: r - 1, c: 4 });
    } else if (c === 1) {
        ids.push({ q: q + 1, r: r - 1, c: 3 });
        ids.push({ q: q + 1, r, c: 5 });
    } else if (c === 2) {
        ids.push({ q: q + 1, r, c: 4 });
        ids.push({ q, r: r + 1, c: 0 });
    } else if (c === 3) {
        ids.push({ q, r: r + 1, c: 5 });
        ids.push({ q: q - 1, r: r + 1, c: 1 });
    } else if (c === 4) {
        ids.push({ q: q - 1, r: r + 1, c: 0 });
        ids.push({ q: q - 1, r, c: 2 });
    } else if (c === 5) {
        ids.push({ q: q - 1, r, c: 1 });
        ids.push({ q, r: r - 1, c: 3 });
    }

    // Sort by q, then r, then c to pick canonical
    ids.sort((a, b) => {
        if (a.q !== b.q) return a.q - b.q;
        if (a.r !== b.r) return a.r - b.r;
        return a.c - b.c;
    });

    const canonical = ids[0];
    return { ...canonical, id: `${canonical.q},${canonical.r},${canonical.c}` };
}

export function normalizeEdge(q: number, r: number, e: number): UnifiedEdgeID {
    const ids = [{ q, r, e }];

    if (e === 0) ids.push({ q: q + 1, r: r - 1, e: 3 });
    else if (e === 1) ids.push({ q: q + 1, r, e: 4 });
    else if (e === 2) ids.push({ q, r: r + 1, e: 5 });
    else if (e === 3) ids.push({ q: q - 1, r: r + 1, e: 0 });
    else if (e === 4) ids.push({ q: q - 1, r, e: 1 });
    else if (e === 5) ids.push({ q, r: r - 1, e: 2 });

    ids.sort((a, b) => {
        if (a.q !== b.q) return a.q - b.q;
        if (a.r !== b.r) return a.r - b.r;
        return a.e - b.e;
    });

    const canonical = ids[0];
    return { ...canonical, id: `${canonical.q},${canonical.r},${canonical.e}` };
}
