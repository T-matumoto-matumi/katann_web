import React from 'react';
// import { PlayerColor, ResourceType } from '../types';

interface TradePanelProps {
    gameState: any;
    myColor: any;
    onBankTrade: any;
    onOfferTrade: any;
    onCancelTrade: any;
    onRespondTrade: any;
    onConfirmTrade: any;
    onClose: () => void;
}

// const RESOURCE_EMOJIS ...


export const TradePanel: React.FC<TradePanelProps> = ({ onClose }) => {
    return (
        <div className="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center">
            <div className="bg-white p-6 rounded">
                <h1>Trade Panel Debug</h1>
                <button onClick={onClose}>Close</button>
            </div>
        </div>
    );
};
