
import React from 'react';

const About: React.FC = () => {
  return (
    <section id="about" className="py-24">
      <h2 className="text-3xl font-bold text-center mb-12">
        <span className="text-indigo-400">01.</span> About Me
      </h2>
      <div className="grid md:grid-cols-5 gap-10 items-center">
        <div className="md:col-span-3 text-gray-300 text-lg space-y-4">
          <p>
            Hello! I'm Alex, a frontend engineer based in San Francisco, CA. My journey into web development started back in 2014 when I decided to build a custom website for a local band — turns out hacking together a beautiful and functional site was a lot of fun!
          </p>
          <p>
            Fast-forward to today, and I've had the privilege of working at an innovation-focused corporation, a start-up, and a digital agency. My main focus these days is building accessible, inclusive products and digital experiences for a variety of clients. I'm also deeply passionate about the potential of AI and have been actively integrating models like Gemini into my work to create smarter, more intuitive applications.
          </p>
          <p>
            When I'm not at the computer, I'm usually exploring the outdoors, playing guitar, or searching for the best coffee in the city.
          </p>
        </div>
        <div className="md:col-span-2 flex justify-center">
          <div className="relative w-64 h-64 md:w-80 md:h-80 group">
            <div className="absolute inset-0 bg-indigo-500 rounded-lg transform transition-transform duration-300 group-hover:rotate-6"></div>
            <img src="https://picsum.photos/seed/alex/400/400" alt="Alex Doe" className="absolute inset-0 w-full h-full object-cover rounded-lg shadow-xl" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
