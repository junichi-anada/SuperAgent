import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import AgentList from "../components/AgentList";
import ChatHistory from "../components/ChatHistory";
import ChatWindow from "../components/ChatWindow";

export default function Dashboard() {
	const [isLoggedIn, setIsLoggedIn] = useState(false);
	const router = useRouter();
	const [selectedAgent, setSelectedAgent] = useState(null);
	const [selectedChat, setSelectedChat] = useState(null);

	useEffect(() => {
		const token = localStorage.getItem("access_token");
		if (token) {
			setIsLoggedIn(true);
		} else {
			router.push("/login");
		}
	}, [router]);

	const handleLogout = () => {
		localStorage.removeItem("access_token");
		setIsLoggedIn(false);
		router.push("/login");
	};

	if (!isLoggedIn) {
		return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center">Loading...</div>;
	}

	return (
		<div className="bg-gray-900 text-white min-h-screen flex flex-col">
			<header className="flex justify-between items-center p-4 border-b border-gray-700">
				<h1 className="text-2xl font-bold">✨ Super Agent ✨</h1>
				<button onClick={handleLogout} className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
					ログアウト
				</button>
			</header>
			<main className="flex-grow grid grid-cols-1 md:grid-cols-4 gap-4 p-4">
				<aside className="md:col-span-1">
					<AgentList setSelectedAgent={setSelectedAgent} />
				</aside>
				<section className="md:col-span-1">
					<ChatHistory agent={selectedAgent} setSelectedChat={setSelectedChat} />
				</section>
				<section className="md:col-span-2">
					<ChatWindow chat={selectedChat} agent={selectedAgent} />
				</section>
			</main>
		</div>
	);
}

