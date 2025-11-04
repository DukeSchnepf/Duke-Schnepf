
import React from 'react';
import { SKILLS_DATA } from '../constants';
import Card from './ui/Card';
import type { SkillCategory, Skill } from '../types';

const SkillItem: React.FC<{ skill: Skill }> = ({ skill }) => (
  <div className="flex flex-col items-center p-4 transition-transform duration-300 hover:-translate-y-1">
    <div className="text-indigo-400 mb-2">{skill.icon}</div>
    <span className="text-gray-300">{skill.name}</span>
  </div>
);

const Skills: React.FC = () => {
  return (
    <section id="skills" className="py-24">
      <h2 className="text-3xl font-bold text-center mb-12">
        <span className="text-indigo-400">04.</span> My Tech Stack
      </h2>
      <div className="grid md:grid-cols-3 gap-8">
        {SKILLS_DATA.map((category: SkillCategory) => (
          <Card key={category.title}>
            <div className="p-6">
              <h3 className="text-xl font-bold text-center text-gray-100 mb-6">{category.title}</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {category.skills.map((skill) => (
                  <SkillItem key={skill.name} skill={skill} />
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </section>
  );
};

export default Skills;
