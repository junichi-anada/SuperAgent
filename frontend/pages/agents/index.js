import { useEffect, useState, useCallback } from "react";
import { useAuth } from "../../contexts/AuthContext";
import Link from "next/link";

export default function AgentsPage() {
	const { isLoggedIn, loading, logout, fetchWithAuth } = useAuth();
	const [agents, setAgents] = useState([]);

	const fetchAgents = useCallback(async () => {
		if (!isLoggedIn) return;
		try {
			const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "";
			const response = await fetchWithAuth(`${baseUrl}/api/v1/agents`);
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

	if (loading || !isLoggedIn) {
		return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center">Loading...</div>;
	}

	return (
		<div className="bg-gray-900 text-white min-h-screen flex flex-col">
			<header className="flex justify-between items-center p-4 border-b border-gray-700">
				<h1 className="text-2xl font-bold">
					<Link href="/">
						✨ Super Agent ✨
					</Link>
				</h1>
				<button onClick={logout} className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
					ログアウト
				</button>
			</header>
			<main className="flex-grow p-4">
				<div className="max-w-6xl mx-auto">
					<div className="mb-4">
						<Link href="/" className="text-blue-400 hover:text-blue-300">
							← チャットに戻る
						</Link>
					</div>
					<div className="bg-gray-800 rounded-lg p-6">
						<h2 className="text-2xl font-bold mb-6">エージェント管理</h2>
						<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
							{agents.map((agent) => (
								<div key={agent.id} className="bg-gray-700 rounded-lg p-4 flex flex-col items-center">
									<div className="w-20 h-20 bg-gray-600 rounded-full mb-3 flex-shrink-0">
										{agent.image_url && (
											<img src={`${process.env.NEXT_PUBLIC_API_BASE_URL || ""}${agent.image_url}`} alt={agent.name} className="w-20 h-20 rounded-full object-cover" />
										)}
									</div>
									<h3 className="text-lg font-semibold text-center mb-2">{agent.name}</h3>
									<p className="text-gray-300 text-sm text-center mb-4 line-clamp-2">{agent.description}</p>
									<div className="flex space-x-2">
										<Link href={`/agents/${agent.id}`} className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
											編集
										</Link>
									</div>
								</div>
							))}
						</div>
						<div className="mt-6">
							<Link href="/agents/new" className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded">
								新しいエージェントを作成
							</Link>
						</div>
					</div>
				</div>
			</main>
		</div>
	);
}