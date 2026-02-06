'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { cleanMessage, parseSuggestions, parseMode } from '@/utils/chatUtils';


type Message = {
  role: 'user' | 'assistant';
  content: string;
  mode?: 'RAG' | 'BRAIN';
};

type UserProfile = {
  age: string;
  gender: string;
  history: string;
  allergies: string;
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'สวัสดีครับ หมอพร้อมให้คำปรึกษาแล้วครับ', mode: 'BRAIN' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [userProfile, setUserProfile] = useState<UserProfile>({
    age: '',
    gender: 'ไม่ระบุ',
    history: '',
    allergies: ''
  });
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    setSuggestions([]);
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: messageText }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: messageText,
          history: messages,
          user_profile: userProfile
        }),

      });

      if (!response.ok) throw new Error('Failed to connect');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';



      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.replace('data: ', '');
            console.log('📦 Chunk:', data); // Debug: Log raw chunk

            if (data === '[DONE]') {
              console.log('✅ Stream complete');
              const options = parseSuggestions(assistantMessage);
              const mode = parseMode(assistantMessage);
              console.log('🏷️ Parsed Mode:', mode); // Debug: Log mode
              console.log('💡 Parsed Suggestions:', options); // Debug: Log suggestions
              setSuggestions(options);


              // CRITICAL: Final clean of the assistant message before finishing
              const finalMessage = cleanMessage(assistantMessage);
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMsg = newMessages[newMessages.length - 1];
                lastMsg.content = finalMessage;
                if (mode) lastMsg.mode = mode; // Set mode if found
                return newMessages;
              });
              break;
            }

            assistantMessage += data;
            const displayMessage = cleanMessage(assistantMessage);

            setMessages(prev => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1].content = displayMessage;
              return newMessages;
            });
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'ขออภัยครับ เกิดข้อผิดพลาดในการเชื่อมต่อกับระบบ' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(input);
  };

  if (showOnboarding) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen relative p-6 overflow-hidden">
        {/* Background Layer */}
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: "url('/bg.png')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
        <div className="absolute inset-0 z-0 bg-blue-900/10 backdrop-blur-[2px]" />

        <div className="bg-white/70 backdrop-blur-xl p-8 rounded-3xl shadow-2xl max-w-md w-full border border-white/50 relative z-10">
          <div className="flex flex-col items-center mb-6">
            <div className="bg-blue-600 p-3 rounded-2xl mb-4">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800">ข้อมูลผู้ปรึกษา</h2>
            <p className="text-gray-500 text-sm text-center">เพื่อการวิเคราะห์อาการที่แม่นยำยิ่งขึ้นครับ</p>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">อายุ</label>
                <input
                  type="number"
                  placeholder="ปี"
                  className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-gray-900 outline-none"
                  value={userProfile.age}
                  onChange={(e) => setUserProfile({...userProfile, age: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">เพศ</label>
                <select
                  className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-gray-900 outline-none"
                  value={userProfile.gender}
                  onChange={(e) => setUserProfile({...userProfile, gender: e.target.value})}
                >
                  <option value="ชาย">ชาย</option>
                  <option value="หญิง">หญิง</option>
                  <option value="ไม่ระบุ">ไม่ระบุ</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">โรคประจำตัว</label>
              <textarea
                placeholder="เช่น ความดัน, เบาหวาน (ถ้ามี)"
                className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-gray-900 outline-none h-20 resize-none"
                value={userProfile.history}
                onChange={(e) => setUserProfile({...userProfile, history: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ประวัติแพ้ยา</label>
              <input
                type="text"
                placeholder="เช่น แพ้ยาเพนิซิลลิน (ถ้ามี)"
                className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-gray-900 outline-none"
                value={userProfile.allergies}
                onChange={(e) => setUserProfile({...userProfile, allergies: e.target.value})}
              />
            </div>

            <button
              onClick={() => setShowOnboarding(false)}
              className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold text-lg hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/30 active:scale-95 mt-4"
            >
              เริ่มต้นปรึกษาคุณหมอ
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen relative overflow-hidden">
      {/* Background Layer */}
      <div 
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: "url('/bg.png')",
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      />
      <div className="absolute inset-0 z-0 bg-slate-50/80 backdrop-blur-md" />

      {/* Header */}
      <header className="bg-white/70 backdrop-blur-md shadow-sm px-6 py-4 flex items-center gap-3 relative z-10 border-b border-white/50">
        <div className="bg-blue-600 p-2 rounded-lg">
            <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
            <h1 className="text-xl font-bold text-gray-800">Medical AI Agent</h1>
            <p className="text-xs text-gray-500 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                {userProfile.age && `พยาธิสภาพ: ${userProfile.gender} ${userProfile.age} ปี`}
                {userProfile.history && ` | ประวัติ: ${userProfile.history}`}
            </p>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 relative z-10">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none'
              }`}
            >
              <div className="flex items-start gap-3">
                {message.role === 'assistant' && (
                    <div className="bg-blue-100 p-1.5 rounded-full shrink-0">
                        <Bot className="w-4 h-4 text-blue-600" />
                    </div>
                )}
                <div className="flex-1">
                    <div className="whitespace-pre-wrap leading-relaxed">
                        {message.content}
                    </div>
                    {message.role === 'assistant' && message.mode && (
                        <div className="mt-2 flex items-center gap-1.5">
                            <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium flex items-center gap-1 ${
                                message.mode === 'RAG' 
                                ? 'bg-green-100 text-green-700 border border-green-200' 
                                : 'bg-purple-100 text-purple-700 border border-purple-200'
                            }`}>
                                {message.mode === 'RAG' ? '📚 จากฐานข้อมูลแพทย์' : '🧠 ความรู้ทั่วไป'}
                            </span>
                        </div>
                    )}
                </div>
                {message.role === 'user' && (
                    <div className="bg-blue-500 p-1.5 rounded-full shrink-0">
                        <User className="w-4 h-4 text-white" />
                    </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white p-4 rounded-2xl rounded-bl-none shadow-sm border border-gray-100 flex items-center gap-3">
               <div className="bg-blue-100 p-1.5 rounded-full">
                    <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
               </div>
               <span className="text-gray-500 text-sm animate-pulse">คุณหมอกำลังวิเคราะห์ข้อมูล...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white/80 backdrop-blur-md p-4 border-t border-white/50 relative z-10">
        {suggestions.length > 0 && !isLoading && (
          <div className="max-w-4xl mx-auto mb-3 flex flex-wrap gap-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
            {suggestions.map((option, idx) => (
              <button
                key={idx}
                onClick={() => {
                  handleSendMessage(option);
                }}
                className="px-4 py-2 bg-blue-50 text-blue-600 rounded-full text-sm font-medium hover:bg-blue-100 transition-colors border border-blue-100 shadow-sm whitespace-nowrap"
              >
                {option}
              </button>
            ))}
          </div>
        )}
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="พิมพ์ถามคุณหมอได้เลยครับ..."
            className="flex-1 px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 placeholder-gray-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20"
          >
            <Send className="w-4 h-4" />
            <span className="font-medium">Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}
