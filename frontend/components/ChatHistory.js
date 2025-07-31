import { useEffect, useState } from "react";
import { NEW_CHAT_TEXT } from "../constants";

const ChatHistory = ({ agent, setSelectedChat }) => {
	const [chats, setChats] = useState([]);

	useEffect(() => {
		if (agent) {
			const fetchChats = async () => {
				const token = localStorage.getItem("access_token");
				if (!token) return;

				try {
					const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/chats/agent/${agent.id}`;
					const response = await fetch(apiUrl, {
						headers: {
							Authorization: `Bearer ${token}`,
						},
					});
					if (response.ok) {
						const data = await response.json();
						setChats(data);
					} else {
						console.error("Failed to fetch chats");
					}
				} catch (error) {
					console.error("Error fetching chats:", error);
				}
			};
			fetchChats();
		} else {
			setChats([]);
		}
	}, [agent]);

	const handleNewChat = () => {
		setSelectedChat(null); // Or a special object like { id: 'new' }
	};

	return (
		<div className="bg-gray-800 rounded-lg p-4 h-full">
			<h2 className="text-xl font-bold mb-4">Chats</h2>
			<ul className="space-y-2">
				{agent && (
					<li>
						<button onClick={handleNewChat} className="w-full text-left block p-2 rounded bg-blue-600 hover:bg-blue-700 font-bold">
							{NEW_CHAT_TEXT}
						</button>
					</li>
				)}
				{chats.map((chat) => (
					<li key={chat.id} onClick={() => setSelectedChat(chat)} className="cursor-pointer">
						<button className="w-full text-left block p-2 rounded hover:bg-gray-700">Chat {chat.id}</button>
					</li>
				))}
			</ul>
		</div>
	);
};

export default ChatHistory;

