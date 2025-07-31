import { useEffect, useState } from "react";

const ChatWindow = ({ chat, agent }) => {
	const [messages, setMessages] = useState([]);
	const [newMessage, setNewMessage] = useState("");
	const [currentChat, setCurrentChat] = useState(chat);
	const [error, setError] = useState(null);

	useEffect(() => {
		setCurrentChat(chat);
		if (chat) {
			const fetchMessages = async () => {
				const token = localStorage.getItem("access_token");
				if (!token) return;

				try {
					const response = await fetch(`http://localhost:8000/chats/${chat.id}/messages`, {
						headers: {
							Authorization: `Bearer ${token}`,
						},
					});
					if (response.ok) {
						const data = await response.json();
						setMessages(data);
					} else {
						console.error("Failed to fetch messages");
						setError("Failed to load messages.");
					}
				} catch (error) {
					console.error("Error fetching messages:", error);
					setError("An error occurred while fetching messages.");
				}
			};
			fetchMessages();
		} else {
			setMessages([]);
		}
	}, [chat]);

	const handleSendMessage = async () => {
		if (newMessage.trim() === "" || !agent) return;
		setError(null);

		const token = localStorage.getItem("access_token");
		if (!token) return;

		let chatToUse = currentChat;

		if (!chatToUse) {
			try {
				const response = await fetch("http://localhost:8000/chats/", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
					body: JSON.stringify({ agent_id: agent.id }),
				});
				if (response.ok) {
					const newChat = await response.json();
					setCurrentChat(newChat);
					chatToUse = newChat;
				} else {
					console.error("Failed to create new chat");
					setError("Failed to create a new chat. Please try again.");
					return;
				}
			} catch (error) {
				console.error("Error creating new chat:", error);
				setError("An error occurred while creating a new chat. Please try again.");
				return;
			}
		}

		const tempMessage = { id: `temp-${Date.now()}`, content: newMessage, sender: "user" };
		setMessages((prev) => [...prev, tempMessage]);
		setNewMessage("");

		try {
			const response = await fetch(`http://localhost:8000/chats/${chatToUse.id}/messages`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({ content: newMessage }),
			});

			if (response.ok) {
				const [userMessage, aiMessage] = await response.json();
				setMessages((prev) => [...prev.filter((msg) => msg.id !== tempMessage.id), userMessage, aiMessage]);
			} else {
				console.error("Failed to send message");
				setError("Failed to send message. Please try again.");
				setMessages((prev) => prev.filter((msg) => msg.id !== tempMessage.id));
			}
		} catch (error) {
			console.error("Error sending message:", error);
			setError("An error occurred while sending the message. Please try again.");
			setMessages((prev) => prev.filter((msg) => msg.id !== tempMessage.id));
		}
	};

	const handleKeyDown = (e) => {
		if (e.key === "Enter") {
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
			<div className="p-4 border-b border-gray-700">
				<h2 className="text-xl font-bold">{agent.name}</h2>
			</div>
			<div className="flex-grow p-4 overflow-y-auto">
				{messages.map((msg) => (
					<div key={msg.id} className={`mb-2 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
						<span className={`inline-block p-2 rounded-lg ${msg.sender === "user" ? "bg-blue-600" : "bg-gray-700"}`}>{msg.content}</span>
					</div>
				))}
			</div>
			<div className="p-4 border-t border-gray-700">
				{error && <p className="text-red-500 text-sm mb-2">{error}</p>}
				<input type="text" placeholder="Type a message..." className="w-full bg-gray-700 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500" value={newMessage} onChange={(e) => setNewMessage(e.target.value)} onKeyDown={handleKeyDown} />
			</div>
		</div>
	);
};

export default ChatWindow;

