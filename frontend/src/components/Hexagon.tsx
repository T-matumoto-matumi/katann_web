import React from 'react';
import { ResourceType } from '../types';

interface HexagonProps {
    x: number;
    y: number;
    size: number;
    resource: ResourceType;
    number: number | null;
}

const resourceColors: Record<ResourceType, string> = {
    [ResourceType.LUMBER]: '#228B22',   // ForestGreen
    [ResourceType.BRICK]: '#A52A2A',    // Brown
    [ResourceType.WOOL]: '#7FFF00',     // Chartreuse
    [ResourceType.GRAIN]: '#FFD700',    // Gold
    [ResourceType.ORE]: '#808080',      // Gray
    [ResourceType.DESERT]: '#F4A460',   // SandyBrown
};

export const Hexagon: React.FC<HexagonProps> = ({ x, y, size, resource, number }) => {
    // Pointy topped hexagon styling
    // Width = sqrt(3) * size
    // Height = 2 * size
    const width = Math.sqrt(3) * size;
    const height = 2 * size;

    return (
        <div
            className="absolute flex items-center justify-center"
            style={{
                left: x,
                top: y,
                width: width,
                height: height,
                transform: 'translate(-50%, -50%)', // Center the hex on x,y
            }}
        >
            <div
                className="w-full h-full flex items-center justify-center"
                style={{
                    backgroundColor: resourceColors[resource],
                    clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'
                }}
            >
                {number !== null && (
                    <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md z-10">
                        <span className={`font-bold ${number === 6 || number === 8 ? 'text-red-500' : 'text-black'}`}>
                            {number}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
};
