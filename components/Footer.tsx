
import React from 'react';
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 py-8">
      <div className="container mx-auto px-6 md:px-12 lg:px-24 text-center text-gray-500">
        <div className="flex justify-center space-x-6 mb-4">
          <a href="#" className="hover:text-indigo-400 transition-colors duration-300"><FaGithub size={24} /></a>
          <a href="#" className="hover:text-indigo-400 transition-colors duration-300"><FaLinkedin size={24} /></a>
          <a href="#" className="hover:text-indigo-400 transition-colors duration-300"><FaTwitter size={24} /></a>
        </div>
        <p>Designed & Built by Alex Doe</p>
        <p>&copy; {new Date().getFullYear()}. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
