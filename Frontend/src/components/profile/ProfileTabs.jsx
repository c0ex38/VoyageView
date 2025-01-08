function ProfileTabs({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'about', label: 'Hakkında' },
    { id: 'posts', label: 'Gönderiler' }
  ];

  return (
    <div className="border-b border-gray-700">
      <nav className="-mb-px flex space-x-8 px-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
              ${activeTab === tab.id 
                ? 'border-purple-500 text-purple-500' 
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'}
            `}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
}

export default ProfileTabs; 