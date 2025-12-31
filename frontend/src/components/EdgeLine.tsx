import React from 'react';
import { PlayerColor } from '../types';
import type { Road } from '../types';

interface EdgeLineProps {
    x: number;
    y: number;
    rotation: number; // degrees
    length: number;
    road?: Road;
    onClick: () => void;
}

const playerColors: Record<PlayerColor, string> = {
    [PlayerColor.RED]: '#EF4444',
    [PlayerColor.BLUE]: '#3B82F6',
    [PlayerColor.ORANGE]: '#F97316',
    [PlayerColor.WHITE]: '#F8FAFC',
};

export const EdgeLine: React.FC<EdgeLineProps> = ({ x, y, rotation, length, road, onClick }) => {
    return (
        <div
            className="absolute z-10 flex items-center justify-center cursor-pointer group"
            style={{
                left: x,
                top: y,
                width: length,
                height: '20px', // Hit area height
                transform: `translate(-50%, -50%) rotate(${rotation}deg)`,
            }}
            onClick={onClick}
        >
            {/* Visual Line */}
            <div
                className={`h-2 rounded transition-all duration-200
                    ${road ? 'w-full' : 'w-2/3 bg-white/20 hover:bg-white/60'}
                `}
                style={{
                    backgroundColor: road ? playerColors[road.owner] : undefined
                }}
            />
        </div>
    );
};
