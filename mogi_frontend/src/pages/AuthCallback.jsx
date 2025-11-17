import { useEffect } from "react";
import { supabase } from "../supabaseClient";
import { useNavigate } from "react-router-dom";

export default function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    async function handleOAuth() {
      const { data, error } = await supabase.auth.getSession();

      if (error) {
        console.error("Error obteniendo sesion:", error);
        return;
      }

      console.log("Sesion:", data.session); // <--- AQUI VES LA SESION

      if (data.session) {
        navigate("/dashboard");
      }
    }

    handleOAuth();
  }, [navigate]);

  return <p>Validando autenticacion...</p>;
}
