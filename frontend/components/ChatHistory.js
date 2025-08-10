import { useEffect, useState, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import { NEW_CHAT_TEXT } from "../constants";

const ChatHistory = ({ agent, selectedChat, setSelectedChat, onNewChat }) => {
	const { fetchWithAuth } = useAuth();
	const [chats, setChats] = useState([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	const fetchChats = useCallback(async () => {
		if (!agent) return;
		setLoading(true);
		setError(null);
		try {
			const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "";
			const apiUrl = `${baseUrl}/api/v1/chats/agent/${agent.id}`;
			const response = await fetchWithAuth(apiUrl);
			if (response.ok) {
				const data = await response.json();
				setChats(data);
			} else {
				setError("Failed to fetch chats.");
				console.error("Failed to fetch chats");
			}
		} catch (error) {
			if (error.message !== "Unauthorized") {
				setError("Error fetching chats.");
				console.error("Error fetching chats:", error);
			}
		} finally {
			setLoading(false);
		}
	}, [agent, fetchWithAuth]);

	useEffect(() => {
		if (agent) {
			fetchChats();
		} else {
			setChats([]);
		}
	}, [agent, fetchChats]);

	// This is now handled by the parent component
	// const handleNewChat = () => {
	// 	setSelectedChat(null);
	// };

	const handleDeleteChat = async (chatId, e) => {
		e.stopPropagation(); // Prevent chat selection when clicking delete
		if (window.confirm("Are you sure you want to delete this chat?")) {
			setLoading(true);
			setError(null);
			try {
				const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "";
				const apiUrl = `${baseUrl}/api/v1/chats/${chatId}`;
				const response = await fetchWithAuth(apiUrl, {
					method: "DELETE",
				});

				if (response.ok) {
					if (selectedChat && selectedChat.id === chatId) {
						setSelectedChat(null);
					}
					await fetchChats();
				} else {
					const errorData = await response.json();
					setError(errorData.detail || "Failed to delete chat.");
				}
			} catch (err) {
				if (err.message !== "Unauthorized") {
					setError("An error occurred while deleting the chat.");
					console.error("Error deleting chat:", err);
				}
			} finally {
				setLoading(false);
			}
		}
	};

	return (
		<div className="bg-gray-800 rounded-lg p-4 h-full flex flex-col">
			<h2 className="text-xl font-bold mb-4">Chats</h2>
			{agent && (
				<button onClick={onNewChat} className="w-full text-left block p-2 rounded bg-blue-600 hover:bg-blue-700 font-bold mb-4">
					{NEW_CHAT_TEXT}
				</button>
			)}
			{loading && <p>Loading chats...</p>}
			{error && <p className="text-red-500">{error}</p>}
			<ul className="space-y-2 flex-grow overflow-y-auto">
				{chats.map((chat) => (
					<li
						key={chat.id}
						onClick={() => setSelectedChat(chat)}
						className={`cursor-pointer p-2 rounded flex justify-between items-center group hover:bg-gray-700 ${
							selectedChat?.id === chat.id ? "bg-gray-700" : ""
						}`}
					>
						<span className="truncate">Chat {chat.id}</span>
						<button
							onClick={(e) => handleDeleteChat(chat.id, e)}
							className="text-gray-400 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"
							aria-label="Delete chat"
						>
							<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
								<path
									fillRule="evenodd"
									d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z"
									clipRule="evenodd"
								/>
							</svg>
						</button>
					</li>
				))}
			</ul>
		</div>
	);
};

export default ChatHistory;

