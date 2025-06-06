// components/PatientSelectionModal.tsx
"use client";

import { useState, useEffect } from "react";
import {
  X,
  Search,
  User as UserIcon,
  Users as UsersIcon,
  Plus,
} from "lucide-react";
import { usePatient } from "./PatientContext";

interface PatientSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateNewPatient: () => void; // ← new prop
}

interface Patient {
  id: number;
  name: string;
  father_surname: string;
  mother_surname: string;
  birth_date: string;
  sex: string;
  lastVisit?: string;
}

export default function PatientSelectionModal({
  isOpen,
  onClose,
  onCreateNewPatient, // ← destructure it
}: PatientSelectionModalProps) {
  const { patients, selectedPatient, setSelectedPatient, fetchPatients } =
    usePatient();
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    if (isOpen) {
      fetchPatients();
      setSearchTerm("");
    }
  }, [isOpen, fetchPatients]);

  if (!isOpen) return null;

  const filteredPatients = patients.filter(
    (patient) =>
      patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(patient.id).includes(searchTerm)
  );

  const handleSelectPatient = (patient: Patient) => {
    setSelectedPatient(patient);
    onClose();
  };

  const handleCreateNewPatient = () => {
    onClose(); // close this modal
    onCreateNewPatient(); // tell the parent: “Please open the CreatePatient modal”
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <UserIcon className="h-5 w-5 mr-2" />
            Select Patient
            {selectedPatient && (
              <span className="ml-3 text-sm font-normal text-green-600">
                (Currently: {selectedPatient.name})
              </span>
            )}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close patient selection"
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Search box */}
        <div className="p-6 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        {/* Patient list */}
        <div className="overflow-y-auto max-h-60">
          {filteredPatients.map((patient) => (
            <div
              key={patient.id}
              onClick={() => handleSelectPatient(patient)}
              className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors ${
                selectedPatient?.id === patient.id
                  ? "bg-primary-50 border-primary-200"
                  : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                    <UsersIcon className="h-5 w-5 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {patient.name} {patient.father_surname}{" "}
                      {patient.mother_surname}
                    </h3>
                    <p className="text-sm text-gray-600">
                      ID: {patient.id} •{" "}
                      {new Date().getFullYear() -
                        new Date(patient.birth_date).getFullYear()}{" "}
                      years • {patient.sex}
                    </p>
                  </div>
                </div>
                {selectedPatient?.id === patient.id && (
                  <div className="text-green-600 text-sm font-medium">
                    ✓ Selected
                  </div>
                )}
              </div>
            </div>
          ))}

          {filteredPatients.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              <UsersIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No patients found matching your search.</p>
            </div>
          )}
        </div>

        {/* Create new patient button */}
        <div className="p-6 border-t border-gray-200">
          <button
            type="button"
            onClick={handleCreateNewPatient}
            className="w-full flex items-center justify-center px-4 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors font-medium"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create New Patient
          </button>
        </div>
      </div>
    </div>
  );
}