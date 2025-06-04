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

export function PatientProvider({ children }: { children: ReactNode }) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  async function fetchPatients() {
    // Replace this with your actual “GET /users/{user_id}/patients” call.
    // For example, read token/userId from localStorage and hit your FastAPI route.
    const token = localStorage.getItem("access_token");
    const userId = localStorage.getItem("user_id");
    if (!token || !userId) return;

    const res = await fetch(`http://localhost:8000/users/${userId}/patients`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) throw new Error("Failed to fetch patients");
    const list = (await res.json()) as Patient[];
    setPatients(list);
  }

  // Optionally, fetch on mount if you want.
  useEffect(() => {
    // …or wait until your modal opens to call fetchPatients()
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
