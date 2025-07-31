import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";

export default function Signup() {
	const [username, setUsername] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState(null);
	const router = useRouter();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setIsLoading(true);
		setError(null);

		try {
			const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/signup`, {
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

			await response.json();
			router.push("/login");
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
					<h2 className="mt-2 text-2xl">サインアップ</h2>
				</div>

				<form onSubmit={handleSubmit} className="space-y-6">
					<div>
						<Input type="text" placeholder="ユーザー名" value={username} onChange={(e) => setUsername(e.target.value)} required />
					</div>

					<div>
						<Input type="email" placeholder="メールアドレス" value={email} onChange={(e) => setEmail(e.target.value)} required />
					</div>

					<div>
						<Input type="password" placeholder="パスワード" value={password} onChange={(e) => setPassword(e.target.value)} required />
					</div>

					<Button type="submit" disabled={isLoading}>
						{isLoading ? "登録中..." : "登録"}
					</Button>
				</form>

				{error && (
					<div className="px-4 py-3 text-red-700 bg-red-100 border border-red-400 rounded-md" role="alert">
						<span className="block sm:inline">エラー: {error}</span>
					</div>
				)}

				<p className="text-sm text-center text-gray-600">
					すでにアカウントをお持ちの方は{" "}
					<Link href="/login" className="font-medium text-primary hover:text-primary-hover">
						ログイン
					</Link>
				</p>
			</div>
		</div>
	);
}

