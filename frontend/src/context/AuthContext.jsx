import React, { createContext, useContext, useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const AuthContext = createContext();

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase = (supabaseUrl && supabaseAnonKey && !supabaseUrl.includes('your-project'))
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({
    id: 'demo_user',
    email: 'student@contestmate.dev',
    user_metadata: { name: '대학생 사용자' }
  });
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!supabase) return;

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.user) {
        setUser(session.user);
        localStorage.setItem('supabase_access_token', session.access_token);
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session?.user) {
        setUser(session.user);
        localStorage.setItem('supabase_access_token', session.access_token);
      } else {
        localStorage.removeItem('supabase_access_token');
      }
    });

    return () => subscription?.unsubscribe();
  }, []);

  const loginWithEmail = async (email, password) => {
    if (!supabase) {
      setUser({ id: 'demo_user', email, user_metadata: { name: '대학생 사용자' } });
      return { success: true };
    }
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data;
  };

  const signUpWithEmail = async (email, password) => {
    if (!supabase) {
      setUser({ id: 'demo_user', email, user_metadata: { name: '대학생 사용자' } });
      return { success: true };
    }
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) throw error;
    return data;
  };

  const logout = async () => {
    if (supabase) {
      await supabase.auth.signOut();
    }
    localStorage.removeItem('supabase_access_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, loginWithEmail, signUpWithEmail, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
