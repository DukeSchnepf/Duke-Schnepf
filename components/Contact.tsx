
import React, { useState, useRef, useEffect } from 'react';
import { getAIChatResponse } from '../services/geminiService';
import type { ChatMessage } from '../types';

const Contact: React.FC = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: ChatMessage = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const aiResponse = await getAIChatResponse(input);
            const aiMessage: ChatMessage = { sender: 'ai', text: aiResponse };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Error fetching AI response:', error);
            const errorMessage: ChatMessage = { sender: 'ai', text: "Sorry, I'm having trouble connecting right now. Please try again later." };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section id="contact" className="py-24">
            <h2 className="text-3xl font-bold text-center mb-4">
                <span className="text-indigo-400">05.</span> Get In Touch
            </h2>
            <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">
                Have a question or just want to say hi? I've connected my personal AI assistant. Feel free to ask it anything about my experience or projects.
            </p>

            <div className="max-w-3xl mx-auto bg-gray-800/50 rounded-lg shadow-2xl border border-gray-700 flex flex-col" style={{height: '60vh'}}>
                <div className="flex-1 p-6 overflow-y-auto">
                    {messages.length === 0 && (
                      <div className="flex justify-center items-center h-full">
                        <p className="text-gray-500">Ask me something like, "What was Alex's role at Innovate Inc.?"</p>
                      </div>
                    )}
                    {messages.map((msg, index) => (
                        <div key={index} className={`flex mb-4 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`rounded-lg px-4 py-2 max-w-sm ${msg.sender === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-200'}`}>
                                {msg.text}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="flex justify-start mb-4">
                             <div className="rounded-lg px-4 py-2 max-w-sm bg-gray-700 text-gray-200">
                                <div className="flex items-center space-x-1">
                                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse delay-75"></span>
                                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse delay-150"></span>
                                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse delay-300"></span>
                                </div>
                            </div>
                        </div>
                    )}
                     <div ref={messagesEndRef} />
                </div>
                <div className="p-4 border-t border-gray-700">
                    <form onSubmit={handleSubmit} className="flex space-x-3">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your message..."
                            className="flex-1 bg-gray-700 rounded-full px-5 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            disabled={isLoading}
                        />
                        <button type="submit" className="bg-indigo-600 rounded-full px-5 py-3 text-white font-semibold hover:bg-indigo-700 disabled:bg-indigo-900 disabled:cursor-not-allowed transition-colors" disabled={isLoading}>
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </section>
    );
};

export default Contact;
