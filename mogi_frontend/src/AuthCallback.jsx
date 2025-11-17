import { useEffect } from "react";
import { supabase } from "../supabaseClient";
import { useNavigate } from "react-router-dom";

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const processAuth = async () => {
      // 1. Intentar obtener la sesión normal
      let {
        data: { session },
      } = await supabase.auth.getSession();

      // 2. Si no hay sesión, puede ser un email de confirmación → crear sesión desde URL
      if (!session) {
        const { data: exchanged, error } =
          await supabase.auth.exchangeCodeForSession(window.location.href);

        if (error) {
          console.error("Error al intercambiar código:", error);
          return;
        }

        session = exchanged.session;
      }

      // 3. Si aún no hay sesión, nada que hacer
      if (!session) {
        console.log("No se pudo crear una sesión");
        return;
      }

      console.log("Sesion creada:", session);

      // 4. Enviar token a Django
      try {
        const res = await fetch("http://localhost:8000/api/auth/google/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            access_token: session.access_token,
          }),
        });

        const data = await res.json();
        console.log("Respuesta Django:", data);

      } catch (err) {
        console.error("Error enviando token a Django:", err);
      }

      // 5. Redirigir al dashboard
      navigate("/");
    };

    processAuth();
  }, [navigate]);

  return <p>Procesando login...</p>;
};

export default AuthCallback;
