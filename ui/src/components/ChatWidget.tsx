import { useState, useEffect, useRef, FormEvent } from 'react';
import { sendChatMessage, getChatHistory } from '../services/api';
import { ChatMessage } from '../types/chat';
import { useAuth } from '../context/AuthContext';
import './ChatWidget.css';

const SESSION_ID = 'fundops-' + Date.now();

const SUGGESTIONS = [
  'Give me a fund summary',
  'What is the NAV?',
  'Show me the properties',
  'What is the current DSCR?',
];

function formatContent(text: string) {
  const parts = text.split('\n').filter(Boolean);
  return parts.map((line, i) => {
    const html = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return <p key={i} dangerouslySetInnerHTML={{ __html: html }} />;
  });
}

function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  const initials = (user?.name || 'U')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  useEffect(() => {
    if (!open || loaded) return;
    getChatHistory(SESSION_ID)
      .then((data) => {
        if (data.messages?.length) {
          setMessages(data.messages);
        } else {
          setMessages([{
            role: 'assistant',
            content: "Welcome to **REstackAI**! Ask me about NAV, AUM, NOI, cash, properties, debt, expenses, or request a **fund summary**.",
          }]);
        }
      })
      .catch(() => {
        setMessages([{
          role: 'assistant',
          content: "Welcome to **REstackAI**! Ask me about NAV, AUM, NOI, cash, properties, debt, expenses, or request a **fund summary**.",
        }]);
      })
      .finally(() => setLoaded(true));
  }, [open, loaded]);

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
        content: "Sorry, I couldn't process that request. Please try again.",
      }]);
    } finally {
      setSending(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    handleSend();
  };

  if (!user) return null;

  return (
    <>
      {open && (
        <div className="cw-popup">
          <div className="cw-header">
            <div className="cw-header-left">
              <div className="cw-header-icon">AI</div>
              <span className="cw-header-title">REstackAI Chat</span>
            </div>
            <button className="cw-close-btn" onClick={() => setOpen(false)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          <div className="cw-messages">
            {messages.map((msg, i) => (
              <div className={`cw-message ${msg.role}`} key={i}>
                <div className="cw-avatar">
                  {msg.role === 'assistant' ? 'AI' : initials}
                </div>
                <div className="cw-bubble">
                  {formatContent(msg.content)}
                </div>
              </div>
            ))}

            {sending && (
              <div className="cw-message assistant">
                <div className="cw-avatar">AI</div>
                <div className="cw-bubble">
                  <div className="cw-typing">
                    <span className="cw-typing-dot" />
                    <span className="cw-typing-dot" />
                    <span className="cw-typing-dot" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {messages.length <= 1 && (
            <div className="cw-suggestions">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  className="cw-suggestion-btn"
                  onClick={() => handleSend(s)}
                  disabled={sending}
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          <form className="cw-input-area" onSubmit={handleSubmit}>
            <input
              className="cw-input"
              type="text"
              placeholder="Ask about fund performance..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={sending}
            />
            <button className="cw-send-btn" type="submit" disabled={sending || !input.trim()}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        </div>
      )}

      <button className="cw-fab" onClick={() => setOpen(!open)}>
        {open ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>
    </>
  );
}

export default ChatWidget;
