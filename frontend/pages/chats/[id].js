import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { Container, Paper, TextField, Button, Box, Typography, List, ListItem, ListItemText, Divider } from "@mui/material";

export default function ChatRoom() {
	const router = useRouter();
	const { id } = router.query;
	const [messages, setMessages] = useState([]);
	const [inputMessage, setInputMessage] = useState("");
	const [ws, setWs] = useState(null);
	const [chat, setChat] = useState(null);
	const messagesEndRef = useRef(null);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages]);

	useEffect(() => {
		if (!id) return;

		// Fetch chat info
		fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chats/${id}`, {
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		})
			.then((res) => {
				if (!res.ok) throw new Error("Failed to fetch chat info");
				return res.json();
			})
			.then((data) => setChat(data))
			.catch((err) => console.error(err));

		// Load existing messages
		fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chats/${id}/messages`, {
			headers: {
				Authorization: `Bearer ${localStorage.getItem("access_token")}`,
			},
		})
			.then((res) => {
				if (!res.ok) {
					// 404 Not Foundなどのエラーケース
					if (res.status === 404) {
						return []; // メッセージがない場合は空の配列を返す
					}
					throw new Error(`HTTP error! status: ${res.status}`);
				}
				return res.json();
			})
			.then((data) => {
				if (Array.isArray(data)) {
					setMessages(data);
				} else {
					console.error("Loaded messages data is not an array:", data);
					setMessages([]);
				}
			})
			.catch((err) => {
				console.error("Failed to load messages:", err);
				setMessages([]); // エラー時も空配列をセット
			});

		// Connect to WebSocket
		const token = localStorage.getItem("access_token");
		if (!token) {
			router.push("/login");
			return;
		}
		const websocket = new WebSocket(`${process.env.NEXT_PUBLIC_API_URL.replace(/^http/, 'ws')}/api/v1/chats/ws/${id}?token=${token}`);

		websocket.onopen = () => {
			console.log("WebSocket connected");
		};

		websocket.onmessage = (event) => {
			const message = JSON.parse(event.data);
			if (message.error) {
				console.error("WebSocket error:", message.error);
			} else {
				setMessages((prev) => [...prev, message]);
			}
		};

		websocket.onerror = (error) => {
			console.error("WebSocket error:", error);
		};

		websocket.onclose = () => {
			console.log("WebSocket disconnected");
		};

		setWs(websocket);

		return () => {
			websocket.close();
		};
	}, [id]);

	const sendMessage = () => {
		if (!inputMessage.trim() || !ws || ws.readyState !== WebSocket.OPEN) return;

		const token = localStorage.getItem("access_token");
		ws.send(JSON.stringify({ content: inputMessage, token: token }));
		setInputMessage("");
	};

	const handleKeyPress = (e) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	};

	return (
		<Container maxWidth="md" sx={{ mt: 4 }}>
			<Paper elevation={3} sx={{ height: "80vh", display: "flex", flexDirection: "column" }}>
				<Box sx={{ p: 2, borderBottom: 1, borderColor: "divider", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
					<Typography variant="h5">チャット</Typography>
					{chat && (
						<Link href={`/agents/${chat.agent_id}`} passHref>
							<Button variant="outlined" size="small">
								エージェント詳細に戻る
							</Button>
						</Link>
					)}
				</Box>

				<Box sx={{ flexGrow: 1, overflow: "auto", p: 2 }}>
					<List>
						{messages.map((message, index) => (
							<Box key={message.id || index}>
								<ListItem alignItems="flex-start">
									<ListItemText
										primary={
											<Typography component="span" variant="body2" color="text.primary" sx={{ fontWeight: "bold" }}>
												{message.sender === "user" ? "あなた" : "AI"}
											</Typography>
										}
										secondary={
											<>
												<Typography component="span" variant="body1" color="text.primary" sx={{ display: "block", mt: 0.5 }}>
													{message.content}
												</Typography>
												{message.image_url && (
													<Box sx={{ mt: 1, mb: 1 }}>
														<img src={message.image_url} alt="AI generated" style={{ maxWidth: "100%", height: "auto", borderRadius: "8px" }} />
													</Box>
												)}
												<Typography component="span" variant="caption" color="text.secondary">
													{message.created_at ? new Date(message.created_at).toLocaleString("ja-JP") : ""}
												</Typography>
											</>
										}
									/>
								</ListItem>
								{index < messages.length - 1 && <Divider variant="inset" component="li" />}
							</Box>
						))}
						<div ref={messagesEndRef} />
					</List>
				</Box>

				<Box sx={{ p: 2, borderTop: 1, borderColor: "divider" }}>
					<Box sx={{ display: "flex", gap: 1 }}>
						<TextField fullWidth multiline maxRows={4} value={inputMessage} onChange={(e) => setInputMessage(e.target.value)} onKeyPress={handleKeyPress} placeholder="メッセージを入力..." variant="outlined" size="small" />
						<Button variant="contained" onClick={sendMessage} disabled={!inputMessage.trim() || !ws || ws.readyState !== WebSocket.OPEN}>
							送信
						</Button>
					</Box>
				</Box>
			</Paper>
		</Container>
	);
}

