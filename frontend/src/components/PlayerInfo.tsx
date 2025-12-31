import React from 'react';
import { PlayerColor, ResourceType } from '../types';
import type { GameState } from '../types';

interface PlayerInfoProps {
    gameState: GameState;
    myColor?: PlayerColor; // Future use if we identify 'me'
}

const playerHexColors: Record<PlayerColor, string> = {
    [PlayerColor.RED]: '#EF4444',
    [PlayerColor.BLUE]: '#3B82F6',
    [PlayerColor.ORANGE]: '#F97316',
    [PlayerColor.WHITE]: '#F8FAFC',
};

export const PlayerInfo: React.FC<PlayerInfoProps> = ({ gameState }) => {
    return (
        <div className="absolute bottom-4 left-4 right-4 z-50 flex justify-between gap-4 pointer-events-none">
            {gameState.players.map(p => {
                const inv = gameState.inventories[p] || {};
                const totalCards = Object.values(inv).reduce((a, b) => a + b, 0);
                const isCurrentTurn = p === gameState.players[gameState.current_turn_index];

                return (
                    <div
                        key={p}
                        className={`bg-white/90 p-3 rounded-lg shadow-md pointer-events-auto min-w-[150px]
                            ${isCurrentTurn ? 'ring-4 ring-yellow-400' : ''}
                        `}
                    >
                        <div className="flex items-center gap-2 mb-2 border-b pb-1">
                            <div className="w-4 h-4 rounded-full" style={{ backgroundColor: playerHexColors[p], border: p === PlayerColor.WHITE ? '1px solid black' : 'none' }}></div>
                            <span className="font-bold capitalize">{p}</span>
                            <span className="ml-auto text-sm bg-gray-200 px-2 rounded-full">{totalCards} cards</span>
                        </div>

                        {/* Resource Breakdown */}
                        <div className="grid grid-cols-5 gap-1 text-xs text-center">
                            {Object.entries(ResourceType).map(([, res]) => (
                                <div key={res} className="flex flex-col items-center">
                                    {/* Resource Emoji */}
                                    <div className="text-lg mb-1" title={res}>
                                        {res === 'brick' ? '🧱' :
                                            res === 'lumber' ? '🌲' :
                                                res === 'wool' ? '🐑' :
                                                    res === 'grain' ? '🌾' :
                                                        res === 'ore' ? '🪨' : '❓'}
                                    </div>
                                    <span className="font-bold">{inv[res] || 0}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
