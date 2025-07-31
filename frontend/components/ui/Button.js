import React from "react";

const Button = ({ children, ...props }) => {
	return (
		<button {...props} className="w-full px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 transition-colors duration-300">
			{children}
		</button>
	);
};

export default Button;

