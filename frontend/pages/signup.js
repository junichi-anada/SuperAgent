import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { useAuth } from "../contexts/AuthContext";

export default function Signup() {
	const [username, setUsername] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState(null);
	const router = useRouter();
	const { login } = useAuth();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setIsLoading(true);
		setError(null);

		try {
			const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/signup`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					username,
					email,
					password,
				}),
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || "サインアップに失敗しました");
			}

			const data = await response.json();
			// Signup doesn't return a token, so we can't log in directly.
			// We will redirect to login page.
			router.push("/login");
		} catch (err) {
			setError(err.message);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="min-h-screen bg-gray-900 text-white flex flex-col justify-center items-center">
			<div className="w-full max-w-md">
				<div className="text-center mb-8">
					<h1 className="text-4xl font-bold">✨ Super Agent ✨</h1>
					<h2 className="text-2xl mt-2 text-gray-400">新規登録</h2>
				</div>

				<form onSubmit={handleSubmit} className="bg-gray-800 shadow-md rounded-lg px-8 pt-6 pb-8 mb-4">
					<div className="mb-4">
						<label className="block text-gray-400 text-sm font-bold mb-2" htmlFor="username">
							ユーザー名
						</label>
						<input id="username" type="text" placeholder="ユーザー名" value={username} onChange={(e) => setUsername(e.target.value)} required className="w-full bg-gray-700 text-white rounded p-3 focus:outline-none focus:ring-2 focus:ring-blue-500" />
					</div>

					<div className="mb-4">
						<label className="block text-gray-400 text-sm font-bold mb-2" htmlFor="email">
							メールアドレス
						</label>
						<input id="email" type="email" placeholder="メールアドレス" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full bg-gray-700 text-white rounded p-3 focus:outline-none focus:ring-2 focus:ring-blue-500" />
					</div>

					<div className="mb-6">
						<label className="block text-gray-400 text-sm font-bold mb-2" htmlFor="password">
							パスワード
						</label>
						<input id="password" type="password" placeholder="パスワード" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full bg-gray-700 text-white rounded p-3 focus:outline-none focus:ring-2 focus:ring-blue-500" />
					</div>

					<div className="flex items-center justify-between">
						<button type="submit" disabled={isLoading} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-600">
							{isLoading ? "登録中..." : "登録"}
						</button>
					</div>
				</form>

				{error && (
					<div className="bg-red-900 border border-red-400 text-red-300 px-4 py-3 rounded relative text-center" role="alert">
						<strong className="font-bold">エラー: </strong>
						<span className="block sm:inline">{error}</span>
					</div>
				)}

				<p className="text-center text-gray-500 text-sm mt-6">
					すでにアカウントをお持ちの方は{" "}
					<Link href="/login" className="font-bold text-blue-500 hover:text-blue-400">
						ログイン
					</Link>
				</p>
			</div>
		</div>
	);
}

