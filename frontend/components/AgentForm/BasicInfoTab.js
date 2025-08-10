import React from 'react';
import { normalizeImageUrl } from '../../utils';

const BasicInfoTab = ({
  name,
  setName,
  description,
  setDescription,
  relationshipStatus,
  setRelationshipStatus,
  relationshipOptions,
  firstPerson,
  setFirstPerson,
  firstPersonOther,
  setFirstPersonOther,
  firstPersonOptions,
  background,
  setBackground,
  imageUrl,
  openModal,
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-start space-x-4">
        <div className="w-32 h-32 bg-gray-700 rounded-full flex-shrink-0 flex items-center justify-center">
          {imageUrl ? (
            <img src={normalizeImageUrl(imageUrl)} alt="Agent" className="w-32 h-32 rounded-full object-cover cursor-pointer" onClick={openModal} />
          ) : (
            <span className="text-gray-400">No Image</span>
          )}
        </div>
        <div className="flex-grow space-y-4">
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="name">
              名前 <span className="text-red-500">*</span>
            </label>
            <p className="text-gray-400 text-xs mb-2">エージェントのユニークな名前です。</p>
            <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline" placeholder="エージェントの名前" required />
          </div>
          <div>
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="description">
              説明 <span className="text-gray-500 text-xs font-normal">（任意）</span>
            </label>
            <p className="text-gray-400 text-xs mb-2">エージェントの簡単な説明です。</p>
            <textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline" placeholder="エージェントの説明" rows="2" />
          </div>
        </div>
      </div>

      <div>
        <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="relationship">
          関係 <span className="text-gray-500 text-xs font-normal">（任意）</span>
        </label>
        <p className="text-gray-400 text-xs mb-2">ユーザーとの関係性を設定します。</p>
        <select id="relationship" value={relationshipStatus} onChange={(e) => setRelationshipStatus(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
          <option value="">選択してください</option>
          {relationshipOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="first_person">
          一人称 <span className="text-gray-500 text-xs font-normal">（任意）</span>
        </label>
        <p className="text-gray-400 text-xs mb-2">会話で使用する一人称を設定します。</p>
        <div className="flex items-center space-x-2">
          <select id="first_person" value={firstPerson} onChange={(e) => setFirstPerson(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline">
            <option value="">選択してください</option>
            <option value="agent_name">{name || "エージェントの名前"}</option>
            {firstPersonOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
            <option value="other">その他</option>
          </select>
          {firstPerson === "other" && <input type="text" value={firstPersonOther} onChange={(e) => setFirstPersonOther(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline" placeholder="一人称を入力" />}
        </div>
      </div>

      <div>
        <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="background">
          背景設定 <span className="text-gray-500 text-xs font-normal">（任意）</span>
        </label>
        <p className="text-gray-400 text-xs mb-2">エージェントのキャラクター設定や背景情報です。</p>
        <textarea id="background" value={background} onChange={(e) => setBackground(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 bg-gray-700 text-white leading-tight focus:outline-none focus:shadow-outline" placeholder="エージェントの背景や設定" rows="3" />
      </div>
    </div>
  );
};

export default BasicInfoTab;