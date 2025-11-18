// src/pages/Chatbot.jsx
import React, { useState, useRef, useEffect } from 'react';
import "../styles/Chatbot.css"; 

function Chatbot() {
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState([]);
  const chatWindowRef = useRef(null);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message;
    setMessage("");

    setChat(prev => [...prev, { role: "user", text: userMessage }]);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chatbot/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
      });

      const data = await res.json();
      setChat(prev => [...prev, { role: "bot", text: data.reply }]);

    } catch (error) {
      setChat(prev => [...prev, { role: "bot", text: "Error de conexion." }]);
      console.error(error);
    }
  };

  // Scroll automatico al final
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chat]);

  return (
    <div className="chatbot-container">

      {/* --- BANNER FIJO --- */}
      <div className="chatbot-banner">
        <img src="/Logo.png" alt="Mogi logo" className="chatbot-logo" />
        <span className="chatbot-title">MOGI</span>
      </div>

      {/* --- CHAT --- */}
      <div className="chatbot-body">
        <div className="chat-window" ref={chatWindowRef}>
          {chat.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role === "user" ? "user-bubble" : "bot-bubble"}`}>
              {msg.text}
            </div>
          ))}
        </div>
      </div>

      {/* --- INPUT FLOTANTE ESTILO CHATGPT --- */}
      <div className="chat-input-container">
        <input
          type="text"
          placeholder="Escribe tu mensaje..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Enviar</button>
      </div>

    </div>
  );
}

export default Chatbot;
