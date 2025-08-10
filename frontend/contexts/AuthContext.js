import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useRouter } from "next/router";
import { API_BASE_URL } from "../constants";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
	const [isLoggedIn, setIsLoggedIn] = useState(false);
	const [loading, setLoading] = useState(true);
	const [token, setToken] = useState(null);
	const router = useRouter();

	const checkUser = useCallback(async () => {
		const storedToken = localStorage.getItem("access_token");
		if (storedToken) {
			// ここでトークンの有効性をサーバーに問い合わせるのが理想
			setIsLoggedIn(true);
			setToken(storedToken);
		} else {
			setIsLoggedIn(false);
			setToken(null);
		}
		setLoading(false);
	}, []);

	useEffect(() => {
		checkUser();
	}, [checkUser]);

	const login = (newToken) => {
		localStorage.setItem("access_token", newToken);
		setToken(newToken);
		setIsLoggedIn(true);
		router.push("/");
	};

	const logout = useCallback(() => {
		localStorage.removeItem("access_token");
		setToken(null);
		setIsLoggedIn(false);
		router.push("/login");
	}, [router]);

	const fetchWithAuth = useCallback(
		async (url, options = {}) => {
			const token = localStorage.getItem("access_token");
			const headers = {
				...options.headers,
			};
			if (!(options.body instanceof FormData)) {
				headers["Content-Type"] = "application/json";
			}

			if (token) {
				headers["Authorization"] = `Bearer ${token}`;
			}

			const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
			console.log("Fetching URL:", fullUrl);
			console.log("Fetch options:", { ...options, headers });
			const response = await fetch(fullUrl, { ...options, headers });

			if (response.status === 401) {
				logout();
				throw new Error("Unauthorized");
			}

			return response;
		},
		[logout]
	);

	return (
		<AuthContext.Provider value={{ isLoggedIn, loading, token, login, logout, fetchWithAuth }}>{children}</AuthContext.Provider>
	);
};

export const useAuth = () => useContext(AuthContext);