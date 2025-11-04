
import React from 'react';
import { EXPERIENCE_DATA } from '../constants';
import type { ExperienceItem } from '../types';

const ExperienceCard: React.FC<ExperienceItem> = ({ role, company, period, description }) => (
  <div className="relative pl-8 sm:pl-12 py-6 group">
    <div className="absolute top-5 left-0 w-2 h-2 mt-1 rounded-full bg-indigo-400 z-10 transition-all duration-300 group-hover:scale-150"></div>
    <div className="absolute top-7 left-1 w-px h-full bg-gray-700"></div>

    <div className="flex flex-col sm:flex-row items-start mb-1 group-hover:text-indigo-300 transition-colors duration-300">
      <h3 className="text-xl font-bold text-gray-100">{role}</h3>
      <span className="sm:ml-2 text-indigo-400">@ {company}</span>
    </div>
    <p className="text-sm font-mono text-gray-500 mb-3">{period}</p>
    <p className="text-gray-400 leading-relaxed">
      {description}
    </p>
  </div>
);

const Experience: React.FC = () => {
  return (
    <section id="experience" className="py-24">
      <h2 className="text-3xl font-bold text-center mb-12">
        <span className="text-indigo-400">02.</span> Where I've Worked
      </h2>
      <div className="relative">
        {EXPERIENCE_DATA.map((item, index) => (
          <ExperienceCard key={index} {...item} />
        ))}
      </div>
    </section>
  );
};

export default Experience;
