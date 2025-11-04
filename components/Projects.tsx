
import React from 'react';
import { PROJECTS_DATA } from '../constants';
import type { Project } from '../types';
import Card from './ui/Card';
import Tag from './ui/Tag';
import { FaGithub, FaExternalLinkAlt } from 'react-icons/fa';

const ProjectCard: React.FC<{ project: Project }> = ({ project }) => (
    <Card className="flex flex-col h-full group">
        <div className="overflow-hidden rounded-t-lg">
            <img src={project.imageUrl} alt={project.title} className="w-full h-48 object-cover transform transition-transform duration-500 group-hover:scale-110" />
        </div>
        <div className="p-6 flex flex-col flex-grow">
            <h3 className="text-xl font-bold text-gray-100 mb-2">{project.title}</h3>
            <p className="text-gray-400 mb-4 flex-grow">{project.description}</p>
            <div className="flex flex-wrap gap-2 mb-4">
                {project.tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
            </div>
        </div>
        <div className="p-6 pt-0 mt-auto flex justify-between items-center text-gray-400">
            <div className="flex space-x-4">
                 {project.repoUrl && (
                    <a href={project.repoUrl} target="_blank" rel="noopener noreferrer" className="hover:text-indigo-400 transition-colors duration-300">
                        <FaGithub size={22} />
                    </a>
                )}
                {project.liveUrl && (
                    <a href={project.liveUrl} target="_blank" rel="noopener noreferrer" className="hover:text-indigo-400 transition-colors duration-300">
                        <FaExternalLinkAlt size={20} />
                    </a>
                )}
            </div>
        </div>
    </Card>
);


const Projects: React.FC = () => {
  return (
    <section id="projects" className="py-24">
      <h2 className="text-3xl font-bold text-center mb-12">
        <span className="text-indigo-400">03.</span> Things I've Built
      </h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-8">
        {PROJECTS_DATA.map((project) => (
          <ProjectCard key={project.title} project={project} />
        ))}
      </div>
    </section>
  );
};

export default Projects;
