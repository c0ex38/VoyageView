function Footer() {
  return (
    <footer className="bg-gray-900 border-t border-gray-800" data-scroll-section>
      <div className="container mx-auto py-8 px-4">
        {/* Main Footer Content */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {/* Brand Section */}
          <div className="col-span-2" data-scroll data-scroll-speed="0.3">
            <h2 className="text-xl font-bold bg-clip-text text-transparent 
                          bg-gradient-to-r from-purple-400 to-pink-600
                          hover:from-pink-600 hover:to-purple-400 transition-all duration-300
                          inline-block mb-3">
              VoyageView
            </h2>
            <p className="text-gray-400 text-sm mb-3">
              Yapay zeka destekli blog platformu ile benzersiz içerikler oluşturun.
            </p>
          </div>

          {/* Quick Links */}
          <div data-scroll data-scroll-speed="0.2">
            <h3 className="text-sm font-semibold text-white mb-3">Hızlı Bağlantılar</h3>
            <ul className="space-y-1.5">
              {quickLinks.map((link, index) => (
                <li key={index}>
                  <a href={link.url} 
                     className="text-gray-400 hover:text-purple-400 transition-colors duration-300
                              text-sm flex items-center group">
                    <span className="transform group-hover:translate-x-1 transition-transform duration-300">
                      {link.name}
                    </span>
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div data-scroll data-scroll-speed="0.1">
            <h3 className="text-sm font-semibold text-white mb-3">İletişim</h3>
            <ul className="space-y-1.5">
              {contactInfo.map((info, index) => (
                <li key={index} 
                    className="text-gray-400 flex items-center space-x-2 group text-sm
                             hover:text-purple-400 transition-colors duration-300">
                  <span className="group-hover:scale-110 transition-transform duration-300">
                    {info.icon}
                  </span>
                  <span>{info.text}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </footer>
  )
}

const quickLinks = [
  { name: "Ana Sayfa", url: "/" },
  { name: "Popüler", url: "/popular" },
];

const contactInfo = [
  { icon: "📧", text: "info@voyageview.com" },
  { icon: "📱", text: "+90 505 177 0483" }
];
export default Footer; 