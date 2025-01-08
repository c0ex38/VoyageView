import { MapPinIcon, CalendarIcon, EnvelopeIcon, UserIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

function AboutSection({ profile, meta = { is_own_profile: false } }) {
  if (!profile) {
    return <div>Yükleniyor...</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Kişisel Bilgiler */}
      <div className="bg-gray-800/50 rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Kişisel Bilgiler</h3>
        <div className="space-y-4">
          <div className="flex items-center text-gray-300">
            <UserIcon className="h-5 w-5 mr-3 text-purple-500" />
            <div>
              <div className="text-sm text-gray-400">Ad Soyad</div>
              <div>{profile.full_name || 'Belirtilmemiş'}</div>
            </div>
          </div>

          <div className="flex items-center text-gray-300">
            <EnvelopeIcon className="h-5 w-5 mr-3 text-purple-500" />
            <div>
              <div className="text-sm text-gray-400">E-posta</div>
              <div>{meta?.is_own_profile ? profile.email : '***********'}</div>
            </div>
          </div>

          {profile.date_of_birth && (
            <div className="flex items-center text-gray-300">
              <CalendarIcon className="h-5 w-5 mr-3 text-purple-500" />
              <div>
                <div className="text-sm text-gray-400">Doğum Tarihi</div>
                <div>
                  {format(new Date(profile.date_of_birth), 'd MMMM yyyy', { locale: tr })}
                </div>
              </div>
            </div>
          )}

          {profile.location && (
            <div className="flex items-center text-gray-300">
              <MapPinIcon className="h-5 w-5 mr-3 text-purple-500" />
              <div>
                <div className="text-sm text-gray-400">Konum</div>
                <div>{profile.location}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Hesap Bilgileri */}
      <div className="bg-gray-800/50 rounded-xl p-6">
        <h3 className="text-lg font-medium text-white mb-4">Hesap Bilgileri</h3>
        <div className="space-y-4">
          <div>
            <div className="text-sm text-gray-400">Kullanıcı Adı</div>
            <div className="text-gray-300">@{profile.username}</div>
          </div>

          {profile.join_date && (
            <div>
              <div className="text-sm text-gray-400">Katılım Tarihi</div>
              <div className="text-gray-300">{profile.join_date}</div>
            </div>
          )}

          <div>
            <div className="text-sm text-gray-400">E-posta Durumu</div>
            <div className="flex items-center mt-1">
              {profile.is_email_verified ? (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Doğrulanmış
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Doğrulanmamış
                </span>
              )}
            </div>
          </div>

          {profile.latitude && profile.longitude && (
            <div>
              <div className="text-sm text-gray-400 mb-2">Harita</div>
              <div className="h-48 bg-gray-700 rounded-lg overflow-hidden">
                <iframe
                  title="location"
                  width="100%"
                  height="100%"
                  frameBorder="0"
                  scrolling="no"
                  marginHeight="0"
                  marginWidth="0"
                  src={`https://www.openstreetmap.org/export/embed.html?bbox=${profile.longitude-0.01},${profile.latitude-0.01},${profile.longitude+0.01},${profile.latitude+0.01}&layer=mapnik&marker=${profile.latitude},${profile.longitude}`}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AboutSection; 