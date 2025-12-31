import React from 'react';
import { PlayerColor } from '../types';
import type { Building } from '../types';

interface VertexNodeProps {
    x: number;
    y: number;
    building?: Building;
    onClick: () => void;
}

const playerColors: Record<PlayerColor, string> = {
    [PlayerColor.RED]: '#EF4444',
    [PlayerColor.BLUE]: '#3B82F6',
    [PlayerColor.ORANGE]: '#F97316',
    [PlayerColor.WHITE]: '#F8FAFC',
};

export const VertexNode: React.FC<VertexNodeProps> = ({ x, y, building, onClick }) => {
    return (
        <div
            className="absolute z-20 flex items-center justify-center cursor-pointer group"
            style={{
                left: x,
                top: y,
                width: '30px', // Hit area
                height: '30px',
                transform: 'translate(-50%, -50%)',
            }}
            onClick={onClick}
        >
            {/* Visual Node */}
            {building ? (
                <div
                    className="flex items-center justify-center rounded-full shadow-md border-2 border-white transition-transform duration-200 hover:scale-125 z-10"
                    style={{
                        backgroundColor: playerColors[building.owner],
                        width: '32px',
                        height: '32px',
                    }}
                    title={`${building.owner}'s ${building.type}`}
                >
                    <div className="text-xl select-none leading-none pb-1">
                        {building.type === 'city' ? '🏙️' : '🏠'}
                    </div>
                </div>
            ) : (
                <div
                    className="w-4 h-4 bg-white/30 rounded-full hover:bg-white/80 transition-all duration-200 group-hover:w-5 group-hover:h-5 shadow-sm border border-white/10"
                />
            )}
        </div>
    );
};
