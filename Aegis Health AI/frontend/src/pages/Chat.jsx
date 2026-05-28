import React, { useState, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../context/AuthContext';
import { 
  Send, 
  Mic, 
  MicOff, 
  Volume2, 
  Trash2, 
  Activity,
  Bot,
  User,
  Sparkles,
  RefreshCcw
} from 'lucide-react';

export default function Chat() {
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: 'Hello! 👋 Welcome to Aegis Health. I\'m your personal AI healthcare assistant, here to listen and help. How are you feeling today?' 
    }
  ]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Setup HTML5 Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';

      rec.onresult = (event) => {
        const text = event.results[0][0].transcript;
        setInput(prev => prev + ' ' + text);
        setIsRecording(false);
      };

      rec.onerror = () => {
        setIsRecording(false);
      };

      rec.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = rec;
    }
  }, []);

  const toggleRecording = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
    } else {
      setIsRecording(true);
      recognitionRef.current.start();
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Append user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    
    // Add temporary assistant loading slot
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    try {
      // Connect to the streaming endpoint
      const response = await fetch(
        `${API_BASE_URL}/chat/stream?message=${encodeURIComponent(userMessage)}`
      );

      if (!response.ok) {
        throw new Error('Streaming failed');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        assistantText += chunk;

        // Update the last assistant message with cumulative chunks
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: assistantText
          };
          return updated;
        });
      }
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: 'I apologize, but I encountered an issue retrieving that information. Please check your network connection.'
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSpeechOutput = (text) => {
    if ('speechSynthesis' in window) {
      // Cancel active voice synthesis first
      window.speechSynthesis.cancel();
      
      const cleanedText = text.replace(/[*#_`]/g, ''); // strip markdown syntax
      const utterance = new SpeechSynthesisUtterance(cleanedText);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    } else {
      alert("Speech synthesis is not supported on this browser.");
    }
  };

  const handleClearHistory = async () => {
    try {
      await fetch(`${API_BASE_URL}/chat/clear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: 'default' }),
      });
      setMessages([
        { 
          role: 'assistant', 
          content: 'Hello again! 👋 Memory cleared. How are you feeling today? I\'m ready to help with any health concerns you may have.' 
        }
      ]);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 h-[calc(100vh-2rem)] flex flex-col animate-fade-in max-w-5xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200/50 dark:border-slate-800/50">
        <div>
          <h2 className="text-3xl font-extrabold tracking-tight flex items-center gap-2.5">
            <span className="bg-gradient-to-r from-brand-500 via-accent-teal to-accent-indigo bg-clip-text text-transparent">
              Aegis Health AI
            </span>
            <Sparkles className="w-6 h-6 text-brand-500 animate-pulse" />
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-2xl leading-relaxed">
            Your intelligent healthcare companion — here to help you understand symptoms, wellness, and medical concerns with AI-powered guidance.
          </p>
        </div>
        <button
          onClick={handleClearHistory}
          title="Clear active dialogue memory"
          className="self-start sm:self-center p-3 bg-slate-100/50 dark:bg-slate-900/50 text-slate-400 hover:text-rose-500 dark:hover:text-rose-400 rounded-xl hover:scale-105 active:scale-95 transition-all border border-slate-200/50 dark:border-slate-800/50 flex items-center gap-1.5 text-xs font-semibold shrink-0"
        >
          <Trash2 className="w-4 h-4" /> Clear Memory
        </button>
      </div>

      {/* Message workspace */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6 pr-2">
        {messages.map((msg, idx) => {
          const isAssistant = msg.role === 'assistant';
          return (
            <div 
              key={idx} 
              className={`flex items-start gap-4 max-w-4xl animate-slide-up ${
                isAssistant ? '' : 'flex-row-reverse ml-auto'
              }`}
            >
              {/* Avatar */}
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow ${
                isAssistant 
                  ? 'bg-gradient-to-tr from-brand-500 to-accent-teal text-white' 
                  : 'bg-gradient-to-tr from-accent-indigo to-accent-violet text-white'
              }`}>
                {isAssistant ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
              </div>

              {/* Message frame */}
              <div className="space-y-1.5 max-w-[80%]">
                <div className={`p-4.5 rounded-3xl text-sm ${
                  isAssistant 
                    ? 'glass-panel text-slate-800 dark:text-slate-200' 
                    : 'bg-brand-500 text-white shadow-md'
                }`}>
                  {msg.content === '' && loading ? (
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-brand-500 dark:bg-accent-teal animate-bounce" />
                      <span className="w-2 h-2 rounded-full bg-brand-500 dark:bg-accent-teal animate-bounce" style={{ animationDelay: '0.2s' }} />
                      <span className="w-2 h-2 rounded-full bg-brand-500 dark:bg-accent-teal animate-bounce" style={{ animationDelay: '0.4s' }} />
                    </span>
                  ) : (
                    <div className="whitespace-pre-line leading-relaxed font-medium">
                      {msg.content}
                    </div>
                  )}
                </div>
                
                {/* Auxiliary options */}
                {isAssistant && msg.content && (
                  <div className="flex items-center gap-3 pl-2">
                    <button
                      onClick={() => handleSpeechOutput(msg.content)}
                      title="Audio synthesis"
                      className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-brand-500 rounded-lg transition-colors"
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                    <span className="text-[9px] uppercase font-bold tracking-widest text-slate-400 bg-slate-100 dark:bg-slate-900/50 px-1.5 py-0.5 rounded">
                      RAG Context Verified
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input panel */}
      <form onSubmit={handleSend} className="p-4 bg-slate-100/50 dark:bg-slate-900/50 rounded-3xl border border-slate-200/50 dark:border-slate-800/50 flex items-center gap-3">
        <button
          type="button"
          onClick={toggleRecording}
          title={isRecording ? 'Stop recording' : 'Speech-to-text voice input'}
          className={`p-3.5 rounded-2xl transition-all ${
            isRecording 
              ? 'bg-rose-500 text-white animate-pulse' 
              : 'hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600'
          }`}
        >
          {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isRecording ? 'Listening, speak clearly...' : 'Say hello, describe symptoms, or ask a health question...'}
          className="flex-1 bg-transparent text-sm text-slate-800 dark:text-white placeholder-slate-400 focus:outline-none"
        />

        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-3.5 bg-gradient-to-r from-brand-500 to-accent-teal hover:scale-105 active:scale-95 text-white rounded-2xl shadow transition-all disabled:opacity-50 disabled:scale-100 disabled:pointer-events-none shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
