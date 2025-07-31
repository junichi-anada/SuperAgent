import { useEffect, useState } from "react";
import Link from "next/link";
import { NEW_AGENT_BUTTON_TEXT } from "../constants";

const AgentList = ({ setSelectedAgent }) => {
	const [agents, setAgents] = useState([]);

	useEffect(() => {
		const fetchAgents = async () => {
			const token = localStorage.getItem("access_token");
			if (!token) {
				// Handle case where user is not logged in
				return;
			}

			try {
				const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/agents`;
				const response = await fetch(apiUrl, {
					headers: {
						Authorization: `Bearer ${token}`,
					},
				});
				if (response.ok) {
					const data = await response.json();
					setAgents(data);
				} else {
					console.error("Failed to fetch agents");
				}
			} catch (error) {
				console.error("Error fetching agents:", error);
			}
		};

		fetchAgents();
	}, []);

	return (
		<div className="bg-gray-800 rounded-lg p-4 h-full">
			<h2 className="text-xl font-bold mb-4">Agents</h2>
			<Link href="/agents/new">
				<button className="w-full text-left block p-2 rounded bg-green-600 hover:bg-green-700 font-bold mb-4">{NEW_AGENT_BUTTON_TEXT}</button>
			</Link>
			<ul className="space-y-2">
				{agents.map((agent) => (
					<li key={agent.id} onClick={() => setSelectedAgent(agent)} className="cursor-pointer">
						<span className="block p-2 rounded hover:bg-gray-700">{agent.name}</span>
					</li>
				))}
			</ul>
		</div>
	);
};

export default AgentList;

