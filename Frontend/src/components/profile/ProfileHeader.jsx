import { MapPinIcon, CalendarIcon } from '@heroicons/react/24/outline';

function ProfileHeader({ profile, meta, onEditClick, showFollowButton, isFollowing, onFollowToggle }) {
  return (
    <div className="flex flex-col space-y-4">
      <div className="flex items-start justify-between">
        {/* Profil Fotoğrafı ve Bilgiler */}
        <div className="flex space-x-3">
          <img
            src={profile?.profile_picture}
            alt={profile?.username}
            className="h-16 w-16 rounded-xl object-cover ring-2 ring-gray-700"
          />
          
          <div>
            <h1 className="text-lg font-bold text-white">{profile?.full_name}</h1>
            <p className="text-sm text-purple-400">@{profile?.username}</p>
            
            <div className="flex items-center space-x-3 mt-1 text-xs text-gray-400">
              {profile?.location && (
                <div className="flex items-center">
                  <MapPinIcon className="h-3 w-3 mr-1" />
                  {profile.location}
                </div>
              )}
              <div className="flex items-center">
                <CalendarIcon className="h-3 w-3 mr-1" />
                {profile?.join_date}
              </div>
            </div>
          </div>
        </div>

        {/* Butonlar */}
        {(showFollowButton || profile?.is_owner) && (
          <button
            onClick={showFollowButton ? onFollowToggle : onEditClick}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors
              ${showFollowButton
                ? isFollowing
                  ? 'bg-gray-700 text-gray-300 hover:bg-red-600/80 hover:text-white'
                  : 'bg-purple-600/90 text-white hover:bg-purple-600'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
          >
            {showFollowButton
              ? isFollowing ? 'Takibi Bırak' : 'Takip Et'
              : 'Profili Düzenle'}
          </button>
        )}
      </div>

      {!profile?.is_email_verified && meta?.is_own_profile && (
        <div className="text-xs bg-yellow-500/10 text-yellow-500 px-3 py-1.5 rounded-lg">
          Email adresinizi doğrulamayı unutmayın
        </div>
      )}
    </div>
  );
}

export default ProfileHeader; 