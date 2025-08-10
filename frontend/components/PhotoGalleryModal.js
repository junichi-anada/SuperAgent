import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { normalizeImageUrl } from "../utils";

const PhotoGalleryModal = ({ agent, isOpen, onClose }) => {
	const { fetchWithAuth } = useAuth();
	const [images, setImages] = useState([]);
	const [selectedImage, setSelectedImage] = useState(null);
	const [uploading, setUploading] = useState(false);
	const [loading, setLoading] = useState(false);

	useEffect(() => {
		if (isOpen && agent) {
			fetchImages();
		}
	}, [isOpen, agent]);

	const fetchImages = async () => {
		setLoading(true);
		try {
			const response = await fetchWithAuth(`/api/v1/agents/${agent.id}/images`);
			if (response.ok) {
				const data = await response.json();
				setImages(data);
				// 最初に表示する画像を設定
				if (data.length > 0) {
					setSelectedImage(data.find(img => img.is_primary) || data[0]);
				}
			}
		} catch (error) {
			console.error("Error fetching images:", error);
		} finally {
			setLoading(false);
		}
	};

	const handleImageUpload = async (event) => {
		const file = event.target.files[0];
		if (!file) return;

		setUploading(true);
		const formData = new FormData();
		formData.append("file", file);
		formData.append("is_primary", images.length === 0 ? "true" : "false");

		try {
			const response = await fetchWithAuth(`/api/v1/agents/${agent.id}/images`, {
				method: "POST",
				body: formData,
			});

			if (response.ok) {
				await fetchImages();
			} else {
				console.error("Failed to upload image");
			}
		} catch (error) {
			console.error("Error uploading image:", error);
		} finally {
			setUploading(false);
			// ファイル入力をリセット
			event.target.value = "";
		}
	};

	const handleDeleteImage = async (imageId) => {
		if (!confirm("この画像を削除してもよろしいですか？")) return;

		try {
			const response = await fetchWithAuth(`/api/v1/agents/${agent.id}/images/${imageId}`, {
				method: "DELETE",
			});

			if (response.ok) {
				await fetchImages();
			} else {
				console.error("Failed to delete image");
			}
		} catch (error) {
			console.error("Error deleting image:", error);
		}
	};

	const handleSetPrimary = async (imageId) => {
		try {
			const response = await fetchWithAuth(`/api/v1/agents/${agent.id}/images/${imageId}/set-primary`, {
				method: "PUT",
			});

			if (response.ok) {
				await fetchImages();
			} else {
				console.error("Failed to set primary image");
			}
		} catch (error) {
			console.error("Error setting primary image:", error);
		}
	};

	if (!isOpen) return null;

	return (
		<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
			<div className="bg-gray-800 rounded-lg max-w-4xl max-h-[90vh] w-full mx-4 flex flex-col" onClick={(e) => e.stopPropagation()}>
				{/* ヘッダー */}
				<div className="p-4 border-b border-gray-700 flex justify-between items-center">
					<h2 className="text-2xl font-bold">{agent.name}のフォトギャラリー</h2>
					<button onClick={onClose} className="text-gray-400 hover:text-white">
						<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>

				{/* コンテンツ */}
				<div className="flex-1 overflow-auto p-4">
					{loading ? (
						<div className="text-center py-8">読み込み中...</div>
					) : images.length === 0 ? (
						<div className="text-center py-8">
							<p className="text-gray-400 mb-4">まだ画像がアップロードされていません</p>
						</div>
					) : (
						<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
							{/* メイン画像表示エリア */}
							<div className="space-y-4">
								{selectedImage && (
									<>
										<div className="relative bg-gray-900 rounded-lg overflow-hidden">
											<img
												src={normalizeImageUrl(selectedImage.image_url)}
												alt={agent.name}
												className="w-full h-96 object-contain"
											/>
											{selectedImage.is_primary && (
												<div className="absolute top-2 left-2 bg-green-600 text-white px-2 py-1 rounded text-sm">
													メイン画像
												</div>
											)}
										</div>
										<div className="flex gap-2">
											{!selectedImage.is_primary && (
												<button
													onClick={() => handleSetPrimary(selectedImage.id)}
													className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
												>
													メイン画像に設定
												</button>
											)}
											<button
												onClick={() => handleDeleteImage(selectedImage.id)}
												className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded"
											>
												削除
											</button>
										</div>
									</>
								)}
							</div>

							{/* サムネイル一覧 */}
							<div className="space-y-4">
								<div className="grid grid-cols-3 gap-2 max-h-96 overflow-y-auto">
									{images.map((image) => (
										<div
											key={image.id}
											className={`relative cursor-pointer rounded overflow-hidden ${
												selectedImage?.id === image.id ? "ring-2 ring-blue-500" : ""
											}`}
											onClick={() => setSelectedImage(image)}
										>
											<img
												src={normalizeImageUrl(image.image_url)}
												alt=""
												className="w-full h-24 object-cover hover:opacity-80 transition-opacity"
											/>
											{image.is_primary && (
												<div className="absolute top-1 left-1 bg-green-600 text-white text-xs px-1 rounded">
													メイン
												</div>
											)}
										</div>
									))}
								</div>

								{/* アップロードボタン */}
								<div className="mt-4">
									<label className="block w-full">
										<input
											type="file"
											accept="image/*"
											onChange={handleImageUpload}
											disabled={uploading}
											className="hidden"
										/>
										<div className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded text-center cursor-pointer">
											{uploading ? "アップロード中..." : "新しい画像をアップロード"}
										</div>
									</label>
								</div>
							</div>
						</div>
					)}

					{/* 画像がない場合のアップロードボタン */}
					{images.length === 0 && !loading && (
						<div className="text-center">
							<label className="inline-block">
								<input
									type="file"
									accept="image/*"
									onChange={handleImageUpload}
									disabled={uploading}
									className="hidden"
								/>
								<div className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded cursor-pointer">
									{uploading ? "アップロード中..." : "画像をアップロード"}
								</div>
							</label>
						</div>
					)}
				</div>
			</div>
		</div>
	);
};

export default PhotoGalleryModal;