import { useState } from "react";
import { supabase } from "../supabaseClient";
import "../styles/Login.css";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [modalMessage, setModalMessage] = useState("");

  const navigate = useNavigate();

  // -----------------------------
  // LOGIN CON GOOGLE
  // -----------------------------
  const handleGoogleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: "http://localhost:3000/auth/callback",
        emailRedirectTo: "http://localhost:3000/auth/callback",
      },
    });

    if (error) {
      setModalMessage(error.message);
      setShowModal(true);
    }
  };

  // -----------------------------
  // LOGIN CON EMAIL
  // -----------------------------
const handleEmailLogin = async (e) => {
  e.preventDefault();

  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  console.log("LOGIN DATA:", data, "ERROR:", error);

  if (error) {
    setModalMessage(error.message);
    setShowModal(true);
    return;
  }

  if (data.user) {
    navigate("/chatbot");
  } else {
    setModalMessage("No se pudo iniciar sesión. Revisa tu correo y contraseña.");
    setShowModal(true);
  }
};

  // -----------------------------
  // REGISTRO
  // -----------------------------
  const handleEmailSignup = async (e) => {
    e.preventDefault();

    const { error } = await supabase.auth.signUp({
      email,
      password,
    });

    if (error) {
      setModalMessage(error.message);
      setShowModal(true);
      return;
    }

    setModalMessage("Cuenta creada. Revisa tu correo para confirmar.");
    setShowModal(true);

    setMode("login");
  };

  return (
    <div className="login-container">

      {/* BANNER SUPERIOR */}
      <div className="login-banner">
        <img src="/Logo.png" alt="Mogi logo" className="mogi-logo" />
        {/*<h2 className="banner-title">MOGI</h2>*/}
      </div>

      <div className="login-card">

        <h1 className="login-title">
          {mode === "login" ? "Iniciar sesion" : "Crear cuenta"}
        </h1>

        <p className="login-sub">
          {mode === "login"
            ? "Accede con tu correo o con Google"
            : "Registra una nueva cuenta"}
        </p>

        {/* FORMULARIO */}
        <form
          className="login-form"
          onSubmit={mode === "login" ? handleEmailLogin : handleEmailSignup}
        >
          <input
            type="email"
            placeholder="Correo electronico"
            className="login-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Contrasena"
            className="login-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit" className="email-btn">
            {mode === "login" ? "Iniciar sesion" : "Registrarse"}
          </button>
        </form>

        <div className="divider">o</div>

        {/* GOOGLE */}
        <button className="google-btn" onClick={handleGoogleLogin}>
          <img
            src="https://www.svgrepo.com/show/355037/google.svg"
            alt="Google icon"
            className="google-icon"
          />
          Continuar con Google
        </button>

        {/* CAMBIO LOGIN ↔ REGISTRO */}
        <p className="switch-mode" style={{ marginTop: "16px" }}>
          {mode === "login" ? (
            <>
              ¿No tienes cuenta?{" "}
              <span onClick={() => setMode("register")}>Registrarse</span>
            </>
          ) : (
            <>
              ¿Ya tienes cuenta?{" "}
              <span onClick={() => setMode("login")}>Iniciar sesion</span>
            </>
          )}
        </p>
      </div>

      {/* -----------------------------
          MODAL
      ------------------------------*/}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <p>{modalMessage}</p>
            <button
              className="modal-btn"
              onClick={() => setShowModal(false)}
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
