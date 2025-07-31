import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Link from "next/link";

export default function NewAgent() {
	const [name, setName] = useState("");
	const [description, setDescription] = useState("");
	const [gender, setGender] = useState("");
	const [background, setBackground] = useState("");
	const [selectedPersonalities, setSelectedPersonalities] = useState([]);
	const [selectedRoles, setSelectedRoles] = useState([]);
	const [selectedTones, setSelectedTones] = useState([]);
	const [personalities, setPersonalities] = useState([]);
	const [roles, setRoles] = useState([]);
	const [tones, setTones] = useState([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);
	const router = useRouter();

	useEffect(() => {
		const fetchTags = async () => {
			const token = localStorage.getItem("access_token");
			if (!token) {
				router.push("/login");
				return;
			}

			try {
				const [personalitiesRes, rolesRes, tonesRes] = await Promise.all([
					fetch("http://localhost:8000/api/v1/tags/personalities", {
						headers: { Authorization: `Bearer ${token}` },
					}),
					fetch("http://localhost:8000/api/v1/tags/roles", {
						headers: { Authorization: `Bearer ${token}` },
					}),
					fetch("http://localhost:8000/api/v1/tags/tones", {
						headers: { Authorization: `Bearer ${token}` },
					}),
				]);

				if (personalitiesRes.ok && rolesRes.ok && tonesRes.ok) {
					setPersonalities(await personalitiesRes.json());
					setRoles(await rolesRes.json());
					setTones(await tonesRes.json());
				}
			} catch (err) {
				console.error("Failed to fetch tags:", err);
			}
		};

		fetchTags();
	}, [router]);

	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		setError(null);

		try {
			const token = localStorage.getItem("access_token");
			if (!token) {
				router.push("/login");
				return;
			}

			const response = await fetch("http://localhost:8000/agents/", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({
					name,
					description,
					gender,
					background,
					personality_ids: selectedPersonalities,
					role_ids: selectedRoles,
					tone_ids: selectedTones,
				}),
			});

			if (!response.ok) {
				if (response.status === 401) {
					router.push("/login");
					return;
				}
				throw new Error("エージェントの作成に失敗しました");
			}

			router.push("/agents");
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="min-h-screen bg-gray-100">
			<div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
				<div className="px-4 py-6 sm:px-0">
					<div className="mb-6">
						<Link href="/agents" className="text-blue-500 hover:text-blue-700">
							← エージェント一覧に戻る
						</Link>
					</div>

					<div className="max-w-2xl mx-auto">
						<h1 className="text-3xl font-bold text-gray-900 mb-6">新しいエージェントを作成</h1>

						<form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
							{error && <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>}

							<div className="mb-4">
								<label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
									名前
								</label>
								<input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" placeholder="エージェントの名前" required />
							</div>

							<div className="mb-4">
								<label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
									説明
								</label>
								<textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" placeholder="エージェントの説明" rows="4" />
							</div>

							<div className="mb-4">
								<label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="gender">
									性別
								</label>
								<select id="gender" value={gender} onChange={(e) => setGender(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
									<option value="">選択してください</option>
									<option value="男性">男性</option>
									<option value="女性">女性</option>
									<option value="中性">中性</option>
									<option value="その他">その他</option>
								</select>
							</div>

							<div className="mb-4">
								<label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="background">
									背景設定
								</label>
								<textarea id="background" value={background} onChange={(e) => setBackground(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" placeholder="エージェントの背景や設定" rows="4" />
							</div>

							<div className="mb-4">
								<label className="block text-gray-700 text-sm font-bold mb-2">
									性格（複数選択可）
								</label>
								<div className="grid grid-cols-2 gap-2">
									{personalities.map((personality) => (
										<label key={personality.id} className="flex items-center">
											<input
												type="checkbox"
												value={personality.id}
												checked={selectedPersonalities.includes(personality.id)}
												onChange={(e) => {
													if (e.target.checked) {
														setSelectedPersonalities([...selectedPersonalities, personality.id]);
													} else {
														setSelectedPersonalities(selectedPersonalities.filter((id) => id !== personality.id));
													}
												}}
												className="mr-2"
											/>
											{personality.name}
										</label>
									))}
								</div>
							</div>

							<div className="mb-4">
								<label className="block text-gray-700 text-sm font-bold mb-2">
									役割（複数選択可）
								</label>
								<div className="grid grid-cols-2 gap-2">
									{roles.map((role) => (
										<label key={role.id} className="flex items-center">
											<input
												type="checkbox"
												value={role.id}
												checked={selectedRoles.includes(role.id)}
												onChange={(e) => {
													if (e.target.checked) {
														setSelectedRoles([...selectedRoles, role.id]);
													} else {
														setSelectedRoles(selectedRoles.filter((id) => id !== role.id));
													}
												}}
												className="mr-2"
											/>
											{role.name}
										</label>
									))}
								</div>
							</div>

							<div className="mb-6">
								<label className="block text-gray-700 text-sm font-bold mb-2">
									口調（複数選択可）
								</label>
								<div className="grid grid-cols-2 gap-2">
									{tones.map((tone) => (
										<label key={tone.id} className="flex items-center">
											<input
												type="checkbox"
												value={tone.id}
												checked={selectedTones.includes(tone.id)}
												onChange={(e) => {
													if (e.target.checked) {
														setSelectedTones([...selectedTones, tone.id]);
													} else {
														setSelectedTones(selectedTones.filter((id) => id !== tone.id));
													}
												}}
												className="mr-2"
											/>
											{tone.name}
										</label>
									))}
								</div>
							</div>

							<div className="flex items-center justify-between">
								<button type="submit" disabled={loading} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400">
									{loading ? "作成中..." : "作成"}
								</button>
							</div>
						</form>
					</div>
				</div>
			</div>
		</div>
	);
}

