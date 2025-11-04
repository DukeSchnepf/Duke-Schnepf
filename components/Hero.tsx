
import React from 'react';
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';

const Hero: React.FC = () => {
    
    const scrollToContact = () => {
        const contactSection = document.getElementById('contact');
        if (contactSection) {
            contactSection.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <section id="home" className="min-h-screen flex flex-col justify-center items-start">
            <div className="max-w-3xl">
                <h1 className="text-lg md:text-xl text-indigo-400 font-mono mb-4">Hi, my name is</h1>
                <h2 className="text-5xl md:text-7xl font-bold text-gray-100">Alex Doe.</h2>
                <h3 className="text-4xl md:text-6xl font-bold text-gray-400 mt-2">I build things for the web.</h3>
                <p className="text-gray-400 mt-6 max-w-xl text-lg">
                    I'm a senior frontend engineer specializing in creating exceptional digital experiences. Currently, I'm focused on building accessible, human-centered products and exploring the intersection of AI and user interfaces.
                </p>
                <div className="mt-8 flex items-center space-x-6">
                    <button onClick={scrollToContact} className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors duration-300">
                        Get In Touch
                    </button>
                    <div className="flex space-x-4">
                        <a href="#" className="text-gray-400 hover:text-indigo-400 transition-colors duration-300"><FaGithub size={24} /></a>
                        <a href="#" className="text-gray-400 hover:text-indigo-400 transition-colors duration-300"><FaLinkedin size={24} /></a>
                        <a href="#" className="text-gray-400 hover:text-indigo-400 transition-colors duration-300"><FaTwitter size={24} /></a>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
