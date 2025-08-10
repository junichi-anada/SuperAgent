import { useState, useEffect, useRef } from 'react';

const WebSocketDiagnostic = ({ ws, isConnected, statusMessage, error, reconnectAttempts }) => {
    const renderCount = useRef(0);
    const [lastMessage, setLastMessage] = useState(null);
    const [lastError, setLastError] = useState(null);
    const [connectionState, setConnectionState] = useState('Initial');

    useEffect(() => {
        renderCount.current += 1;
    });

    useEffect(() => {
        if (ws?.current) {
            const socket = ws.current;
            const onMessageHandler = (event) => setLastMessage({ data: event.data, time: new Date() });
            const onErrorHandler = (event) => setLastError({ event, time: new Date() });
            const onOpenHandler = () => setConnectionState('Open');
            const onCloseHandler = () => setConnectionState('Closed');

            socket.addEventListener('message', onMessageHandler);
            socket.addEventListener('error', onErrorHandler);
            socket.addEventListener('open', onOpenHandler);
            socket.addEventListener('close', onCloseHandler);

            return () => {
                socket.removeEventListener('message', onMessageHandler);
                socket.removeEventListener('error', onErrorHandler);
                socket.removeEventListener('open', onOpenHandler);
                socket.removeEventListener('close', onCloseHandler);
            };
        }
    }, [ws]);

    const getWsState = () => {
        if (!ws?.current) return 'Not Initialized';
        const stateMap = {
            [WebSocket.CONNECTING]: 'Connecting (0)',
            [WebSocket.OPEN]: 'Open (1)',
            [WebSocket.CLOSING]: 'Closing (2)',
            [WebSocket.CLOSED]: 'Closed (3)',
        };
        return stateMap[ws.current.readyState] || 'Unknown';
    };

    return (
        <div className="fixed bottom-4 right-4 bg-gray-900 text-white p-4 rounded-lg shadow-lg w-96 border border-gray-700 z-50 text-xs">
            <h3 className="font-bold text-base mb-2 border-b border-gray-600 pb-1">WebSocket Diagnostics</h3>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                <span className="font-semibold">Render Count:</span>
                <span>{renderCount.current}</span>

                <span className="font-semibold">Connection Status:</span>
                <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                </span>

                <span className="font-semibold">WebSocket State:</span>
                <span>{getWsState()}</span>
                
                <span className="font-semibold">Internal State:</span>
                <span>{connectionState}</span>

                <span className="font-semibold">Reconnect Attempts:</span>
                <span>{reconnectAttempts.current}</span>

                <span className="font-semibold">Status Message:</span>
                <span className="truncate">{statusMessage || 'N/A'}</span>

                <span className="font-semibold">Last Error:</span>
                <span className="truncate text-red-400">{error || 'N/A'}</span>
                
                <span className="font-semibold">Last WS Error:</span>
                <span className="truncate text-red-400">
                    {lastError ? `${lastError.time.toLocaleTimeString()}` : 'N/A'}
                </span>

                <span className="font-semibold">Last Message:</span>
                <span className="truncate">
                    {lastMessage ? `${lastMessage.time.toLocaleTimeString()}: ${lastMessage.data}` : 'N/A'}
                </span>
            </div>
        </div>
    );
};

export default WebSocketDiagnostic;