// components/PatientContext.tsx

"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

export interface Patient {
  id: number;
  name: string;
  father_surname: string;
  mother_surname: string;
  birth_date: string; // e.g. "1985-02-10"
  sex: string; // "M" or "F"
  // add any other fields returned by your API (age, lastVisit, etc.)
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

export function usePatient() {
  const ctx = useContext(PatientContext);
  if (!ctx) throw new Error("usePatient must be used within PatientProvider");
  return ctx;
}

interface PatientProviderProps {
  children: ReactNode;
}

export function PatientProvider({ children }: PatientProviderProps) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  // Pull token & user_id from localStorage
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const userId =
    typeof window !== "undefined" ? localStorage.getItem("user_id") : null;

  async function fetchPatients() {
    if (!token || !userId) return;

    try {
      const res = await fetch(
        `http://localhost:8000/users/${userId}/patients`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!res.ok) {
        console.error("Failed to fetch patients", await res.text());
        return;
      }
      const data: Patient[] = await res.json();
      setPatients(data);
    } catch (err) {
      console.error("Error fetching patients:", err);
    }
  }

  // Whenever the provider mounts (or userId changes), fetch patients once.
  useEffect(() => {
    if (token && userId) {
      fetchPatients();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, userId]);

  return (
    <PatientContext.Provider
      value={{ patients, selectedPatient, setSelectedPatient, fetchPatients }}
    >
      {children}
    </PatientContext.Provider>
  );
}
