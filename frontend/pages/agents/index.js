import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Link from "next/link";

export default function AgentsList() {
	const [agents, setAgents] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	const router = useRouter();

	useEffect(() => {
		const fetchAgents = async () => {
			try {
				const token = localStorage.getItem("access_token");
				if (!token) {
					router.push("/login");
					return;
				}

				const response = await fetch("http://localhost:8000/agents/", {
					headers: {
						Authorization: `Bearer ${token}`,
					},
				});

				if (!response.ok) {
					if (response.status === 401) {
						router.push("/login");
						return;
					}
					throw new Error("エージェントの取得に失敗しました");
				}

				const data = await response.json();
				setAgents(data);
			} catch (err) {
				setError(err.message);
			} finally {
				setLoading(false);
			}
		};

		fetchAgents();
	}, []);

	const handleStartChat = async (agentId) => {
		setError(null);
		try {
			const token = localStorage.getItem("access_token");
			if (!token) {
				router.push("/login");
				return;
			}

			const response = await fetch("http://localhost:8000/chats/", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({ agent_id: agentId }),
			});

			if (!response.ok) {
				throw new Error("チャットの開始に失敗しました");
			}

			const chat = await response.json();
			router.push(`/chats/${chat.id}`);
		} catch (err) {
			setError(err.message);
		}
	};

	if (loading) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<div className="text-lg">読み込み中...</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<div className="text-red-500">エラー: {error}</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-100">
			<div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
				<div className="px-4 py-6 sm:px-0">
					<div className="flex justify-between items-center mb-6">
						<h1 className="text-3xl font-bold text-gray-900">エージェント一覧</h1>
						<div>
							<Link href="/" className="text-blue-500 hover:text-blue-700 mr-4">
								トップに戻る
							</Link>
							<Link href="/agents/new" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
								新しいエージェントを作成
							</Link>
						</div>
					</div>

					{agents.length === 0 ? (
						<div className="text-center py-10">
							<p className="text-gray-500 mb-4">まだエージェントが作成されていません</p>
							<Link href="/agents/new" className="text-blue-500 hover:text-blue-700 underline">
								最初のエージェントを作成する
							</Link>
						</div>
					) : (
						<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
							{agents.map((agent) => (
								<div key={agent.id} className="bg-white overflow-hidden shadow rounded-lg">
									<div className="px-4 py-5 sm:p-6">
										<h3 className="text-lg leading-6 font-medium text-gray-900 mb-2">{agent.name}</h3>
										<p className="text-sm text-gray-500 mb-2">{agent.description || "説明なし"}</p>
										{agent.gender && (
											<p className="text-xs text-gray-400 mb-1">性別: {agent.gender}</p>
										)}
										{agent.personalities && agent.personalities.length > 0 && (
											<p className="text-xs text-gray-400 mb-1">性格: {agent.personalities.map(p => p.name).join("、")}</p>
										)}
										{agent.roles && agent.roles.length > 0 && (
											<p className="text-xs text-gray-400 mb-1">役割: {agent.roles.map(r => r.name).join("、")}</p>
										)}
										{agent.tones && agent.tones.length > 0 && (
											<p className="text-xs text-gray-400 mb-2">口調: {agent.tones.map(t => t.name).join("、")}</p>
										)}
										<div className="flex items-center mt-4">
											<Link href={`/agents/${agent.id}`} className="text-blue-500 hover:text-blue-700 text-sm font-medium">
												編集
											</Link>
											<button onClick={() => handleStartChat(agent.id)} className="ml-4 text-green-500 hover:text-green-700 text-sm font-medium">
												チャット
											</button>
										</div>
									</div>
								</div>
							))}
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

