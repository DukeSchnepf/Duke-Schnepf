
import { GoogleGenAI, Chat } from "@google/genai";
import { portfolioDataAsString } from '../constants';

let chat: Chat | null = null;

const initChat = () => {
  if (!process.env.API_KEY) {
    throw new Error("API_KEY environment variable not set");
  }
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  const systemInstruction = `You are Alex Doe's personal AI assistant, embedded in his portfolio website. Your personality is professional, friendly, and slightly witty. Your primary goal is to answer questions from visitors and potential employers about Alex. You MUST use the following information about Alex to answer all questions. Do not invent information. If a question is outside the scope of this information or is inappropriate, politely decline to answer. Here is Alex's information: ${portfolioDataAsString}`;

  return ai.chats.create({
    model: 'gemini-2.5-flash',
    config: {
      systemInstruction,
    },
  });
};

export const getAIChatResponse = async (message: string): Promise<string> => {
    if (!chat) {
        chat = initChat();
    }
    
    try {
        const response = await chat.sendMessage({ message });
        return response.text;
    } catch (error) {
        console.error("Gemini API error:", error);
        // In case of an error that invalidates the chat, reset it
        chat = null;
        return "There was an error communicating with the AI. Please try again.";
    }
};
