// src/pages/Chatbot.jsx
import React, { useState } from 'react';

function Chatbot() {
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState([]);

  const sendMessage = async () => {
    if (!message) return;

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chatbot/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });

      const data = await res.json();

      setChat([...chat, { user: message, bot: data.reply }]);
      setMessage('');
    } catch (error) {
      console.error("Error enviando mensaje:", error);
    }
  };

  return (
    <div>
      <h1>MOGI Chatbot</h1>
      <div style={{ border: "1px solid #ccc", padding: "10px", height: "300px", overflowY: "scroll" }}>
        {chat.map((c, i) => (
          <div key={i}>
            <b>Tú:</b> {c.user} <br />
            <b>MOGI:</b> {c.bot}
            <hr />
          </div>
        ))}
      </div>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Escribe tu mensaje..."
        style={{ width: "70%" }}
      />
      <button onClick={sendMessage} style={{ width: "25%" }}>Enviar</button>
    </div>
  );
}

export default Chatbot;