// components/DashboardContext.tsx
"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

/**
 * A very simple “DashboardContext” that holds a selectedUser object.
 * You can expand this later to store real auth info, fetch from server, etc.
 */

export interface User {
  id: number;
  name: string;
  // (add any other fields you need, e.g. email, etc.)
}

interface DashboardContextType {
  selectedUser: User | null;
  setSelectedUser: (u: User | null) => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(
  undefined
);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  return (
    <DashboardContext.Provider value={{ selectedUser, setSelectedUser }}>
      {children}
    </DashboardContext.Provider>
  );
}

/**
 * Custom hook to consume DashboardContext.
 * If no provider is found, it will throw.
 */
export function useDashboard(): DashboardContextType {
  const ctx = useContext(DashboardContext);
  if (!ctx) {
    throw new Error("useDashboard must be used within a DashboardProvider");
  }
  return ctx;
}
