import React from "react";

const Input = ({ ...props }) => {
	return <input {...props} className="w-full px-4 py-2 text-gray-700 bg-gray-200 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:bg-white" />;
};

export default Input;

