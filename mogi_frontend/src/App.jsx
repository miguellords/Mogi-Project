import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Chatbot from './pages/Chatbot';
import Login from './pages/Login';
import AuthCallback from "./pages/AuthCallback";
import "./styles/App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/chatbot" element={<Chatbot />} />
        {/*<Route path="/dashboard" element={<Dashboard />} />*/}
        <Route path="/auth/callback" element={<AuthCallback />} />
      </Routes>
    </Router>
  );
}

export default App;
