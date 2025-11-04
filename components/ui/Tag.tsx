
import React from 'react';

interface TagProps {
  children: React.ReactNode;
}

const Tag: React.FC<TagProps> = ({ children }) => {
  return (
    <span className="inline-block bg-gray-700 text-indigo-300 text-xs font-mono px-3 py-1 rounded-full">
      {children}
    </span>
  );
};

export default Tag;
