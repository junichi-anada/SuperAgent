import { useState } from "react";
import { useRouter } from "next/router";

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
    <div style={{ fontFamily: "sans-serif", textAlign: "center", marginTop: "50px" }}>
      <h1>✨ Super Agent ✨</h1>
      <h2>サインアップ</h2>

      <form
        onSubmit={handleSubmit}
        style={{
          maxWidth: "400px",
          margin: "0 auto",
          padding: "20px",
          backgroundColor: "#f7f7f7",
          borderRadius: "8px",
        }}
      >
        <div style={{ marginBottom: "15px" }}>
          <input
            type="text"
            placeholder="ユーザー名"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "10px",
              border: "1px solid #ddd",
              borderRadius: "4px",
              fontSize: "16px",
              boxSizing: "border-box",
            }}
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <input
            type="email"
            placeholder="メールアドレス"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "10px",
              border: "1px solid #ddd",
              borderRadius: "4px",
              fontSize: "16px",
              boxSizing: "border-box",
            }}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <input
            type="password"
            placeholder="パスワード"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "10px",
              border: "1px solid #ddd",
              borderRadius: "4px",
              fontSize: "16px",
              boxSizing: "border-box",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "12px",
            fontSize: "16px",
            backgroundColor: isLoading ? "#ccc" : "#0070f3",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: isLoading ? "not-allowed" : "pointer",
            transition: "background-color 0.2s",
          }}
        >
          {isLoading ? "登録中..." : "登録"}
        </button>
      </form>

      {error && (
        <div
          style={{
            marginTop: "20px",
            padding: "10px",
            backgroundColor: "#fee",
            borderRadius: "6px",
            color: "#c00",
            maxWidth: "400px",
            margin: "20px auto 0",
          }}
        >
          エラー: {error}
        </div>
      )}

      <p style={{ marginTop: "20px" }}>
        すでにアカウントをお持ちの方は{" "}
        <a href="/login" style={{ color: "#0070f3" }}>
          ログイン
        </a>
      </p>
    </div>
  );
}