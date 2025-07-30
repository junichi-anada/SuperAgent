import { useEffect, useState } from "react";

export default function Home() {
	const [message, setMessage] = useState("Loading...");

	useEffect(() => {
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

	return (
		<div style={{ fontFamily: "sans-serif", textAlign: "center", marginTop: "50px" }}>
			<h1>✨ Super Agent ✨</h1>
			<h2>Frontend</h2>
			<p style={{ fontSize: "1.2rem", padding: "20px", background: "#f0f0f0", borderRadius: "8px", display: "inline-block" }}>
				Message from backend: <strong>{message}</strong>
			</p>
		</div>
	);
}

