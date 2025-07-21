import React, { useState, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const wsRef = useRef(null);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    
    // Open a new WebSocket connection for each message (or reuse if you prefer)
    const ws = new window.WebSocket('ws://localhost:8000/ws/chat');
    wsRef.current = ws;

    let reply = '';
    ws.onopen = () => {
      ws.send(JSON.stringify({ messages: newMessages }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.content) {
        reply += data.content;
        // Optionally, update the UI as each chunk arrives:
        setMessages([...newMessages, { role: 'assistant', content: reply }]);
      }
      if (data.done) {
        setLoading(false);
        ws.close();
      }
      if (data.error) {
        setMessages([...newMessages, { role: 'assistant', content: 'Error: ' + data.error }]);
        setLoading(false);
        ws.close();
      }
    };

    ws.onerror = (err) => {
      setMessages([...newMessages, { role: 'assistant', content: 'WebSocket error' }]);
      setLoading(false);
      ws.close();
    };
  };

  return (
    <div className="App">
      <h1>Ollama Chatbot</h1>
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.role === 'user' ? 'user-msg' : 'assistant-msg'}>
            <b>{msg.role === 'user' ? 'You' : 'Bot'}:</b> {msg.content}
          </div>
        ))}
        {loading && <div className="assistant-msg"><b>Bot:</b> <i>Thinking...</i></div>}
      </div>
      <form className="chat-input" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>Send</button>
      </form>
    </div>
  );
}

export default App;