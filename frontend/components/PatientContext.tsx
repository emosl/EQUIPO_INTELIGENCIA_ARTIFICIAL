"use client"

import { createContext, useContext, useState, type ReactNode } from "react"

interface Patient {
  id: string
  name: string
  age: number
  gender: string
  lastVisit: string
}

interface PatientContextType {
  selectedPatient: Patient | null
  setSelectedPatient: (patient: Patient | null) => void
  patients: Patient[]
}

const PatientContext = createContext<PatientContextType | undefined>(undefined)

// Sample patient data
const samplePatients: Patient[] = [
  { id: "1", name: "John Smith", age: 45, gender: "Male", lastVisit: "2024-01-15" },
  { id: "2", name: "Sarah Johnson", age: 32, gender: "Female", lastVisit: "2024-01-14" },
  { id: "3", name: "Michael Brown", age: 58, gender: "Male", lastVisit: "2024-01-13" },
  { id: "4", name: "Emily Davis", age: 29, gender: "Female", lastVisit: "2024-01-12" },
  { id: "5", name: "Robert Wilson", age: 67, gender: "Male", lastVisit: "2024-01-11" },
]

export function PatientProvider({ children }: { children: ReactNode }) {
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)

  return (
    <PatientContext.Provider
      value={{
        selectedPatient,
        setSelectedPatient,
        patients: samplePatients,
      }}
    >
      {children}
    </PatientContext.Provider>
  )
}

export function usePatient() {
  const context = useContext(PatientContext)
  if (context === undefined) {
    throw new Error("usePatient must be used within a PatientProvider")
  }
  return context
}
