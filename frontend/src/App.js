import React, { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages })
      });
      let reply = '';
      if (response.body && response.body.getReader) {
        // Streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
        while (!done) {
          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          if (value) {
            const lines = decoder.decode(value).split('\n').filter(Boolean);
            for (const line of lines) {
              try {
                const data = JSON.parse(line);
                reply += data.message?.content || '';
              } catch {}
            }
          }
        }
      } else {
        // Fallback for non-streaming
        const data = await response.json();
        reply = data.message?.content || '';
      }
      setMessages([...newMessages, { role: 'assistant', content: reply }]);
    } catch (err) {
      setMessages([...newMessages, { role: 'assistant', content: 'Error: ' + err.message }]);
    }
    setLoading(false);
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
