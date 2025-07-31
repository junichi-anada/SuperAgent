/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./pages/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
	theme: {
		extend: {
			colors: {
				primary: {
					DEFAULT: "#3b82f6",
					hover: "#2563eb",
				},
				secondary: "#64748b",
				accent: "#ec4899",
				danger: {
					DEFAULT: "#ef4444",
					hover: "#dc2626",
				},
			},
		},
	},
	plugins: [],
};

