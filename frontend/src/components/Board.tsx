
import React, { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';
import type { BoardData, GameState as GameStateType } from '../types';
import { Hexagon } from './Hexagon';
import { VertexNode } from './VertexNode';
import { EdgeLine } from './EdgeLine';
import { PlayerInfo } from './PlayerInfo';
import { Controls } from './Controls';
// import { TradePanel } from './TradePanel';
import { normalizeVertex, normalizeEdge } from '../utils/coords';

const SOCKET_URL = 'http://localhost:8000'; // Or generic / if proxied

export const Board: React.FC = () => {
    const [boardData, setBoardData] = useState<BoardData | null>(null);
    const [gameState, setGameState] = useState<GameStateType | null>(null);
    const [connectionStatus, setConnectionStatus] = useState('Connecting...');
    const [containerWidth, setContainerWidth] = useState(window.innerWidth);
    const [buildMode, setBuildMode] = useState<'road' | 'settlement' | 'city' | null>(null);

    // Socket ref to emit events
    const socketRef = useRef<any>(null);

    useEffect(() => {
        const socket = io(SOCKET_URL, {
            transports: ['websocket', 'polling']
        });
        socketRef.current = socket;

        socket.on('connect', () => {
            console.log('Connected to server');
            setConnectionStatus('Connected!');
        });

        socket.on('connect_error', (err) => {
            console.error('Connection error:', err);
            setConnectionStatus(`Error: ${err.message} `);
        });

        socket.on('board_state', (data: BoardData) => {
            setBoardData(data);
        });

        socket.on('game_state', (data: GameStateType) => {
            console.log('Game State:', data);
            setGameState(data);
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    useEffect(() => {
        const handleResize = () => setContainerWidth(window.innerWidth);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    if (!boardData) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 text-black">
                <div className="text-xl font-bold mb-2">Loading Catan...</div>
                <div className="text-sm text-gray-600">Status: {connectionStatus}</div>
            </div>
        );
    }

    // ... layout calculation ...

    // (This part is tricky with replace_file_content if I want to keep the middle part. 
    // I will just replace the top import and hook section, and then inject the components in the return)
    // Actually, I can just replace the whole file content chunk by chunk or be careful.
    // The previous `replace_file_content` replaced lines 1 to 140 (wait, no example).

    // Let's assume I replace the imports and the handle functions first.

    const displayWidth = Math.min(containerWidth, 800) * 0.95;
    const hexSize = displayWidth / (5 * Math.sqrt(3));
    const boardHeight = 6 * hexSize + 2 * hexSize;

    // Helper to get pixel coordinates of a hex center
    const getHexCenter = (q: number, r: number) => {
        const x = hexSize * (Math.sqrt(3) * q + Math.sqrt(3) / 2 * r);
        const y = hexSize * (3.0 / 2 * r);
        return { x, y };
    }

    // Generate renderable vertices and edges
    const uniqueVertices = new Map<string, { q: number, r: number, c: number, x: number, y: number }>();
    const uniqueEdges = new Map<string, { q: number, r: number, e: number, x: number, y: number, rotation: number }>();

    if (boardData) {
        boardData.hexes.forEach(hex => {
            const center = getHexCenter(hex.q, hex.r);

            // Vertices
            for (let c = 0; c < 6; c++) {
                const canonical = normalizeVertex(hex.q, hex.r, c);
                if (!uniqueVertices.has(canonical.id)) {
                    // Calculate position for vertex c
                    // Angle: -90 for c0 (Top), -30 for c1, etc. -> -90 + c * 60
                    const angle_rad = (Math.PI / 180) * (-90 + c * 60);
                    const vx = center.x + hexSize * Math.cos(angle_rad);
                    const vy = center.y + hexSize * Math.sin(angle_rad);

                    uniqueVertices.set(canonical.id, {
                        q: canonical.q, r: canonical.r, c: canonical.c,
                        x: vx, y: vy
                    });
                }
            }

            // Edges
            for (let e = 0; e < 6; e++) {
                const canonical = normalizeEdge(hex.q, hex.r, e);
                if (!uniqueEdges.has(canonical.id)) {
                    const angle_mid_rad = (Math.PI / 180) * (-60 + e * 60);
                    const dist = hexSize * (Math.sqrt(3) / 2);
                    const ex = center.x + dist * Math.cos(angle_mid_rad);
                    const ey = center.y + dist * Math.sin(angle_mid_rad);
                    const rotation = 30 + e * 60;

                    uniqueEdges.set(canonical.id, {
                        q: canonical.q, r: canonical.r, e: canonical.e,
                        x: ex, y: ey, rotation
                    });
                }
            }
        });
    }

    const handleVertexClick = (v: { q: number, r: number, c: number }) => {
        // Validation: Can only build if it's my turn (and phase allows)
        if (gameState?.phase === 'GAME_LOOP') {
            if (gameState?.turn_sub_phase === 'ROLL_DICE') {
                console.log("Cannot build, roll dice first!");
                return;
            }

            // Check Build Mode
            if (buildMode === 'city') {
                // Check logic: Must have own settlement here.
                // We can rely on backend, but for UI feedback:
                // Actually we should just emit if confirmed.
                // Use window.confirm for mobile friendliness (user requirement)
                const confirm = window.confirm("Upgrade this settlement to a City? (Cost: 🌾🌾🪨🪨🪨)");
                if (confirm) {
                    socketRef.current?.emit('build_city', { q: v.q, r: v.r, corner: v.c });
                    setBuildMode(null);
                }
                return;
            }

            if (buildMode === 'settlement') {
                socketRef.current?.emit('build_settlement', { q: v.q, r: v.r, corner: v.c });
                setBuildMode(null);
            }
        } else {
            // Initial Phase
            socketRef.current?.emit('build_settlement', { q: v.q, r: v.r, corner: v.c });
        }
    };

    const handleEdgeClick = (e: { q: number, r: number, edge: number }) => {
        if (gameState?.phase === 'GAME_LOOP') {
            if (gameState?.turn_sub_phase === 'ROLL_DICE') {
                console.log("Cannot build, roll dice first!");
                return;
            }
            if (buildMode !== 'road') {
                return;
            }
            socketRef.current?.emit('build_road', { q: e.q, r: e.r, edge: e.edge });
            setBuildMode(null);
        } else {
            socketRef.current?.emit('build_road', { q: e.q, r: e.r, edge: e.edge });
        }
    };

    const handleRollDice = () => {
        socketRef.current?.emit('roll_dice');
    };

    const handleEndTurn = () => {
        socketRef.current?.emit('end_turn');
        setBuildMode(null);
    };

    const handleTestResources = () => {
        socketRef.current?.emit('test_resources');
    };

    // Trade Handlers Removed



    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-blue-300 overflow-hidden relative">
            {/* HUD Layer */}
            <div className="absolute top-4 left-4 z-50 bg-white/80 p-4 rounded shadow pointer-events-none">
                <div className="pointer-events-auto">
                    <h1 className="text-xl font-bold">Catan</h1>
                    {gameState && (
                        <div>
                            <div>Turn: <span className={`font-bold text-${gameState.players[gameState.current_turn_index]}-600`}>
                                {gameState.players[gameState.current_turn_index]}
                            </span></div>
                            <div>Phase: {gameState.phase}</div>
                        </div>
                    )}
                </div>
            </div>

            {gameState && (
                <>
                    <Controls
                        gameState={gameState}
                        onRollDice={handleRollDice}
                        onEndTurn={handleEndTurn}
                        onSetBuildMode={setBuildMode}
                        onTestResources={handleTestResources}
                    />
                    <PlayerInfo gameState={gameState} />





                    {/* Game Logs */}
                    <div className="absolute top-20 left-4 z-40 bg-black/50 text-white p-2 rounded max-h-48 overflow-y-auto w-64 text-xs pointer-events-none">
                        {gameState.logs && gameState.logs.slice().reverse().map((log, i) => (
                            <div key={i} className="mb-1 border-b border-white/20 pb-1">
                                <span className="font-bold capitalize text-yellow-300">{log.player_color || 'System'}: </span>
                                <span>{log.message}</span>
                            </div>
                        ))}
                    </div>

                    {/* Build Mode Indicator */}
                    {buildMode && (
                        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-50 bg-yellow-400 text-black px-4 py-2 rounded-full font-bold shadow-lg animate-pulse pointer-events-none">
                            BUILD MODE: Click to place {buildMode.toUpperCase()}
                        </div>
                    )}
                </>
            )}

            <div
                className="relative"
                style={{ width: displayWidth, height: boardHeight }}
            >
                {/* Center point */}
                <div className="absolute top-1/2 left-1/2 w-0 h-0">
                    {/* Hexes */}
                    {boardData.hexes.map((hex) => {
                        const { x, y } = getHexCenter(hex.q, hex.r);
                        return (
                            <Hexagon
                                key={hex.id}
                                x={x}
                                y={y}
                                size={hexSize * 0.95}
                                resource={hex.resource}
                                number={hex.number}
                            />
                        );
                    })}

                    {/* Edges */}
                    {/* Vertices */}
                    {/* (I'll keep the existing Edge/Vertex mapping logic below this replacement block) */}


                    {/* Edges */}
                    {Array.from(uniqueEdges.values()).map((edge) => {
                        const road = gameState?.roads.find(r =>
                            r.location.q === edge.q &&
                            r.location.r === edge.r &&
                            r.location.edge === edge.e
                        );

                        return (
                            <EdgeLine
                                key={`e-${edge.q}-${edge.r}-${edge.e}`}
                                x={edge.x}
                                y={edge.y}
                                rotation={edge.rotation}
                                length={hexSize}
                                road={road}
                                onClick={() => handleEdgeClick({ q: edge.q, r: edge.r, edge: edge.e })}
                            />
                        );
                    })}

                    {/* Vertices */}
                    {Array.from(uniqueVertices.values()).map((vert) => {
                        const building = gameState?.buildings.find(b =>
                            b.location.q === vert.q &&
                            b.location.r === vert.r &&
                            b.location.corner === vert.c
                        );

                        return (
                            <VertexNode
                                key={`v-${vert.q}-${vert.r}-${vert.c}`}
                                x={vert.x}
                                y={vert.y}
                                building={building}
                                onClick={() => handleVertexClick({ q: vert.q, r: vert.r, c: vert.c })}
                            />
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

