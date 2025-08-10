import { useEffect, useState, useCallback, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";

const ChatWindow = ({ chat, agent, onChatCreated, initialMessage }) => {
	const { fetchWithAuth, token } = useAuth();
	const [messages, setMessages] = useState(initialMessage || []);
	const [newMessage, setNewMessage] = useState("");
	const [currentChat, setCurrentChat] = useState(chat);
	const [error, setError] = useState(null);
	const [statusMessage, setStatusMessage] = useState(null);
	const [isConnected, setIsConnected] = useState(false);
	// pendingMessage state is completely removed.
	const ws = useRef(null);
	const reconnectTimeout = useRef(null);
	const reconnectAttempts = useRef(0);
	const maxReconnectAttempts = 5;
	const reconnectDelay = useRef(1000);
	const messagesEndRef = useRef(null);

	// Auto-scroll to bottom when new messages arrive
	useEffect(() => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages]);

	const fetchMessages = useCallback(async () => {
		if (!chat) return;
		try {
			const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
			const apiUrl = `${baseUrl}/api/v1/chats/${chat.id}/messages`;
			const response = await fetchWithAuth(apiUrl);
			if (response.ok) {
				const data = await response.json();
				const sortedMessages = data.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
				setMessages(sortedMessages);
			} else {
				console.error("Failed to fetch messages");
				setError("Failed to load messages.");
			}
		} catch (error) {
			if (error.message !== "Unauthorized") {
				console.error("Error fetching messages:", error);
				setError("An error occurred while fetching messages.");
			}
		}
	}, [chat, fetchWithAuth]);

	useEffect(() => {
		// This effect synchronizes the component's state with the props from the parent.
		setCurrentChat(chat);

		if (initialMessage && initialMessage.length > 0) {
			// If there are initial messages (from a new chat), display them.
			setMessages(initialMessage);
		} else if (chat) {
			// If an existing chat is selected, fetch its history.
			fetchMessages();
		} else {
			// If no chat is selected (new chat mode), clear messages.
			setMessages([]);
		}
	}, [chat, initialMessage, fetchMessages]);

	const connectWebSocket = useCallback((chatId, authToken) => {
		if (!chatId || !authToken) {
			return;
		}

		// Clean up existing connection
		if (ws.current && ws.current.readyState !== WebSocket.CLOSED) {
			ws.current.close();
		}

		const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
		const wsUrl = `${baseUrl.replace(/^https?/, "ws")}/api/v1/chats/ws/${chatId}?token=${authToken}`;
		
		console.log("Connecting to WebSocket:", wsUrl);
		
		setStatusMessage("接続中...");
		setIsConnected(false);
		setError(null);
		
		const socket = new WebSocket(wsUrl);
		ws.current = socket;

		socket.onopen = () => {
			console.log("WebSocket connected successfully");
			setStatusMessage(null);
			setIsConnected(true);
			setError(null);
			reconnectAttempts.current = 0;
			reconnectDelay.current = 1000;
		};

		socket.onerror = (error) => {
			console.error("WebSocket error occurred:", error);
			// This event will also trigger onclose, so we handle reconnection there.
		};

		socket.onclose = (event) => {
			console.log(`WebSocket closed with code ${event.code}`);
			setIsConnected(false);
			
			// If ws.current is null, it means we closed it intentionally.
			if (!ws.current || ws.current !== socket) {
				return;
			}

			if (event.code === 1008) {
				setError("認証に失敗しました。再度ログインしてください。");
				return;
			}
			
			if (reconnectAttempts.current < maxReconnectAttempts) {
				reconnectAttempts.current++;
				const delay = Math.min(reconnectDelay.current * 2, 10000);
				reconnectDelay.current = delay;
				
				setStatusMessage(`再接続を試みています... (${reconnectAttempts.current}/${maxReconnectAttempts})`);
				
				reconnectTimeout.current = setTimeout(() => {
					connectWebSocket(chatId, authToken);
				}, delay);
			} else {
				setError("接続を確立できませんでした。ページを更新してください。");
				setStatusMessage(null);
			}
		};

		socket.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);

				if (data.type === "status") {
					setStatusMessage(data.message);
				} else if (data.error) {
					setError(data.content || "エラーが発生しました。");
					setStatusMessage(null);
				} else {
					setStatusMessage(null);
					setError(null);
					setMessages((prevMessages) => {
						const exists = prevMessages.some((msg) => msg.id === data.id);
						if (exists) return prevMessages;
						return [...prevMessages, data];
					});
				}
			} catch (error) {
				console.error("Failed to parse WebSocket message:", error);
			}
		};
	}, []); // No dependencies, this function is stable.

	useEffect(() => {
		if (currentChat?.id && token) {
			connectWebSocket(currentChat.id, token);
		}

		return () => {
			if (reconnectTimeout.current) {
				clearTimeout(reconnectTimeout.current);
			}
			if (ws.current) {
				console.log("Closing WebSocket connection on cleanup.");
				const socket = ws.current;
				ws.current = null; // Prevent reconnection by setting this before close
				socket.close(1000, "Component unmounting");
			}
		};
	}, [currentChat?.id, token, connectWebSocket]);

	// The logic for pendingMessage is no longer required.

	const handleSendMessage = async () => {
		if (newMessage.trim() === "" || !agent) return;
		setError(null);

		const messageToSend = newMessage.trim();
		setNewMessage("");

		if (!currentChat) {
			// Create a new chat and send the first message.
			try {
				const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
				const apiUrl = `${baseUrl}/api/v1/chats/`;
				const response = await fetchWithAuth(apiUrl, {
					method: "POST",
					body: JSON.stringify({
						agent_id: agent.id,
						first_message: messageToSend
					}),
				});
				
				if (response.ok) {
					const newChatWithMessages = await response.json();
					if (onChatCreated) {
						onChatCreated(newChatWithMessages, newChatWithMessages.messages);
					}
				} else {
					console.error("Failed to create new chat");
					setError("新しいチャットの作成に失敗しました。");
					setNewMessage(messageToSend);
				}
			} catch (error) {
				if (error.message !== "Unauthorized") {
					console.error("Error creating new chat:", error);
					setError("チャット作成中にエラーが発生しました。");
				}
				setNewMessage(messageToSend);
			}
		} else {
			// Send a message in an existing chat.
			if (isConnected && ws.current?.readyState === WebSocket.OPEN) {
				ws.current.send(JSON.stringify({ content: messageToSend }));
			} else {
				setError("WebSocket is not connected. Please wait or refresh.");
			}
		}
	};

	const handleKeyDown = (e) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSendMessage();
		}
	};

	if (!agent) {
		return (
			<div className="bg-gray-800 rounded-lg h-full flex items-center justify-center">
				<p className="text-gray-400">Select an agent to start chatting.</p>
			</div>
		);
	}

	return (
		<div className="bg-gray-800 rounded-lg h-full flex flex-col">
			<div className="p-4 border-b border-gray-700 flex justify-between items-center">
				<h2 className="text-xl font-bold">{agent.name}</h2>
				<div className="flex items-center space-x-2">
					{isConnected ? (
						<span className="text-green-500 text-xs flex items-center">
							<span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
							接続中
						</span>
					) : (
						<span className="text-yellow-500 text-xs flex items-center">
							<span className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></span>
							未接続
						</span>
					)}
				</div>
			</div>
			<div className="flex-grow p-4 overflow-y-auto h-[50vh]" style={{ scrollBehavior: 'smooth' }}>
				{messages.length === 0 && !statusMessage && (
					<div className="text-center text-gray-500 mt-8">
						<p>メッセージがありません。</p>
						<p className="text-sm mt-2">下のテキストボックスからメッセージを送信してください。</p>
					</div>
				)}
				{messages.map((msg, index) => (
					<div key={msg.id || `msg-${index}`} className={`mb-4 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
						<div className={`inline-block max-w-[80%] ${msg.sender === "user" ? "text-right" : "text-left"}`}>
							<div className={`inline-block p-3 rounded-lg ${
								msg.sender === "user" ? "bg-blue-600" :
								msg.sender === "system" ? "bg-red-900" : "bg-gray-700"
							}`}>
								{msg.content}
							</div>
							{msg.image_url && msg.sender === "ai" && (
								<div className="mt-2">
									<img
										src={msg.image_url}
										alt="Generated image"
										className="max-w-sm rounded-lg shadow-lg cursor-pointer hover:opacity-90 transition-opacity"
										onClick={() => window.open(msg.image_url, "_blank")}
										onError={(e) => {
											e.target.style.display = 'none';
											console.error("Failed to load image:", msg.image_url);
										}}
									/>
								</div>
							)}
							{msg.timestamp && (
								<div className="text-xs text-gray-500 mt-1">
									{new Date(msg.timestamp).toLocaleTimeString('ja-JP')}
								</div>
							)}
						</div>
					</div>
				))}
				{statusMessage && (
					<div className="text-center text-gray-400 italic py-2 animate-pulse">
						{statusMessage}
					</div>
				)}
				<div ref={messagesEndRef} />
			</div>
			<div className="p-4 border-t border-gray-700">
				{error && (
					<div className="bg-red-900 bg-opacity-50 text-red-200 text-sm p-2 rounded mb-2 flex justify-between items-center">
						<span>{error}</span>
						<button
							onClick={() => setError(null)}
							className="text-red-400 hover:text-red-300"
						>
							✕
						</button>
					</div>
				)}
				<div className="flex items-center space-x-2">
					<input
						type="text"
						placeholder={isConnected ? "メッセージを入力..." : "接続中..."}
						className="flex-1 bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
						value={newMessage}
						onChange={(e) => setNewMessage(e.target.value)}
						onKeyDown={handleKeyDown}
						disabled={(currentChat && !isConnected)}
					/>
					<button
						onClick={handleSendMessage}
						disabled={(currentChat && !isConnected) || !newMessage.trim()}
						className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
					>
						送信
					</button>
				</div>
			</div>
		</div>
	);
};

export default ChatWindow;

