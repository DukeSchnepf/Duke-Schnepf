
import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-gray-800/50 border border-gray-700 rounded-lg shadow-lg transition-all duration-300 hover:shadow-indigo-500/20 hover:border-gray-600 ${className}`}>
      {children}
    </div>
  );
};

export default Card;
