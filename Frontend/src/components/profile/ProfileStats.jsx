function ProfileStats({ profile }) {
  const stats = [
    { label: 'Gönderi', value: profile?.total_posts },
    { label: 'Takipçi', value: profile?.total_followers },
    { label: 'Takip', value: profile?.total_following },
    { label: 'Beğeni', value: profile?.total_likes }
  ];

  return (
    <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <div key={index} className="bg-gray-700/30 p-4 rounded-xl text-center">
          <div className="text-2xl font-bold text-white">{stat.value}</div>
          <div className="text-sm text-gray-400">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}

export default ProfileStats; 