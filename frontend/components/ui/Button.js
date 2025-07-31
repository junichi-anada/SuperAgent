import React from "react";

const Button = ({ children, ...props }) => {
	return (
		<button {...props} className="w-full px-4 py-2 font-bold text-white bg-primary rounded-md hover:bg-primary-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400 transition-colors duration-300">
			{children}
		</button>
	);
};

export default Button;

