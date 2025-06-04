"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import { useRouter, usePathname } from "next/navigation";

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
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  const [justLoggedIn, setJustLoggedIn] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // 1) On mount, check for a stored JWT and fetch /users/me if present
  useEffect(() => {
    (async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          // Call /users/me to get the doctor's full info
          const res = await fetch("http://localhost:8000/users/me", {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (res.ok) {
            const meJson: User = await res.json();
            setUser(meJson);
            localStorage.setItem("user", JSON.stringify(meJson));
          } else {
            // Token might be invalid/expired → clear it
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
            setUser(null);
          }
        } catch (error) {
          console.error("Auth check error:", error);
          // Clear potentially corrupted data on error
          localStorage.removeItem("access_token");
          localStorage.removeItem("user");
          setUser(null);
        }
      }
      setIsLoading(false);
      setIsInitialized(true);
    })();
  }, []);

  // 2) Redirect to /login if not authenticated (only after initialization and not just logged in)
  useEffect(() => {
    if (
      isInitialized &&
      !isLoading &&
      !user &&
      !justLoggedIn &&
      pathname !== "/login"
    ) {
      router.push("/login");
    }
  }, [user, isLoading, isInitialized, justLoggedIn, pathname, router]);

  // 3) login() now calls /login (form), stores JWT, then immediately calls /users/me
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setJustLoggedIn(true); // Prevent immediate redirect

    try {
      // Build form‐encoded body for OAuth2
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);

      const loginRes = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form.toString(),
      });

      if (!loginRes.ok) {
        setIsLoading(false);
        setJustLoggedIn(false);
        return false;
      }

      const { access_token } = await loginRes.json();
      localStorage.setItem("access_token", access_token);

      // Fetch /users/me to get the full doctor record (including father_surname)
      const meRes = await fetch("http://localhost:8000/users/me", {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      if (!meRes.ok) {
        // Clean up if /users/me fails
        localStorage.removeItem("access_token");
        setIsLoading(false);
        setJustLoggedIn(false);
        return false;
      }

      const meJson: User = await meRes.json();
      setUser(meJson);
      localStorage.setItem("user", JSON.stringify(meJson));

      setIsLoading(false);

      // Clear the "just logged in" flag after a short delay to allow navigation
      setTimeout(() => {
        setJustLoggedIn(false);
      }, 1000);

      return true;
    } catch (error) {
      console.error("Login error:", error);
      // Clean up on error
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      setUser(null);
      setIsLoading(false);
      setJustLoggedIn(false);
      return false;
    }
  };

  const logout = () => {
    // Clear state first
    setUser(null);
    setIsLoading(false);
    setJustLoggedIn(false); // Reset the login flag

    // Clear localStorage
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    // Navigate to login
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
