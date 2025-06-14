// src/context/AuthContext.tsx

"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  PropsWithChildren,
} from "react";
import { useRouter, usePathname } from "next/navigation";

/**
 * ---------------------------------------------------------------------------
 *  Environment Variable for Backend URL
 * ---------------------------------------------------------------------------
 */
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

/**
 * ---------------------------------------------------------------------------
 *  Types
 * ---------------------------------------------------------------------------
 */
interface User {
  id: string;
  name: string;
  father_surname: string;
  email: string;
  role?: string;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
}

/**
 * ---------------------------------------------------------------------------
 *  Context
 * ---------------------------------------------------------------------------
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * ---------------------------------------------------------------------------
 *  Provider
 * ---------------------------------------------------------------------------
 */

export function AuthProvider({ children }: PropsWithChildren<{}>) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  const [justLoggedIn, setJustLoggedIn] = useState(false);

  const router = useRouter();
  const pathname = usePathname();

  /**
   * 1) On first mount → check for a stored JWT and, if present, fetch /users/me.
   */
  useEffect(() => {
    (async () => {
      const token = localStorage.getItem("access_token");
      if (token && BACKEND_URL) {
        try {
          const res = await fetch(`${BACKEND_URL}/users/me`, {
            headers: { Authorization: `Bearer ${token}` },
          });

          if (res.ok) {
            const me: User = await res.json();
            setUser(me);
            localStorage.setItem("user", JSON.stringify(me));
          } else {
            // bad / expired token
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
            setUser(null);
          }
        } catch (err) {
          console.error("Auth check error", err);
          localStorage.removeItem("access_token");
          localStorage.removeItem("user");
          setUser(null);
        }
      }

      setIsLoading(false);
      setIsInitialized(true);
    })();
  }, []);

  /**
   * 2) Client-side guard: redirect to /login *only* once auth state is known.
   */
  useEffect(() => {
    const tokenExists =
      typeof window !== "undefined" &&
      Boolean(localStorage.getItem("access_token"));

    if (
      isInitialized &&
      !isLoading &&
      !user &&
      !justLoggedIn &&
      !tokenExists &&
      pathname !== "/login"
    ) {
      router.push("/login");
    }
  }, [user, isLoading, isInitialized, justLoggedIn, pathname, router]);

  /**
   * login() → POST /login  ➜ store JWT ➜ GET /users/me ➜ navigate to dashboard
   */
  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setJustLoggedIn(true);

    if (!BACKEND_URL) {
      console.error("BACKEND_URL is not defined");
      setIsLoading(false);
      setJustLoggedIn(false);
      return false;
    }

    try {
      const body = new URLSearchParams();
      body.append("username", email);
      body.append("password", password);

      const res = await fetch(`${BACKEND_URL}/loginApi`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString(),
      });

      if (!res.ok) throw new Error("Invalid credentials");

      const { access_token } = await res.json();
      localStorage.setItem("access_token", access_token);

      const meRes = await fetch(`${BACKEND_URL}/users/me`, {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      if (!meRes.ok) throw new Error("/users/me fetch failed");

      const me: User = await meRes.json();
      setUser(me);
      localStorage.setItem("user", JSON.stringify(me));

      // Small delay before clearing justLoggedIn, to avoid immediate redirect
      setTimeout(() => setJustLoggedIn(false), 500);

      // Navigate to the default protected page
      router.push("/results");

      return true;
    } catch (err) {
      console.error("Login error", err);
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      setUser(null);
      setJustLoggedIn(false);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * logout() → clear tokens, reset state, redirect to /login
   */
  const logout = async (): Promise<void> => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
    setIsLoading(false);
    setJustLoggedIn(false);
    router.push("/login");
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * ---------------------------------------------------------------------------
 *  useAuth() hook – import this throughout the app
 * ---------------------------------------------------------------------------
 */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
