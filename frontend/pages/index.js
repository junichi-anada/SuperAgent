import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import Button from "../components/ui/Button";

export default function Home() {
	const [message, setMessage] = useState("Loading...");
	const [ollamaResponse, setOllamaResponse] = useState(null);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState(null);
	const [isLoggedIn, setIsLoggedIn] = useState(false);
	const router = useRouter();

	useEffect(() => {
		const token = localStorage.getItem("access_token");
		if (token) {
			setIsLoggedIn(true);
		}

		fetch(process.env.NEXT_PUBLIC_API_URL)
			.then((res) => {
				if (!res.ok) {
					throw new Error("Network response was not ok");
				}
				return res.json();
			})
			.then((data) => setMessage(data.message))
			.catch((error) => {
				console.error("Fetch error:", error);
				setMessage("Failed to fetch message from backend.");
			});
	}, []);

	const callOllamaAPI = async () => {
		setIsLoading(true);
		setError(null);
		setOllamaResponse(null);

		try {
			const response = await fetch("http://backend:8000/api/v1/poc/call-ollama");
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const data = await response.json();
			setOllamaResponse(data);
		} catch (err) {
			setError(err.message);
			console.error("Error calling Ollama API:", err);
		} finally {
			setIsLoading(false);
		}
	};

	const handleLogout = () => {
		localStorage.removeItem("access_token");
		setIsLoggedIn(false);
		router.push("/login");
	};

	return (
		<div className="min-h-screen bg-gray-100">
			{isLoggedIn && (
				<header className="bg-white shadow-sm">
					<div className="container mx-auto px-4 py-3 flex justify-between items-center">
						<div></div>
						<button onClick={handleLogout} className="px-4 py-2 font-bold text-white bg-danger rounded-md hover:bg-danger-hover transition-colors">
							ログアウト
						</button>
					</div>
				</header>
			)}

			<main className="container mx-auto px-4 py-10 text-center">
				<h1 className="text-5xl font-bold">✨ Super Agent ✨</h1>

				{isLoggedIn ? (
					<div className="mt-8">
						<h2 className="text-3xl font-semibold">ようこそ！</h2>
						<nav className="mt-10 flex justify-center gap-6">
							<Link href="/agents" className="px-8 py-4 bg-white border-2 border-primary rounded-lg text-xl font-bold text-primary hover:bg-blue-50 transition-all duration-300 transform hover:scale-105">
								エージェント一覧
							</Link>
							<Link href="/chats" className="px-8 py-4 bg-white border-2 border-primary rounded-lg text-xl font-bold text-primary hover:bg-blue-50 transition-all duration-300 transform hover:scale-105">
								チャット
							</Link>
						</nav>
					</div>
				) : (
					<div className="mt-8">
						<h2 className="text-3xl font-semibold">Frontend</h2>
						<p className="mt-4 text-lg p-5 bg-white rounded-lg shadow-md inline-block">
							Message from backend: <strong className="font-semibold text-primary">{message}</strong>
						</p>

						<div className="mt-10">
							<Button onClick={callOllamaAPI} disabled={isLoading}>
								{isLoading ? "呼び出し中..." : "バックエンドAPIを呼び出す"}
							</Button>
						</div>

						{error && (
							<div className="mt-6 max-w-xl mx-auto px-4 py-3 text-red-700 bg-red-100 border border-red-400 rounded-md" role="alert">
								<span className="block sm:inline">エラー: {error}</span>
							</div>
						)}

						{ollamaResponse && (
							<div className="mt-6 max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md text-left">
								<h3 className="text-xl font-bold mb-4">APIレスポンス:</h3>
								<pre className="p-4 bg-gray-100 rounded-md overflow-auto text-sm">{JSON.stringify(ollamaResponse, null, 2)}</pre>
							</div>
						)}
					</div>
				)}
			</main>
		</div>
	);
}

