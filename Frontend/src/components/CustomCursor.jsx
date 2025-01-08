import { useEffect } from 'react';

function CustomCursor() {
  useEffect(() => {
    const cursor = document.createElement('div');
    const follower = document.createElement('div');
    
    cursor.className = 'custom-cursor';
    follower.className = 'cursor-follower';
    
    document.body.appendChild(cursor);
    document.body.appendChild(follower);

    let mouseX = 0;
    let mouseY = 0;
    let followerX = 0;
    let followerY = 0;

    document.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      
      cursor.style.transform = `translate(${mouseX}px, ${mouseY}px)`;
    });

    const followMouse = () => {
      followerX += (mouseX - followerX) / 6;
      followerY += (mouseY - followerY) / 6;
      
      follower.style.transform = `translate(${followerX}px, ${followerY}px)`;
      
      requestAnimationFrame(followMouse);
    };

    followMouse();

    // Hover efektleri
    const handleMouseEnter = () => {
      cursor.classList.add('cursor-hover');
      follower.classList.add('follower-hover');
    };

    const handleMouseLeave = () => {
      cursor.classList.remove('cursor-hover');
      follower.classList.remove('follower-hover');
    };

    const elements = document.querySelectorAll('a, button');
    elements.forEach(el => {
      el.addEventListener('mouseenter', handleMouseEnter);
      el.addEventListener('mouseleave', handleMouseLeave);
    });

    return () => {
      document.body.removeChild(cursor);
      document.body.removeChild(follower);
      elements.forEach(el => {
        el.removeEventListener('mouseenter', handleMouseEnter);
        el.removeEventListener('mouseleave', handleMouseLeave);
      });
    };
  }, []);

  return null;
}

export default CustomCursor; 