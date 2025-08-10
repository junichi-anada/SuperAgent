import React, { useState } from 'react';
import { HAIR_COLORS } from '../../constants';
import { Copy } from 'lucide-react';
import { normalizeImageUrl } from '../../utils';

const DebugInfo = ({ log }) => {
	if (!log) return null;

	const copyToClipboard = (text) => {
		navigator.clipboard.writeText(text);
	};

	return (
		<div className="bg-gray-900 p-3 rounded-lg space-y-3 text-xs">
			<h3 className="font-semibold text-base text-white mb-2">画像生成デバッグ情報</h3>
			
			<div className="space-y-1">
				<div className="flex justify-between">
					<span className="text-gray-400">ステータス:</span>
					<span className={`font-medium ${
						log.status === 'completed' ? 'text-green-400' :
						log.status === 'failed' ? 'text-red-400' :
						log.status === 'cached' ? 'text-blue-400' :
						'text-yellow-400'
					}`}>
						{log.status}
					</span>
				</div>
				<div className="flex justify-between">
					<span className="text-gray-400">プロバイダー:</span>
					<span className="text-white">{log.provider}</span>
				</div>
				{log.total_time && (
					<div className="flex justify-between">
						<span className="text-gray-400">生成時間:</span>
						<span className="text-white">{log.total_time}</span>
					</div>
				)}
				{log.image_seed && (
					<div className="flex justify-between items-center">
						<span className="text-gray-400">シード値:</span>
						<div className="flex items-center gap-1">
							<span className="text-white">{log.image_seed}</span>
							<button onClick={() => copyToClipboard(log.image_seed)} className="text-gray-400 hover:text-white">
								<Copy size={12} />
							</button>
						</div>
					</div>
				)}
			</div>

			{log.prompt && (
				<div className="border-t border-gray-700 pt-2">
					<h4 className="text-sm font-medium text-gray-300">プロンプト</h4>
					<p className="font-mono bg-gray-800 p-2 rounded break-all mt-1">{log.prompt}</p>
				</div>
			)}

			{log.negative_prompt && (
				<div className="border-t border-gray-700 pt-2">
					<h4 className="text-sm font-medium text-gray-300">ネガティブプロンプト</h4>
					<p className="font-mono bg-gray-800 p-2 rounded break-all mt-1">{log.negative_prompt}</p>
				</div>
			)}

			{log.error && (
				<div className="border-t border-gray-700 pt-2">
					<h4 className="text-sm font-medium text-red-400">エラー</h4>
					<p className="font-mono bg-red-900/20 text-red-400 p-2 rounded break-all mt-1">{log.error}</p>
				</div>
			)}
		</div>
	);
};

const AppearanceTab = ({
  gender,
  setGender,
  age,
  setAge,
  height,
  setHeight,
  ethnicity,
  setEthnicity,
  bodyType,
  setBodyType,
  bodyTypeOptions,
  hairStyle,
  setHairStyle,
  hairStyleOptions,
  hairColor,
  setHairColor,
  eyeColor,
  setEyeColor,
  clothing,
  setClothing,
  clothingOptions,
  isEditMode,
  handleGenerateImage,
  isGeneratingImage,
  isDeletingImage,
  progress,
  imageUrl,
  handleDeleteImage,
  imageSeed,
  setImageSeed,
  openModal,
  generationLog,
}) => {
  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Left Column: Image and Generation */}
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-3">プロフィール画像</h3>
            
            {imageUrl ? (
              <div className="mb-4">
                <div
                  className="relative inline-block cursor-pointer group"
                  onClick={openModal}
                >
                  <img
                    src={normalizeImageUrl(imageUrl)}
                    alt="Agent Profile"
                    className="w-48 h-48 object-cover rounded-lg shadow-lg transition-transform duration-200 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 rounded-lg transition-opacity duration-200 flex items-center justify-center">
                    <svg className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                    </svg>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mb-4">
                <div className="w-48 h-48 bg-gray-700 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <svg className="w-16 h-16 text-gray-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <p className="text-gray-500 text-sm">画像未生成</p>
                  </div>
                </div>
              </div>
            )}
            
            <p className="text-gray-300 text-sm mb-3">
              エージェントの外見情報から自動的に画像を生成します
            </p>
            <div className="flex space-x-2">
              {!imageUrl && (
                <button type="button" onClick={handleGenerateImage} disabled={isGeneratingImage || isDeletingImage || !isEditMode} className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400 flex items-center">
                  {isGeneratingImage ? "生成中..." : "画像を生成"}
                </button>
              )}
              {imageUrl && (
                <button type="button" onClick={handleDeleteImage} disabled={isGeneratingImage || isDeletingImage || !isEditMode} className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400 flex items-center">
                  {isDeletingImage ? "削除中..." : "画像を削除"}
                </button>
              )}
            </div>
            {isGeneratingImage && (
              <div className="mt-4 w-full bg-gray-600 rounded-full h-2.5">
                <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${progress}%` }}></div>
                <p className="text-sm text-white text-center mt-1">{progress.toFixed(1)}%</p>
              </div>
            )}
            {imageUrl && (
             <div className="mt-4">
               <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="image_seed">
                 画像シード値
               </label>
               <p className="text-gray-400 text-xs mb-2">この値を固定すると、同じような特徴を持つ画像を再生成しやすくなります。-1はランダムを意味します。</p>
               <input
                 id="image_seed"
                 type="number"
                 value={imageSeed === null || imageSeed === undefined ? '' : imageSeed}
                 onChange={(e) => setImageSeed(e.target.value === '' ? null : Number(e.target.value))}
                 className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline"
                 placeholder="ランダム"
               />
             </div>
           )}
          </div>
        </div>

        {/* Right Column: Debug Info */}
        <div className="space-y-4">
          {generationLog && (
            <div className="bg-gray-800 rounded-lg p-4">
              <DebugInfo log={generationLog} />
            </div>
          )}
        </div>
      </div>

      {/* Bottom Section: Appearance Settings */}
      <div className="space-y-4">
        <div>
          <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="gender">
            性別 <span className="text-gray-500 text-xs font-normal">（任意）</span>
          </label>
          <p className="text-gray-400 text-xs mb-2">画像生成と応答に影響します。</p>
          <select id="gender" value={gender} onChange={(e) => setGender(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
            <option value="">選択してください</option>
            <option value="male">男性</option>
            <option value="female">女性</option>
            <option value="neutral">中性</option>
            <option value="other">その他</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="age">
              年齢: {age}歳 <span className="text-gray-500 text-xs font-normal">（任意）</span>
            </label>
            <input id="age" type="range" min="18" max="60" value={age} onChange={(e) => setAge(e.target.value)} className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer" />
          </div>
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="height">
              身長: {height}cm <span className="text-gray-500 text-xs font-normal">（任意）</span>
            </label>
            <input id="height" type="range" min="150" max="200" value={height} onChange={(e) => setHeight(e.target.value)} className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="ethnicity">
              系統 <span className="text-gray-500 text-xs font-normal">（任意）</span>
            </label>
            <select id="ethnicity" value={ethnicity} onChange={(e) => setEthnicity(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
              <option value="">選択してください</option>
              <option value="asian">アジア系</option>
              <option value="white">白人系</option>
              <option value="black">黒人系</option>
              <option value="hispanic">ヒスパニック系</option>
              <option value="other">その他</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="body_type">
              体型 <span className="text-gray-500 text-xs font-normal">（任意）</span>
            </label>
            <select id="body_type" value={bodyType} onChange={(e) => setBodyType(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
              <option value="">選択してください</option>
              {bodyTypeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="hair_style">
              髪型 <span className="text-gray-500 text-xs font-normal">（任意）</span>
            </label>
            <select id="hair_style" value={hairStyle} onChange={(e) => setHairStyle(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
              <option value="">選択してください</option>
              {hairStyleOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="hair_color">
              髪の色 <span className="text-gray-500 text-xs font-normal">（任意）</span>
            </label>
            <select id="hair_color" value={hairColor} onChange={(e) => setHairColor(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
              <option value="">選択してください</option>
              {HAIR_COLORS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="eye_color">
              目の色 <span className="text-gray-500 text-xs font-normal">（任意）</span>
            </label>
            <select id="eye_color" value={eyeColor} onChange={(e) => setEyeColor(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
              <option value="">選択してください</option>
              <option value="black">ブラック</option>
              <option value="dark brown">ダークブラウン</option>
              <option value="brown">ブラウン</option>
              <option value="light brown">ライトブラウン</option>
              <option value="hazel">ヘーゼル</option>
              <option value="green">グリーン</option>
              <option value="blue">ブルー</option>
              <option value="gray">グレー</option>
              <option value="amber">アンバー</option>
              <option value="violet">バイオレット</option>
              <option value="emerald green">エメラルドグリーン</option>
              <option value="sapphire blue">サファイアブルー</option>
              <option value="honey">ハニー</option>
              <option value="chestnut">チェスナット</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="clothing">
            服装 <span className="text-gray-500 text-xs font-normal">（任意）</span>
          </label>
          <select id="clothing" value={clothing} onChange={(e) => setClothing(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
            <option value="">選択してください</option>
            {clothingOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default AppearanceTab;