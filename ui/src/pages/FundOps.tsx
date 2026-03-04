import { useState, useEffect, useRef, FormEvent } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { sendChatMessage, getChatHistory } from '../services/api';
import { ChatMessage } from '../types/chat';
import { useAuth } from '../context/AuthContext';
import '../components/Layout.css';
import './FundOps.css';

const SESSION_ID = 'fundops-' + Date.now();

const SUGGESTIONS = [
  'Give me a fund summary',
  'What is the NAV?',
  'Show me the properties',
  'What is the current DSCR?',
  'How much cash do we have?',
];

function formatContent(text: string) {
  // Convert **bold** to <strong> and newlines to paragraphs
  const parts = text.split('\n').filter(Boolean);
  return parts.map((line, i) => {
    const html = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return <p key={i} dangerouslySetInnerHTML={{ __html: html }} />;
  });
}

function FundOps() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  const initials = (user?.name || 'U')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  useEffect(() => {
    // Load existing history
    getChatHistory(SESSION_ID)
      .then((data) => {
        if (data.messages?.length) {
          setMessages(data.messages);
        } else {
          // Welcome message
          setMessages([{
            role: 'assistant',
            content: "Welcome to **FundOps AI**! I can answer questions about Horizon Value Fund I — ask me about NAV, AUM, NOI, cash, properties, debt, expenses, or request a full **fund summary**.",
          }]);
        }
      })
      .catch(() => {
        setMessages([{
          role: 'assistant',
          content: "Welcome to **FundOps AI**! I can answer questions about Horizon Value Fund I — ask me about NAV, AUM, NOI, cash, properties, debt, expenses, or request a full **fund summary**.",
        }]);
      });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const handleSend = async (text?: string) => {
    const message = (text || input).trim();
    if (!message || sending) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: message }]);
    setSending(true);

    try {
      const response = await sendChatMessage(message, SESSION_ID);
      setMessages((prev) => [...prev, { role: 'assistant', content: response.content }]);
    } catch {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: "Sorry, I couldn't process that request. Please make sure the API server is running and try again.",
      }]);
    } finally {
      setSending(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    handleSend();
  };

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      <div className="dashboard-main">
        <Topbar title="FundOps AI Chat" onMenuToggle={toggleSidebar} />

        <div className="chat-content">
          <div className="chat-header">
            <p className="chat-header-title">
              <strong>FundOps AI</strong> — Ask questions about fund performance, properties, and financial metrics
            </p>
          </div>

          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div className={`chat-message ${msg.role}`} key={i}>
                <div className="chat-avatar">
                  {msg.role === 'assistant' ? 'AI' : initials}
                </div>
                <div className="chat-bubble">
                  {formatContent(msg.content)}
                </div>
              </div>
            ))}

            {sending && (
              <div className="chat-message assistant">
                <div className="chat-avatar">AI</div>
                <div className="chat-bubble">
                  <div className="chat-typing">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <form className="chat-input-row" onSubmit={handleSubmit}>
              <input
                className="chat-input"
                type="text"
                placeholder="Ask about fund performance, NAV, properties..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={sending}
              />
              <button className="chat-send-btn" type="submit" disabled={sending || !input.trim()}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </form>
            {messages.length <= 1 && (
              <div className="chat-suggestions">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    className="chat-suggestion-btn"
                    onClick={() => handleSend(s)}
                    disabled={sending}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default FundOps;
