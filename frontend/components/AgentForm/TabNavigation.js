import React from 'react';

const TabNavigation = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'basic', label: '基本情報' },
    { id: 'appearance', label: '外見' },
    { id: 'personality', label: '性格・口調' },
  ];

  return (
    <div className="w-full md:w-1/4 md:p-4">
      <nav className="flex space-x-1 md:flex-col md:space-x-0 md:space-y-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
              activeTab === tab.id
                ? 'bg-gray-900 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
};

export default TabNavigation;