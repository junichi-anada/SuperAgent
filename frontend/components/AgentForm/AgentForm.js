import { useState, useEffect } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { GENDER_SPECIFIC_OPTIONS, HAIR_COLORS } from "../../constants";
import TabNavigation from "./TabNavigation";
import BasicInfoTab from "./BasicInfoTab";
import AppearanceTab from "./AppearanceTab";
import PersonalityTab from "./PersonalityTab";
import { normalizeImageUrl } from "../../utils";

export default function AgentForm({ agentId, onSave, onCancel, onDelete, onAgentUpdate }) {
	const { fetchWithAuth } = useAuth();
	const [name, setName] = useState("");
	const [description, setDescription] = useState("");
	const [gender, setGender] = useState("");
	const [relationshipStatus, setRelationshipStatus] = useState("");
	const [background, setBackground] = useState("");
	const [hairStyle, setHairStyle] = useState("");
	const [hairColor, setHairColor] = useState("");
	const [eyeColor, setEyeColor] = useState("");
	const [ethnicity, setEthnicity] = useState("");
	const [age, setAge] = useState(30);
	const [bodyType, setBodyType] = useState("");
	const [clothing, setClothing] = useState("");
	const [selectedPersonalities, setSelectedPersonalities] = useState([]);
	const [selectedRoles, setSelectedRoles] = useState([]);
	const [selectedTones, setSelectedTones] = useState([]);
	const [firstPerson, setFirstPerson] = useState("");
	const [firstPersonOther, setFirstPersonOther] = useState("");
	const [personalities, setPersonalities] = useState([]);
	const [roles, setRoles] = useState([]);
	const [tones, setTones] = useState([]);
	const [loading, setLoading] = useState(false);
	const [deleting, setDeleting] = useState(false);
	const [error, setError] = useState(null);
	const [imageUrl, setImageUrl] = useState("");
	const [imageSeed, setImageSeed] = useState(null);
	const [isGeneratingImage, setIsGeneratingImage] = useState(false);
	const [isDeletingImage, setIsDeletingImage] = useState(false);
	const [isModalOpen, setIsModalOpen] = useState(false);
	const [isLogModalOpen, setIsLogModalOpen] = useState(false);
	const [generationLog, setGenerationLog] = useState(null);
	const [isLoadingLog, setIsLoadingLog] = useState(false);
	const [progress, setProgress] = useState(0);
	const [pollingIntervalId, setPollingIntervalId] = useState(null);
	const [hairStyleOptions, setHairStyleOptions] = useState(GENDER_SPECIFIC_OPTIONS[""].hairStyles);
	const [bodyTypeOptions, setBodyTypeOptions] = useState(GENDER_SPECIFIC_OPTIONS[""].bodyTypes);
	const [clothingOptions, setClothingOptions] = useState(GENDER_SPECIFIC_OPTIONS[""].clothings);
	const [relationshipOptions, setRelationshipOptions] = useState(GENDER_SPECIFIC_OPTIONS[""].relationships);
	const [firstPersonOptions, setFirstPersonOptions] = useState(GENDER_SPECIFIC_OPTIONS[""].firstPersons);
	const [activeTab, setActiveTab] = useState('basic');

	const isEditMode = agentId !== null;

	useEffect(() => {
		const options = GENDER_SPECIFIC_OPTIONS[gender] || GENDER_SPECIFIC_OPTIONS[""];
		setHairStyleOptions(options.hairStyles);
		setBodyTypeOptions(options.bodyTypes);
		setClothingOptions(options.clothings);
		setRelationshipOptions(options.relationships);
		setFirstPersonOptions(options.firstPersons);

		if (!options.hairStyles.some((opt) => opt.value === hairStyle)) {
			setHairStyle("");
		}
		if (!options.bodyTypes.some((opt) => opt.value === bodyType)) {
			setBodyType("");
		}
		if (!options.clothings.some((opt) => opt.value === clothing)) {
			setClothing("");
		}
		if (!options.relationships.some((opt) => opt.value === relationshipStatus)) {
			setRelationshipStatus("");
		}
		if (!options.firstPersons.some((opt) => opt.value === firstPerson) && firstPerson !== "agent_name" && firstPerson !== "other") {
			setFirstPerson("");
		}
	}, [gender, hairStyle, bodyType, clothing, relationshipStatus, firstPerson]);

	const openModal = () => {
		if (imageUrl) {
			setIsModalOpen(true);
		}
	};

	const closeModal = () => {
		setIsModalOpen(false);
	};

	useEffect(() => {
		const fetchTags = async () => {
			try {
				const [personalitiesRes, rolesRes, tonesRes] = await Promise.all([
					fetchWithAuth(`/api/v1/tags/personalities`),
					fetchWithAuth(`/api/v1/tags/roles`),
					fetchWithAuth(`/api/v1/tags/tones`),
				]);

				if (personalitiesRes.ok && rolesRes.ok && tonesRes.ok) {
					setPersonalities(await personalitiesRes.json());
					setRoles(await rolesRes.json());
					setTones(await tonesRes.json());
				}
			} catch (err) {
				console.error("Failed to fetch tags:", err);
				setError("タグの読み込みに失敗しました。");
			}
		};

		fetchTags();
	}, [fetchWithAuth]);

	useEffect(() => {
		if (isEditMode) {
			const fetchAgent = async () => {
				setLoading(true);
				try {
					const response = await fetchWithAuth(`/api/v1/agents/${agentId}`);

					if (!response.ok) {
						throw new Error("エージェント情報の取得に失敗しました");
					}

					const data = await response.json();
					setName(data.name);
					setDescription(data.description || "");
					setGender(data.gender || "");
					setRelationshipStatus(data.relationship_status || "");
					setBackground(data.background || "");
					setHairStyle(data.hair_style || "");
					setHairColor(data.hair_color || "");
					setEyeColor(data.eye_color || "");
					setEthnicity(data.ethnicity || "");
					setAge(data.age || 30);
					setBodyType(data.body_type || "");
					setClothing(data.clothing || "");
					setImageUrl(data.image_url || "");
					setImageSeed(data.image_seed || null);
					setFirstPerson(data.first_person || "");
					setFirstPersonOther(data.first_person_other || "");
					setSelectedPersonalities(data.personalities?.map((p) => p.id) || []);
					setSelectedRoles(data.roles?.map((r) => r.id) || []);
					setSelectedTones(data.tones?.map((t) => t.id) || []);
				} catch (err) {
					setError(err.message);
				} finally {
					setLoading(false);
				}
			};
			fetchAgent();
		}
	}, [agentId, isEditMode, fetchWithAuth]);

	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		setError(null);

		try {
			const url = isEditMode ? `/api/v1/agents/${agentId}` : `/api/v1/agents/`;
			const method = isEditMode ? "PUT" : "POST";

			// Prepare the request body
			const requestBody = {
				name,
				description,
				gender,
				relationship_status: relationshipStatus,
				background,
				hair_style: hairStyle,
				hair_color: hairColor,
				eye_color: eyeColor,
				ethnicity: ethnicity,
				age: parseInt(age, 10),
				body_type: bodyType,
				clothing: clothing,
				personality_ids: selectedPersonalities,
				role_ids: selectedRoles,
				tone_ids: selectedTones,
				image_url: imageUrl,
				first_person: firstPerson,
				first_person_other: firstPersonOther,
			};

			// Always include image_seed in the request, even if it's null
			// This ensures the backend will update the field properly
			if (isEditMode || imageSeed !== undefined) {
				requestBody.image_seed = imageSeed;
			}

			const response = await fetchWithAuth(url, {
				method: method,
				body: JSON.stringify(requestBody),
			});

			if (!response.ok) {
				throw new Error(isEditMode ? "エージェントの更新に失敗しました" : "エージェントの作成に失敗しました");
			}

			const savedAgent = await response.json();
			onSave(savedAgent);
			if (onAgentUpdate) {
				onAgentUpdate();
			}
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	const handleTagChange = (setter, selectedIds, id) => {
		if (selectedIds.includes(id)) {
			setter(selectedIds.filter((selectedId) => selectedId !== id));
		} else {
			setter([...selectedIds, id]);
		}
	};

	const handleDelete = async () => {
		if (!window.confirm("本当にこのエージェントを削除しますか？")) {
			return;
		}

		setDeleting(true);
		setError(null);

		try {
			const response = await fetchWithAuth(`/api/v1/agents/${agentId}`, {
				method: "DELETE",
			});

			if (!response.ok) {
				throw new Error("エージェントの削除に失敗しました");
			}

			onDelete();
		} catch (err) {
			setError(err.message);
		} finally {
			setDeleting(false);
		}
	};

	const pollGenerationStatus = async () => {
		try {
			const response = await fetchWithAuth(`/api/v1/agents/${agentId}/generation-log`);

			if (!response.ok) {
				console.error("Failed to fetch generation log");
				return;
			}

			const logData = await response.json();
			setGenerationLog(logData);

			if (logData.progress) {
				setProgress(parseFloat(logData.progress));
			}

			if (logData.status === "completed" || logData.status === "failed" || logData.status === "cached") {
				setIsGeneratingImage(false);
				if (pollingIntervalId) {
					clearInterval(pollingIntervalId);
					setPollingIntervalId(null);
				}
				setProgress(100);

				if (logData.status === "completed" && logData.image_url) {
					setImageUrl(logData.image_url);
					// Set the seed value if it's available in the log
					if (logData.image_seed !== undefined) {
						setImageSeed(logData.image_seed);
					}
					if (onAgentUpdate) onAgentUpdate();
				} else if (logData.status === "failed") {
					setError(logData.error || "画像の生成に失敗しました。");
				}
			}
		} catch (err) {
			setError("ログの取得中にエラーが発生しました。");
			setIsGeneratingImage(false);
			if (pollingIntervalId) {
				clearInterval(pollingIntervalId);
				setPollingIntervalId(null);
			}
		}
	};

	const handleGenerateImage = async () => {
		if (!isEditMode) {
			setError("エージェントを保存してから画像を生成してください。");
			return;
		}

		setIsGeneratingImage(true);
		setError(null);
		setProgress(0);
		setGenerationLog(null);

		try {
			const response = await fetchWithAuth(`/api/v1/agents/${agentId}/generate-image`, {
				method: "POST",
				body: JSON.stringify({ force_regenerate: true }),
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || "画像生成の開始に失敗しました");
			}

			const intervalId = setInterval(pollGenerationStatus, 2000);
			setPollingIntervalId(intervalId);

		} catch (err) {
			setError(err.message);
			setIsGeneratingImage(false);
		}
	};

	const handleDeleteImage = async () => {
		if (!window.confirm("本当にこの画像を削除しますか？")) {
			return;
		}

		setIsDeletingImage(true);
		setError(null);

		try {
			console.log(`画像削除開始: エージェントID ${agentId}`);
			const response = await fetchWithAuth(`/api/v1/agents/${agentId}/image`, {
				method: "DELETE",
			});

			if (!response.ok) {
				const errorData = await response.json();
				console.error("画像削除エラー:", errorData);
				throw new Error(errorData.detail || "画像の削除に失敗しました");
			}

			console.log("画像削除成功");
			setImageUrl("");
			setImageSeed(null);
			if (onAgentUpdate) {
				onAgentUpdate();
			}
		} catch (err) {
			console.error("画像削除処理でエラー:", err);
			setError(err.message);
		} finally {
			setIsDeletingImage(false);
		}
	};

	const handleViewGenerationLog = async () => {
		if (!isEditMode) {
			return;
		}

		setIsLoadingLog(true);
		setGenerationLog(null);
		setIsLogModalOpen(true);

		try {
			const response = await fetchWithAuth(`/api/v1/agents/${agentId}/generation-log`);

			if (!response.ok) {
				throw new Error("ログの取得に失敗しました");
			}

			const data = await response.json();
			setGenerationLog(data);
		} catch (err) {
			console.error("生成ログの取得エラー:", err);
			setGenerationLog({
				error: err.message || "ログの取得に失敗しました"
			});
		} finally {
			setIsLoadingLog(false);
		}
	};

	const closeLogModal = () => {
		setIsLogModalOpen(false);
		setGenerationLog(null);
	};

	if (loading && isEditMode) {
		return <div className="text-white">読み込み中...</div>;
	}

	const renderTabContent = () => {
		switch (activeTab) {
			case 'basic':
				return <BasicInfoTab {...{ name, setName, description, setDescription, relationshipStatus, setRelationshipStatus, relationshipOptions, firstPerson, setFirstPerson, firstPersonOther, setFirstPersonOther, firstPersonOptions, background, setBackground, imageUrl, openModal }} />;
			case 'appearance':
				return <AppearanceTab {...{ gender, setGender, age, setAge, ethnicity, setEthnicity, bodyType, setBodyType, bodyTypeOptions, hairStyle, setHairStyle, hairStyleOptions, hairColor, setHairColor, eyeColor, setEyeColor, clothing, setClothing, clothingOptions, isEditMode, handleGenerateImage, isGeneratingImage, isDeletingImage, progress, imageUrl, handleDeleteImage, imageSeed, setImageSeed, openModal, generationLog }} />;
			case 'personality':
				return <PersonalityTab {...{ personalities, selectedPersonalities, handleTagChange, setSelectedPersonalities, roles, selectedRoles, setSelectedRoles, tones, selectedTones, setSelectedTones }} />;
			default:
				return null;
		}
	};

	return (
		<div className="bg-gray-800 rounded-lg p-6 h-full overflow-y-auto">
			<h1 className="text-2xl font-bold text-white mb-6">{isEditMode ? "エージェントを編集" : "新しいエージェントを作成"}</h1>

			<form onSubmit={handleSubmit}>
				{error && <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>}
				<div className="flex flex-col md:flex-row">
					<TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />
					<div className="w-full md:w-3/4 p-6 bg-gray-900 rounded-lg mt-4 md:mt-0">
						{renderTabContent()}
					</div>
				</div>

				<div className="flex items-center justify-between pt-4 mt-8">
					<div>
						<button type="submit" disabled={loading || deleting} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400">
							{loading ? "保存中..." : "保存"}
						</button>
						<button type="button" onClick={onCancel} className="ml-2 bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
							キャンセル
						</button>
					</div>
					{isEditMode && (
						<button type="button" onClick={handleDelete} disabled={deleting} className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400">
							{deleting ? "削除中..." : "削除"}
						</button>
					)}
				</div>
			</form>

			{isModalOpen && (
				<div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 transition-opacity duration-300 ease-in-out" onClick={closeModal}>
					<div className="relative max-w-4xl max-h-4xl" onClick={(e) => e.stopPropagation()}>
						<img src={normalizeImageUrl(imageUrl)} alt="Agent" className="w-full h-full object-contain rounded-lg" />
						<button onClick={closeModal} className="absolute top-2 right-2 text-white text-4xl font-bold hover:text-gray-300 focus:outline-none">&times;</button>
					</div>
				</div>
			)}

			{isLogModalOpen && (
				<div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 transition-opacity duration-300 ease-in-out" onClick={closeLogModal}>
					<div className="relative bg-gray-800 rounded-lg max-w-4xl max-h-[80vh] overflow-hidden shadow-2xl" onClick={(e) => e.stopPropagation()}>
						<div className="sticky top-0 bg-gray-900 px-6 py-4 border-b border-gray-700 flex justify-between items-center">
							<h2 className="text-xl font-bold text-white">画像生成ログ</h2>
							<button onClick={closeLogModal} className="text-gray-400 hover:text-white text-2xl font-bold focus:outline-none">&times;</button>
						</div>
						
						<div className="p-6 overflow-y-auto max-h-[calc(80vh-80px)]">
							{isLoadingLog ? (
								<div className="flex items-center justify-center py-8">
									<svg className="animate-spin h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
										<circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
										<path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
									</svg>
									<span className="ml-3 text-gray-300">ログを読み込み中...</span>
								</div>
							) : generationLog ? (
								<div className="space-y-6">
									{generationLog.error ? (
										<div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
											<p className="text-red-400">{generationLog.error}</p>
										</div>
									) : generationLog.message ? (
										<div className="bg-gray-700 rounded-lg p-4">
											<p className="text-gray-300">{generationLog.message}</p>
										</div>
									) : (
										<>
											<div className="bg-gray-700 rounded-lg p-4 space-y-2">
												<h3 className="text-lg font-semibold text-white mb-3">基本情報</h3>
												<div className="grid grid-cols-2 gap-4 text-sm">
													<div>
														<span className="text-gray-400">ステータス:</span>
														<span className={`ml-2 font-medium ${
															generationLog.status === 'completed' ? 'text-green-400' :
															generationLog.status === 'failed' ? 'text-red-400' :
															generationLog.status === 'cached' ? 'text-blue-400' :
															'text-yellow-400'
														}`}>
															{generationLog.status === 'completed' ? '✓ 完了' :
															 generationLog.status === 'failed' ? '✗ 失敗' :
															 generationLog.status === 'cached' ? '◆ キャッシュ使用' :
															 '● 処理中'}
														</span>
													</div>
													<div>
														<span className="text-gray-400">プロバイダー:</span>
														<span className="ml-2 text-white">{generationLog.provider}</span>
													</div>
													{generationLog.started_at && (
														<div>
															<span className="text-gray-400">開始時刻:</span>
															<span className="ml-2 text-white">{new Date(generationLog.started_at).toLocaleString('ja-JP')}</span>
														</div>
													)}
													{generationLog.total_time && (
														<div>
															<span className="text-gray-400">処理時間:</span>
															<span className="ml-2 text-white">{generationLog.total_time}</span>
														</div>
													)}
												</div>
											</div>

											{generationLog.prompt && (
												<div className="bg-gray-700 rounded-lg p-4">
													<h3 className="text-lg font-semibold text-white mb-3">プロンプト</h3>
													<div className="space-y-3">
														<div>
															<h4 className="text-sm font-medium text-gray-400 mb-1">メインプロンプト:</h4>
															<p className="text-sm text-gray-200 bg-gray-800 rounded p-3 font-mono">{generationLog.prompt}</p>
														</div>
														{generationLog.negative_prompt && (
															<div>
																<h4 className="text-sm font-medium text-gray-400 mb-1">ネガティブプロンプト:</h4>
																<p className="text-sm text-gray-200 bg-gray-800 rounded p-3 font-mono break-all">{generationLog.negative_prompt}</p>
															</div>
														)}
													</div>
												</div>
											)}

											{generationLog.steps && generationLog.steps.length > 0 && (
												<div className="bg-gray-700 rounded-lg p-4">
													<h3 className="text-lg font-semibold text-white mb-3">処理ステップ</h3>
													<div className="space-y-3">
														{generationLog.steps.map((step, index) => (
															<div key={index} className="flex items-start space-x-3">
																<div className={`mt-1 w-2 h-2 rounded-full ${
																	step.status === 'completed' ? 'bg-green-500' :
																	step.status === 'failed' ? 'bg-red-500' :
																	step.status === 'cached' ? 'bg-blue-500' :
																	'bg-yellow-500'
																}`}></div>
																<div className="flex-1">
																	<div className="flex justify-between items-start">
																		<h4 className="text-sm font-medium text-white">
																			{step.step === 'prompt_generation' ? 'プロンプト生成' :
																			 step.step === 'image_generation' ? '画像生成' :
																			 step.step === 'save_image' ? '画像保存' :
																			 step.step === 'cache_check' ? 'キャッシュ確認' :
																			 step.step}
																		</h4>
																		{step.generation_time && (
																			<span className="text-xs text-gray-400">{step.generation_time}</span>
																		)}
																	</div>
																	{step.message && (
																		<p className="text-sm text-gray-300 mt-1">{step.message}</p>
																	)}
																	{step.error && (
																		<p className="text-sm text-red-400 mt-1">{step.error}</p>
																	)}
																	{step.timestamp && (
																		<p className="text-xs text-gray-500 mt-1">{new Date(step.timestamp).toLocaleTimeString('ja-JP')}</p>
																	)}
																</div>
															</div>
														))}
													</div>
												</div>
											)}

											{generationLog.error && (
												<div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
													<h3 className="text-lg font-semibold text-red-400 mb-2">エラー</h3>
													<p className="text-sm text-red-300">{generationLog.error}</p>
												</div>
											)}
										</>
									)}
								</div>
							) : null}
						</div>
					</div>
				</div>
			)}
		</div>
	);
}