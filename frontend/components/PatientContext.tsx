// src/components/PatientContext.tsx
"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

interface Patient {
  id: number;
  name: string;
  father_surname: string;
  mother_surname: string;
  birth_date: string;
  sex: string;
  lastVisit?: string;
}

interface PatientContextValue {
  patients: Patient[];
  selectedPatient: Patient | null;
  setSelectedPatient: (p: Patient) => void;
  fetchPatients: () => Promise<void>;
}

const PatientContext = createContext<PatientContextValue | undefined>(
  undefined
);

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export function PatientProvider({ children }: { children: ReactNode }) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  async function fetchPatients() {
    if (!BACKEND_URL) {
      console.error("BACKEND_URL is not defined");
      return;
    }

    const token = localStorage.getItem("access_token");
    const userId = localStorage.getItem("user_id");
    if (!token || !userId) return;

    try {
      const res = await fetch(`${BACKEND_URL}/users/${userId}/patients`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        throw new Error("Failed to fetch patients");
      }
      const list = (await res.json()) as Patient[];
      setPatients(list);
    } catch (err) {
      console.error("Error fetching patients:", err);
    }
  }

  // You can choose to fetch on mount or only when modal opens
  useEffect(() => {
    // If you want to load patients immediately on provider mount, uncomment:
    // fetchPatients();
  }, []);

  return (
    <PatientContext.Provider
      value={{ patients, selectedPatient, setSelectedPatient, fetchPatients }}
    >
      {children}
    </PatientContext.Provider>
  );
}

export function usePatient() {
  const ctx = useContext(PatientContext);
  if (!ctx) throw new Error("usePatient must be used inside PatientProvider");
  return ctx;
}
