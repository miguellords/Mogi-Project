import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
    "https://okpdneacoyzchbolspch.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9rcGRuZWFjb3l6Y2hib2xzcGNoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxNjQwNDIsImV4cCI6MjA3ODc0MDA0Mn0.MtovbXHx7nOMANTRCgy_TuVDP4gnnIY7Sedchgta9R8",
  {
    auth: {
      persistSession: true,   // ⬅ IMPORTANTE
      autoRefreshToken: true, // ⬅ IMPORTANTE
      detectSessionInUrl: true,
    },
  }
);
