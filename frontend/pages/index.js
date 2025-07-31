import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";

// 仮のコンポーネントたち
const AgentList = () => (
	<div className="bg-gray-800 rounded-lg p-4 h-full">
		<h2 className="text-xl font-bold mb-4">Agents</h2>
		<ul className="space-y-2">
			<li>
				<span className="block p-2 rounded bg-gray-700 text-gray-400">Agent 1 (Sample)</span>
			</li>
			<li>
				<span className="block p-2 rounded bg-gray-700 text-gray-400">Agent 2 (Sample)</span>
			</li>
			<li>
				<span className="block p-2 rounded bg-gray-700 text-gray-400">Agent 3 (Sample)</span>
			</li>
		</ul>
	</div>
);

const ChatHistory = () => (
	<div className="bg-gray-800 rounded-lg p-4 h-full">
		<h2 className="text-xl font-bold mb-4">Chats</h2>
		<ul className="space-y-2">
			<li>
				<a href="javascript:void(0)" className="block p-2 rounded hover:bg-gray-700" title="Sample item - not functional">
					Chat with Agent 1
				</a>
			</li>
			<li>
				<a href="javascript:void(0)" className="block p-2 rounded hover:bg-gray-700" title="Sample item - not functional">
					Chat with Agent 2
				</a>
			</li>
		</ul>
	</div>
);

const ChatWindow = () => {
	const [message, setMessage] = useState("");

	const handleInputChange = (e) => {
		setMessage(e.target.value);
	};

	const handleKeyDown = (e) => {
		if (e.key === "Enter" && message.trim()) {
			console.log("Message sent:", message); // Replace with actual message handling logic
			setMessage("");
		}
	};

	return (
		<div className="bg-gray-800 rounded-lg h-full flex flex-col">
			<div className="p-4 border-b border-gray-700">
				<h2 className="text-xl font-bold">Agent 1</h2>
			</div>
			<div className="flex-grow p-4 overflow-y-auto">
				{/* Chat messages go here */}
				<p>Hello! How can I help you today?</p>
			</div>
			<div className="p-4 border-t border-gray-700">
				<input type="text" placeholder="Type a message..." className="w-full bg-gray-700 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500" value={message} onChange={handleInputChange} onKeyDown={handleKeyDown} />
			</div>
		</div>
	);
};

export default function Dashboard() {
	const [isLoggedIn, setIsLoggedIn] = useState(false);
	const router = useRouter();

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
					<AgentList />
				</aside>
				<section className="md:col-span-1">
					<ChatHistory />
				</section>
				<section className="md:col-span-2">
					<ChatWindow />
				</section>
			</main>
		</div>
	);
}

