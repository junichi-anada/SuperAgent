import React from 'react';

const PersonalityTab = ({
  personalities,
  selectedPersonalities,
  handleTagChange,
  setSelectedPersonalities,
  roles,
  selectedRoles,
  setSelectedRoles,
  tones,
  selectedTones,
  setSelectedTones,
}) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-gray-300 text-sm font-bold mb-2">性格 <span className="text-gray-500 text-xs font-normal">（任意・複数選択可）</span></label>
        <p className="text-gray-400 text-xs mb-2">エージェントの基本的な性格特性を選択します。</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {personalities.map((p) => (
            <label key={p.id} className="flex items-center text-white">
              <input type="checkbox" value={p.id} checked={selectedPersonalities.includes(p.id)} onChange={() => handleTagChange(setSelectedPersonalities, selectedPersonalities, p.id)} className="mr-2" />
              {p.name}
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-gray-300 text-sm font-bold mb-2">職業 <span className="text-gray-500 text-xs font-normal">（任意・複数選択可）</span></label>
        <p className="text-gray-400 text-xs mb-2">エージェントの役割や職業を設定します。</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {roles.map((r) => (
            <label key={r.id} className="flex items-center text-white">
              <input type="checkbox" value={r.id} checked={selectedRoles.includes(r.id)} onChange={() => handleTagChange(setSelectedRoles, selectedRoles, r.id)} className="mr-2" />
              {r.name}
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-gray-300 text-sm font-bold mb-2">口調 <span className="text-gray-500 text-xs font-normal">（任意・複数選択可）</span></label>
        <p className="text-gray-400 text-xs mb-2">エージェントの話し方やトーンを設定します。</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {tones.map((t) => (
            <label key={t.id} className="flex items-center text-white">
              <input type="checkbox" value={t.id} checked={selectedTones.includes(t.id)} onChange={() => handleTagChange(setSelectedTones, selectedTones, t.id)} className="mr-2" />
              {t.name}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PersonalityTab;