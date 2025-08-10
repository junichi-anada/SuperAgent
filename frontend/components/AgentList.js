import { useState } from "react";
import { NEW_AGENT_BUTTON_TEXT } from "../constants";
import Link from "next/link";
import PhotoGalleryModal from "./PhotoGalleryModal";
import { normalizeImageUrl } from "../utils";

const AgentList = ({ agents, setSelectedAgent }) => {
	const [galleryModalOpen, setGalleryModalOpen] = useState(false);
	const [galleryAgent, setGalleryAgent] = useState(null);

	const handleImageClick = (e, agent) => {
		e.stopPropagation();
		setGalleryAgent(agent);
		setGalleryModalOpen(true);
	};

	return (
		<>
			<div className="bg-gray-800 rounded-lg p-4 h-full">
				<h2 className="text-xl font-bold mb-4">Agents</h2>
				<Link href="/agents/new" className="w-full text-left block p-2 rounded bg-green-600 hover:bg-green-700 font-bold mb-4">
					{NEW_AGENT_BUTTON_TEXT}
				</Link>
				<ul className="space-y-2">
					{agents.map((agent) => (
						<li key={agent.id} className="flex items-center justify-between p-2 rounded hover:bg-gray-700">
							<div onClick={() => setSelectedAgent(agent)} className="cursor-pointer flex-grow flex items-center space-x-3">
								<div
									className="w-10 h-10 bg-gray-700 rounded-full flex-shrink-0 cursor-pointer hover:ring-2 hover:ring-blue-500"
									onClick={(e) => handleImageClick(e, agent)}
								>
									{agent.image_url && (
										<img src={normalizeImageUrl(agent.image_url)} alt={agent.name} className="w-10 h-10 rounded-full object-cover" />
									)}
								</div>
								<span>{agent.name}</span>
							</div>
						<Link href={`/agents/${agent.id}`} className="p-1 text-gray-400 hover:text-white">
							<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
								<path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
								<path fillRule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clipRule="evenodd" />
							</svg>
						</Link>
					</li>
				))}
			</ul>
		</div>

		{/* フォトギャラリーモーダル */}
		<PhotoGalleryModal
			agent={galleryAgent}
			isOpen={galleryModalOpen}
			onClose={() => {
				setGalleryModalOpen(false);
				setGalleryAgent(null);
			}}
		/>
		</>
	);
};

export default AgentList;

