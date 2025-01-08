function ProfileProgress({ profile, meta }) {
  if (!meta?.is_own_profile) return null;

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">Profil Tamamlanma</span>
        <span className="text-sm font-medium text-purple-400">
          {profile?.profile_completion}%
        </span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full">
        <div 
          className="h-full bg-purple-500 rounded-full transition-all duration-500"
          style={{ width: `${profile?.profile_completion}%` }}
        />
      </div>
    </div>
  );
}

export default ProfileProgress; 