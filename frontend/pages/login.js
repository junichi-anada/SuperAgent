import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";

export default function Login() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState(null);
	const router = useRouter();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setIsLoading(true);
		setError(null);

		try {
			const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/token`, {
				method: "POST",
				headers: {
					"Content-Type": "application/x-www-form-urlencoded",
				},
				body: new URLSearchParams({
					username,
					password,
				}),
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || "ログインに失敗しました");
			}

			const data = await response.json();
			localStorage.setItem("access_token", data.access_token);
			router.push("/");
		} catch (err) {
			setError(err.message);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
			<div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
				<div className="text-center">
					<h1 className="text-4xl font-bold">✨ Super Agent ✨</h1>
					<h2 className="mt-2 text-2xl">ログイン</h2>
				</div>

				<form onSubmit={handleSubmit} className="space-y-6">
					<div>
						<Input type="text" placeholder="ユーザー名" value={username} onChange={(e) => setUsername(e.target.value)} required />
					</div>

					<div>
						<Input type="password" placeholder="パスワード" value={password} onChange={(e) => setPassword(e.target.value)} required />
					</div>

					<Button type="submit" disabled={isLoading}>
						{isLoading ? "ログイン中..." : "ログイン"}
					</Button>
				</form>

				{error && (
					<div className="px-4 py-3 text-red-700 bg-red-100 border border-red-400 rounded-md" role="alert">
						<span className="block sm:inline">エラー: {error}</span>
					</div>
				)}

				<p className="text-sm text-center text-gray-600">
					アカウントをお持ちでない方は{" "}
					<Link href="/signup" className="font-medium text-primary hover:text-primary-hover">
						新規登録
					</Link>
				</p>
			</div>
		</div>
	);
}

