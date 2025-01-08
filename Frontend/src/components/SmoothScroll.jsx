import { useEffect, useRef } from 'react';
import LocomotiveScroll from 'locomotive-scroll';
import 'locomotive-scroll/dist/locomotive-scroll.css';

function SmoothScroll({ children }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    let scroll;

    // Sayfa yüklendikten sonra Locomotive Scroll'u başlat
    const initScroll = () => {
      scroll = new LocomotiveScroll({
        el: scrollRef.current,
        smooth: true,
        multiplier: 1,
        class: 'is-revealed',
        reloadOnContextChange: true,
        touchMultiplier: 2,
        smoothMobile: true,
        smartphone: {
          smooth: true
        },
        tablet: {
          smooth: true
        }
      });

      // Scroll olaylarını dinle
      scroll.on('scroll', (args) => {
        // Scroll pozisyonuna göre elementleri güncelle
      });
    };

    // Sayfa tam yüklendiğinde scroll'u başlat
    window.addEventListener('load', initScroll);

    return () => {
      window.removeEventListener('load', initScroll);
      if (scroll) scroll.destroy();
    };
  }, []);

  return (
    <div data-scroll-container ref={scrollRef}>
      {children}
    </div>
  );
}

export default SmoothScroll; 