
import React from 'react';
import type { Project, ExperienceItem, SkillCategory } from './types';
import { SiTypescript, SiJavascript, SiPython, SiReact, SiNextdotjs, SiNodedotjs, SiTailwindcss, SiVite, SiDocker, SiPostgresql, SiMongodb, SiGit } from 'react-icons/si';

// Using a popular icon library for demonstration. In a real project, you might SVG-inline these.
// For this example, we will use react-icons components.
// To avoid installing a library, here are example SVG components for icons.

const TypeScriptIcon = () => <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current"><title>TypeScript</title><path d="M1.5 0 h21 l-1.91 21.563L11.977 24l-8.564-2.438z" fill="#007acc"/><path d="M12 21.9l6.53-1.85L20.42 2H3.58l1.92 20.05L12 21.9z" fill="#3178c6"/><path d="M12 4.41v15.22l5.72-1.62L18.42 4.41H12zm-3.03 3.03h2.1v2.1h-2.1V7.44zm0 4.2h2.1v6.3h2.1v-6.3h2.1v-2.1h-6.3v2.1z" fill="#fff"/></svg>;
const ReactIcon = () => <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current text-sky-400"><title>React</title><path d="M12.001 2.002c-5.522 0-10 4.477-10 10s4.478 10 10 10 10-4.477 10-10-4.478-10-10-10zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/><path d="M12.126 7.962c.188-.475.656-.84 1.206-.84h.24c.465 0 .8.143.987.41.189.268.223.63.13 1.05l-1.05 4.885c-.093.42.064.84.42.98l.24.095c.56.21 1.235-.015 1.625-.475l.93-1.115c.39-.46.99-.64 1.56-.475.57.165.99.645 1.015 1.23l.115 2.37c.025.59-.285 1.13-.81 1.39l-.21.1c-.69.34-1.47.01-1.87-.65l-.955-1.575c-.39-.64-1.21-.89-1.88-.58l-.23.1c-1.02.475-2.16-.29-2.38-1.39l-1.28-6.42z"/><path d="M12.015 11.532a1.47 1.47 0 100-2.94 1.47 1.47 0 000 2.94z"/></svg>;
const NodejsIcon = () => <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current text-green-500"><title>Node.js</title><path d="M12.37.24L.85 6.42v11.16l11.52 6.18 11.52-6.18V6.42L12.37.24zM12 1.87l9.9 5.31v9.64l-9.9 5.32-9.9-5.32V7.18L12 1.87zM8.1 8.93a.48.48 0 00-.47.47v5.2c0 .26.21.47.47.47h.88v-4.8h1.8v4.8h.89a.47.47 0 00.47-.47v-5.2a.47.47 0 00-.47-.47H8.1zm6.98 0a.47.47 0 00-.47.47v5.2c0 .26.21.47.47.47h2.64a.47.47 0 00.47-.47v-1.9h-1.77V11.8h1.3v-1.1h-1.3V9.4h1.76v-1.9a.47.47 0 00-.47-.47h-2.63zM12.98 9.4h.88v.8h-.88v-.8zM5.56 8.93a.47.47 0 00-.47.47v5.2c0 .26.21.47.47.47h.88v-2.22h.89v2.22h.88a.47.47 0 00.47-.47V9.4a.47.47 0 00-.47-.47H5.56zm1.33 2.54H6v-.89h.89v.89z"/></svg>;
const NextjsIcon = () => <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current"><title>Next.js</title><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.284 18.238-6.15-10.957h-1.28L6.47 18.238H4.077L11.332 5h1.337l7.255 13.238h-2.36zM13.43 14.37h2.893l-1.446-2.583-1.447 2.583z"/></svg>;
const TailwindIcon = () => <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current text-teal-400"><title>Tailwind CSS</title><path d="M12.001,4.8c-3.2,0-5.2,1.6-6,4.8c1.2-1.6,2.6-2.2,4.2-1.8c0.913,0.228,1.565,0.89,2.288,1.624 C13.666,10.618,15.027,12,18.001,12c3.2,0,5.2-1.6,6-4.8c-1.2,1.6-2.6,2.2-4.2,1.8c-0.913-0.228-1.565-0.89-2.288-1.624 C16.334,6.182,14.973,4.8,12.001,4.8z M6.001,12c-3.2,0-5.2,1.6-6,4.8c1.2-1.6,2.6-2.2,4.2-1.8c0.913,0.228,1.565,0.89,2.288,1.624 c1.177,1.194,2.538,2.576,5.512,2.576c3.2,0,5.2-1.6,6-4.8c-1.2,1.6-2.6,2.2-4.2,1.8c-0.913-0.228-1.565-0.89-2.288-1.624 C16.334,13.382,14.973,12,12.001,12C9.027,12,7.666,13.382,6.488,14.576C6.488,14.576,6.001,12,6.001,12z"/></svg>;
const GitIcon = () => <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current text-orange-600"><title>Git</title><path d="M23.5,11.1l-4.14-4.15c-0.53-0.52-1.37-0.52-1.9,0l-1.42,1.42c-0.53,0.52-0.53,1.38,0,1.9l2.2,2.2l-2.2,2.2 c-0.53,0.52-0.53,1.38,0,1.9l1.42,1.42c0.53,0.52,1.37,0.52,1.9,0l4.14-4.15C24.03,12.47,24.03,11.62,23.5,11.1z M17.47,19.38 l-1.42-1.42l-2.22,2.23c-0.53,0.52-1.37,0.52-1.9,0l-4.14-4.15c-0.53-0.52-0.53-1.38,0-1.9l4.14-4.15c0.53-0.52,1.37-0.52,1.9,0 l2.22,2.22l1.42-1.42L16.03,9.22c-1.32-1.32-3.48-1.32-4.8,0L7.08,13.37c-1.32,1.32-1.32,3.48,0,4.8l4.15,4.15 C12.55,23.6,14.7,23.6,16.03,22.3L17.47,19.38z M9.28,7.78C9.8,7.25,9.8,6.4,9.28,5.88L7.85,4.46c-0.53-0.52-1.37-0.52-1.9,0 L1.8,8.61c-0.53,0.52-0.53,1.38,0,1.9L6,14.65l1.42-1.42L4.03,9.84L9.28,7.78z"/></svg>;


export const SKILLS_DATA: SkillCategory[] = [
  {
    title: "Languages",
    skills: [
      { name: 'TypeScript', icon: <TypeScriptIcon /> },
      { name: 'JavaScript', icon: <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current text-yellow-400"><title>JavaScript</title><path d="M0 0h24v24H0V0zm22.034 18.276c-.546 1.344-1.4 2.472-2.562 3.384-1.164.912-2.586 1.368-4.266 1.368-1.764 0-3.33-.522-4.698-1.566-1.368-1.044-2.37-2.424-3.006-4.14h3.198c.522 1.224 1.236 2.1 2.142 2.628.906.528 1.956.792 3.15.792 1.116 0 2.022-.234 2.718-.702.696-.468.954-1.122.774-1.962-.12-.648-.552-1.224-1.296-1.728-.744-.504-1.782-.99-3.114-1.458-1.92-.684-3.39-1.59-4.404-2.724-1.014-1.134-1.524-2.58-1.524-4.338 0-1.632.492-3.036 1.476-4.212 1.056-1.248 2.448-1.872 4.176-1.872 1.56 0 2.94.456 4.14 1.368 1.2.912 2.034 2.112 2.508 3.6h-3.198c-.45-.96-.984-1.692-1.608-2.196-.624-.504-1.386-.756-2.286-.756-.936 0-1.698.24-2.286.72-.588.48-.792 1.08-.612 1.8 0 .588.318 1.128.954 1.62.636.492 1.56.996 2.772 1.512 2.184.912 3.822 1.956 4.914 3.132 1.092 1.176 1.638 2.7 1.638 4.572 0 1.656-.522 3.078-1.566 4.266z"/></svg> },
      { name: 'Python', icon: <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current text-blue-500"><title>Python</title><path d="M23.25 12c0 6.213-5.037 11.25-11.25 11.25S.75 18.213.75 12 .75.75 12 .75c3.27 0 6.204 1.404 8.25 3.63V0h3v5.625A11.203 11.203 0 0123.25 12zM12 20.25c4.554 0 8.25-3.696 8.25-8.25S16.554 3.75 12 3.75 3.75 7.446 3.75 12 7.446 20.25 12 20.25zm-3-9.375V12h3.375a2.625 2.625 0 000-5.25H9v1.875h1.125a.75.75 0 110 1.5H9zm6 4.5V14.25h-3.375a2.625 2.625 0 000 5.25H15v-1.875h-1.125a.75.75 0 110-1.5H15z"/></svg> },
    ]
  },
  {
    title: "Frameworks & Libraries",
    skills: [
      { name: 'React', icon: <ReactIcon /> },
      { name: 'Next.js', icon: <NextjsIcon /> },
      { name: 'Node.js', icon: <NodejsIcon /> },
      { name: 'Tailwind CSS', icon: <TailwindIcon /> },
    ]
  },
  {
    title: "Tools & Platforms",
    skills: [
      { name: 'Git', icon: <GitIcon /> },
      { name: 'Docker', icon: <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current text-blue-600"><title>Docker</title><path d="M23.156 12.188c-.14-3.344-2.016-6.17-4.67-7.812a.33.33 0 00-.437.126l-2.11 3.655a.33.33 0 00.11.484 5.3 5.3 0 013.11 4.766c0 .3-.016.6-.047.89a.33.33 0 00.33.344h3.985a.33.33 0 00.328-.313zm-6.14-8.86a.33.33 0 00-.438-.11L13.25 4.5a.33.33 0 00.11.594l2.58 1.03a.33.33 0 00.437-.11zm-5.69 1.61a.33.33 0 00-.437-.11L7.56 6.11a.33.33 0 00.11.593l2.58 1.032a.33.33 0 00.438-.11zM6.61 6.11a.33.33 0 00-.437-.11L2.844 7.283a.33.33 0 00.11.593l2.58 1.032a.33.33 0 00.438-.11zM1.173 8.7a.33.33 0 00-.438-.11L0 8.875v7.25l.734.293a.33.33 0 00.438-.11l2.58-4.468a.33.33 0 00-.11-.594zM16.5 15.625h-3.375v-3.375H9.75v3.375H6.375v3.375h3.375v3.375H13.125v-3.375h3.375z"/></svg> },
      { name: 'Vite', icon: <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 fill-current text-purple-500"><title>Vite</title><path d="M23.415 5.432a2.31 2.31 0 00-1.632-.676H18.96c-.34 0-.66.166-.856.438l-6.49 9.006-2.923-9.01a.98.98 0 00-.91-.659H5.013c-.92 0-1.42.94-.962 1.698l6.023 9.718L3.92 20.482c-.44.577.014 1.442.843 1.442h2.81c.365 0 .706-.18.9-.47l6.5-9.02 2.924 9.02c.2.61.78.995 1.41.995h2.772c.905 0 1.396-.91.96-1.658L16.2 11.232l6.252-8.102c.45-.6-.05-1.698-.938-1.698z"/></svg> },
    ]
  },
];

export const PROJECTS_DATA: Project[] = [
    {
        title: 'Project Zenith',
        description: 'A cutting-edge data visualization platform that provides real-time analytics for enterprise clients. Built with a focus on performance and scalability.',
        tags: ['React', 'TypeScript', 'D3.js', 'Node.js', 'PostgreSQL'],
        imageUrl: 'https://picsum.photos/seed/zenith/600/400',
        liveUrl: '#',
        repoUrl: '#',
    },
    {
        title: 'ConnectSphere',
        description: 'A social networking app designed for professionals to connect and collaborate on projects. Features include real-time chat and project management tools.',
        tags: ['Next.js', 'Tailwind CSS', 'Firebase', 'GraphQL'],
        imageUrl: 'https://picsum.photos/seed/connect/600/400',
        liveUrl: '#',
        repoUrl: '#',
    },
    {
        title: 'AI Art Generator',
        description: 'An innovative web application that leverages generative AI models to create unique digital art from user prompts. Integrated with the Gemini API.',
        tags: ['Vite', 'React', 'Gemini API', 'Python', 'FastAPI'],
        imageUrl: 'https://picsum.photos/seed/artai/600/400',
        liveUrl: '#',
        repoUrl: '#',
    },
    {
        title: 'E-Commerce Platform',
        description: 'A full-featured e-commerce solution with a custom CMS, product management, and a secure payment gateway integration.',
        tags: ['React', 'Node.js', 'Express', 'MongoDB', 'Stripe API'],
        imageUrl: 'https://picsum.photos/seed/ecom/600/400',
        liveUrl: '#',
        repoUrl: '#',
    },
];

export const EXPERIENCE_DATA: ExperienceItem[] = [
    {
        role: 'Senior Frontend Engineer',
        company: 'Innovate Inc.',
        period: '2020 - Present',
        description: 'Led the development of the main user-facing application, improving performance by 40%. Mentored junior developers and established best practices for code quality and testing. Integrated AI features using Gemini to enhance user experience.',
    },
    {
        role: 'Frontend Developer',
        company: 'Tech Solutions LLC',
        period: '2017 - 2020',
        description: 'Developed and maintained responsive web applications for various clients using React and Angular. Collaborated with UI/UX designers to translate mockups into functional, high-quality code.',
    },
    {
        role: 'Junior Web Developer',
        company: 'Digital Creations',
        period: '2015 - 2017',
        description: 'Assisted in building websites and web applications using HTML, CSS, and JavaScript. Gained foundational knowledge in web development and agile methodologies.',
    },
];

export const portfolioDataAsString = `
  Name: Alex Doe
  Title: Senior Frontend Engineer & AI Specialist
  Summary: A passionate and experienced frontend engineer with over 8 years of experience building high-quality, scalable, and performant web applications. Specializes in the React ecosystem, TypeScript, and modern web technologies. Deep expertise in integrating Large Language Models like Gemini to create intelligent and interactive user experiences.

  Experience:
  ${EXPERIENCE_DATA.map(exp => `
    - Role: ${exp.role}
      Company: ${exp.company}
      Period: ${exp.period}
      Description: ${exp.description}
  `).join('')}

  Projects:
  ${PROJECTS_DATA.map(proj => `
    - Title: ${proj.title}
      Description: ${proj.description}
      Technologies: ${proj.tags.join(', ')}
  `).join('')}

  Skills:
  - Languages: TypeScript, JavaScript, Python
  - Frameworks & Libraries: React, Next.js, Node.js, Tailwind CSS
  - Tools & Platforms: Git, Docker, Vite, PostgreSQL, MongoDB
`;
