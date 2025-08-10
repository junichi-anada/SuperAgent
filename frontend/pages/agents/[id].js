import { useRouter } from "next/router";
import { useEffect } from "react";
import AgentForm from "../../components/AgentForm/AgentForm";
import Link from "next/link";
import { useAuth } from "../../contexts/AuthContext";

export default function EditAgentPage() {
	const router = useRouter();
	const { id } = router.query;
	const { isLoggedIn, loading } = useAuth();

	useEffect(() => {
		if (!loading && !isLoggedIn) {
			router.push("/login");
		}
	}, [isLoggedIn, loading, router]);

	const handleSave = (savedAgent) => {
		router.push("/");
	};

	const handleCancel = () => {
		router.push("/");
	};

	const handleDelete = () => {
		router.push("/");
	};

	if (loading || !isLoggedIn || !id) {
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
					<AgentForm agentId={id} onSave={handleSave} onCancel={handleCancel} onDelete={handleDelete} />
				</div>
			</main>
		</div>
	);
}