
import React, { useState, useEffect } from 'react';

const Header: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  const sections = ['about', 'experience', 'projects', 'skills', 'contact'];

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? 'bg-gray-900/80 backdrop-blur-sm shadow-lg' : 'bg-transparent'}`}>
      <div className="container mx-auto px-6 md:px-12 lg:px-24 flex justify-between items-center h-20">
        <div className="text-2xl font-bold text-white cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          <span className="text-indigo-400">A</span>D
        </div>
        <nav className="hidden md:flex space-x-8">
          {sections.map(section => (
            <button
              key={section}
              onClick={() => scrollToSection(section)}
              className="capitalize text-gray-300 hover:text-indigo-400 transition-colors duration-300 font-medium"
            >
              {section}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};

export default Header;
