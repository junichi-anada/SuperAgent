import { useEffect, useState, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import AgentList from "../components/AgentList";
import ChatHistory from "../components/ChatHistory";
import ChatWindow from "../components/ChatWindow";

export default function Dashboard() {
	const { isLoggedIn, loading, logout, fetchWithAuth } = useAuth();
	const [agents, setAgents] = useState([]);
	const [selectedAgent, setSelectedAgent] = useState(null);
	const [selectedChat, setSelectedChat] = useState(null);
	const [chatListVersion, setChatListVersion] = useState(0);
	const [initialMessages, setInitialMessages] = useState([]);
	const [newChatCounter, setNewChatCounter] = useState(0);

	const handleChatCreated = (newChat, firstMessages) => {
		setInitialMessages(firstMessages);
		setChatListVersion(prev => prev + 1);
		setSelectedChat(newChat);
	};

	const handleNewChat = () => {
		setSelectedChat(null);
		setNewChatCounter(prev => prev + 1);
	};

	const handleSelectChat = (chat) => {
		setSelectedChat(chat);
		setInitialMessages([]); // Reset initial messages when a chat is selected
	};

	const fetchAgents = useCallback(async () => {
		if (!isLoggedIn) return;
		try {
			const response = await fetchWithAuth(`/api/v1/agents`);
			if (response.ok) {
				const data = await response.json();
				setAgents(data);
			} else {
				console.error("Failed to fetch agents");
			}
		} catch (error) {
			if (error.message !== "Unauthorized") {
				console.error("Error fetching agents:", error);
			}
		}
	}, [isLoggedIn, fetchWithAuth]);

	useEffect(() => {
		if (!loading && !isLoggedIn) {
			logout();
		}
	}, [isLoggedIn, loading, logout]);

	useEffect(() => {
		if (isLoggedIn) {
			fetchAgents();
		}
	}, [isLoggedIn, fetchAgents]);

	// ページにフォーカスが戻った際にエージェントリストを再取得
	useEffect(() => {
		const handleFocus = () => {
			if (isLoggedIn) {
				fetchAgents();
			}
		};

		window.addEventListener("focus", handleFocus);
		return () => window.removeEventListener("focus", handleFocus);
	}, [isLoggedIn, fetchAgents]);

	if (loading || !isLoggedIn) {
		return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center">Loading...</div>;
	}

	return (
		<div className="bg-gray-900 text-white min-h-screen flex flex-col">
			<header className="flex justify-between items-center p-4 border-b border-gray-700">
				<h1 className="text-2xl font-bold">✨ Super Agent ✨</h1>
				<button onClick={logout} className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
					ログアウト
				</button>
			</header>
			<main className="flex-grow grid grid-cols-1 md:grid-cols-4 gap-4 p-4">
				<aside className="md:col-span-1">
					<AgentList agents={agents} setSelectedAgent={setSelectedAgent} />
				</aside>
				<>
					<section className="md:col-span-1">
						<ChatHistory
							key={chatListVersion}
							agent={selectedAgent}
							selectedChat={selectedChat}
							setSelectedChat={handleSelectChat}
							onNewChat={handleNewChat}
						/>
					</section>
					<section className="md:col-span-2">
						<ChatWindow
							key={selectedChat ? selectedChat.id : `new-${newChatCounter}`}
							chat={selectedChat}
							agent={selectedAgent}
							onChatCreated={handleChatCreated}
							initialMessage={initialMessages}
						/>
					</section>
				</>
			</main>
		</div>
	);
}