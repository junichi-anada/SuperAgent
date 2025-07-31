import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";

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
		<div style={{ fontFamily: "sans-serif", textAlign: "center", marginTop: "50px" }}>
			<div style={{ position: "absolute", top: "20px", right: "20px" }}>
				{isLoggedIn && (
					<button
						onClick={handleLogout}
						style={{
							padding: "10px 20px",
							fontSize: "1rem",
							backgroundColor: "#f44336",
							color: "white",
							border: "none",
							borderRadius: "6px",
							cursor: "pointer",
						}}
					>
						ログアウト
					</button>
				)}
			</div>

			<h1>✨ Super Agent ✨</h1>

			{isLoggedIn ? (
				<div>
					<h2>ようこそ！</h2>
					<nav style={{ marginTop: "30px", display: "flex", justifyContent: "center", gap: "20px" }}>
						<Link href="/agents" style={{ textDecoration: "none", color: "#0070f3", fontSize: "1.2rem", padding: "10px 20px", border: "1px solid #0070f3", borderRadius: "8px" }}>
							エージェント一覧
						</Link>
						<Link href="/chats" style={{ textDecoration: "none", color: "#0070f3", fontSize: "1.2rem", padding: "10px 20px", border: "1px solid #0070f3", borderRadius: "8px" }}>
							チャット
						</Link>
					</nav>
				</div>
			) : (
				<div>
					<h2>Frontend</h2>
					<p style={{ fontSize: "1.2rem", padding: "20px", background: "#f0f0f0", borderRadius: "8px", display: "inline-block" }}>
						Message from backend: <strong>{message}</strong>
					</p>

					<div style={{ marginTop: "40px" }}>
						<button
							onClick={callOllamaAPI}
							disabled={isLoading}
							style={{
								padding: "12px 24px",
								fontSize: "1rem",
								backgroundColor: isLoading ? "#ccc" : "#0070f3",
								color: "white",
								border: "none",
								borderRadius: "6px",
								cursor: isLoading ? "not-allowed" : "pointer",
								transition: "background-color 0.2s",
							}}
						>
							{isLoading ? "呼び出し中..." : "バックエンドAPIを呼び出す"}
						</button>
					</div>

					{error && <div style={{ marginTop: "20px", padding: "10px", backgroundColor: "#fee", borderRadius: "6px", color: "#c00" }}>エラー: {error}</div>}

					{ollamaResponse && (
						<div style={{ marginTop: "20px", padding: "20px", backgroundColor: "#e7f5ff", borderRadius: "8px", textAlign: "left", maxWidth: "600px", margin: "20px auto" }}>
							<h3>APIレスポンス:</h3>
							<pre style={{ backgroundColor: "#f5f5f5", padding: "10px", borderRadius: "4px", overflow: "auto" }}>{JSON.stringify(ollamaResponse, null, 2)}</pre>
						</div>
					)}
				</div>
			)}
		</div>
	);
}

