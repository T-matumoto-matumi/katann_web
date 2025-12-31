import React from 'react';
import type { GameState } from '../types';

interface ControlsProps {
    gameState: GameState;
    onRollDice: () => void;
    onEndTurn?: () => void;
    onSetBuildMode?: (mode: 'road' | 'settlement' | 'city' | null) => void;
    onTestResources?: () => void;
}

export const Controls: React.FC<ControlsProps> = (props) => {
    const { gameState, onRollDice } = props;
    // Determine if actions are allowed
    const isGameLoop = gameState.phase === "GAME_LOOP";
    const subPhase = gameState.turn_sub_phase;
    const canRoll = isGameLoop && (subPhase === "ROLL_DICE" || !subPhase); // Default to roll if null for safety

    const myColor = gameState.players[gameState.current_turn_index]; // Assumption: client will identify itself later. For now, strictly UI based.
    const myInventory = gameState.inventories[myColor] || {};

    const canBuildRoad = (myInventory['lumber'] >= 1 && myInventory['brick'] >= 1);
    const canBuildSettlement = (myInventory['lumber'] >= 1 && myInventory['brick'] >= 1 && myInventory['wool'] >= 1 && myInventory['grain'] >= 1);
    const canBuildCity = (myInventory['grain'] >= 2 && myInventory['ore'] >= 3);

    return (
        <div className="absolute top-4 right-4 z-50 flex flex-col items-end gap-2">
            {/* Dice Result Display */}
            {gameState.last_dice_result !== null && (
                <div className="bg-black/70 text-white p-4 rounded-xl text-4xl font-bold shadow-lg animate-bounce">
                    🎲 {gameState.last_dice_result}
                </div>
            )}

            {/* Roll Button */}
            {canRoll && (
                <button
                    onClick={onRollDice}
                    className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg text-lg transition-transform active:scale-95"
                >
                    Roll Dice 🎲
                </button>
            )}

            {/* Build / End Turn Actions */}
            {!canRoll && isGameLoop && (
                <div className="flex flex-col gap-2 items-end">
                    <div className="bg-white/90 p-2 rounded-lg flex flex-col gap-2 text-sm font-semibold shadow-md">
                        <div className="text-gray-700 border-b pb-1 mb-1">Actions</div>

                        <button
                            onClick={() => props.onSetBuildMode && props.onSetBuildMode('road')}
                            disabled={!canBuildRoad}
                            className={`px-3 py-2 rounded flex justify-between gap-2 border ${canBuildRoad ? 'bg-amber-100 border-amber-300 hover:bg-amber-200 text-amber-900' : 'bg-gray-100 text-gray-400 cursor-not-allowed'}`}
                        >
                            <span>Build Road</span>
                            <span className="text-xs font-normal opacity-70">🌲🧱</span>
                        </button>

                        <button
                            onClick={() => props.onSetBuildMode && props.onSetBuildMode('settlement')}
                            disabled={!canBuildSettlement}
                            className={`px-3 py-2 rounded flex justify-between gap-2 border ${canBuildSettlement ? 'bg-orange-100 border-orange-300 hover:bg-orange-200 text-orange-900' : 'bg-gray-100 text-gray-400 cursor-not-allowed'}`}
                        >
                            <span>Build Settlement</span>
                            <span className="text-xs font-normal opacity-70">🌲🧱🐑🌾</span>
                        </button>

                        <button
                            onClick={() => props.onSetBuildMode && props.onSetBuildMode('city')}
                            disabled={!canBuildCity}
                            className={`px-3 py-2 rounded flex justify-between gap-2 border ${canBuildCity ? 'bg-purple-100 border-purple-300 hover:bg-purple-200 text-purple-900' : 'bg-gray-100 text-gray-400 cursor-not-allowed'}`}
                        >
                            <span>Build City</span>
                            <span className="text-xs font-normal opacity-70">🌾🌾🪨🪨🪨</span>
                        </button>
                    </div>

                    <button
                        onClick={() => props.onEndTurn && props.onEndTurn()}
                        className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded shadow transition-colors"
                    >
                        End Turn ➡️
                    </button>
                </div>
            )}
        </div>
    );
};
