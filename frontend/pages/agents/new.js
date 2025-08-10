import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import AgentForm from "../../components/AgentForm/AgentForm";
import Link from "next/link";

export default function NewAgentPage() {
	const router = useRouter();
	const [isLoggedIn, setIsLoggedIn] = useState(false);

	useEffect(() => {
		const token = localStorage.getItem("access_token");
		if (token) {
			setIsLoggedIn(true);
		} else {
			router.push("/login");
		}
	}, [router]);

	const handleSave = (savedAgent) => {
		router.push("/");
	};

	const handleCancel = () => {
		router.push("/");
	};

	if (!isLoggedIn) {
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
			</header>
			<main className="flex-grow p-4">
				<div className="max-w-4xl mx-auto">
					<AgentForm agentId={null} onSave={handleSave} onCancel={handleCancel} />
				</div>
			</main>
		</div>
	);
}