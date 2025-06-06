// components/PatientSelectionModal.tsx
"use client";

import { useState, useEffect } from "react";
// Remove useRouter import since we're not using it anymore
import { X, Search, User as UserIcon, Users as UsersIcon } from "lucide-react";
import { usePatient } from "./PatientContext";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

interface PatientSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
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
}: PatientSelectionModalProps) {
  // Remove router since we're not using it
  const { patients, selectedPatient, setSelectedPatient, fetchPatients } =
    usePatient();

  const [searchTerm, setSearchTerm] = useState("");
  const [showNewForm, setShowNewForm] = useState(false);
  const [newPatientData, setNewPatientData] = useState({
    name: "",
    father_surname: "",
    mother_surname: "",
    birth_date: "",
    sex: "",
  });
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      fetchPatients();
      setSearchTerm("");
      setShowNewForm(false);
      setNewPatientData({
        name: "",
        father_surname: "",
        mother_surname: "",
        birth_date: "",
        sex: "",
      });
      setError("");
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
    onClose(); // Just close the modal, don't navigate

    // Optional: Show a success message or update UI to indicate patient is selected
    // You could add a toast notification here if you have one
  };

  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const userId =
    typeof window !== "undefined" ? localStorage.getItem("user_id") : null;

  const handleCreatePatient = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!token || !userId) {
      setError("Not authenticated.");
      return;
    }
    if (!BACKEND_URL) {
      setError("Backend URL not configured.");
      return;
    }
    const { name, father_surname, mother_surname, birth_date, sex } =
      newPatientData;
    if (!name || !father_surname || !mother_surname || !birth_date || !sex) {
      setError("All fields are required.");
      return;
    }
    try {
      const res = await fetch(`${BACKEND_URL}/users/${userId}/patients`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(newPatientData),
      });
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || "Failed to create patient");
      }
      setShowNewForm(false);
      setNewPatientData({
        name: "",
        father_surname: "",
        mother_surname: "",
        birth_date: "",
        sex: "",
      });
      await fetchPatients();
    } catch (err: any) {
      setError(err.message);
    }
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

        {/* Create new patient toggle */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={() => setShowNewForm((prev) => !prev)}
            className="text-sm text-primary-600 hover:text-primary-500 font-medium"
          >
            {showNewForm ? "Cancel" : "➕ Create New Patient"}
          </button>
        </div>

        {/* New Patient Form */}
        {showNewForm && (
          <form onSubmit={handleCreatePatient} className="p-6 space-y-4">
            {error && (
              <div className="text-sm text-red-600 border border-red-200 bg-red-50 p-2 rounded">
                {error}
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* First name */}
              <div>
                <label
                  htmlFor="new-name"
                  className="block text-sm font-medium text-gray-700"
                >
                  First Name
                </label>
                <input
                  id="new-name"
                  type="text"
                  required
                  value={newPatientData.name}
                  onChange={(e) =>
                    setNewPatientData((prev) => ({
                      ...prev,
                      name: e.target.value,
                    }))
                  }
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="First Name"
                />
              </div>
              {/* Father's surname */}
              <div>
                <label
                  htmlFor="new-father"
                  className="block text-sm font-medium text-gray-700"
                >
                  Last Name (Father)
                </label>
                <input
                  id="new-father"
                  type="text"
                  required
                  value={newPatientData.father_surname}
                  onChange={(e) =>
                    setNewPatientData((prev) => ({
                      ...prev,
                      father_surname: e.target.value,
                    }))
                  }
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Father's surname"
                />
              </div>
              {/* Mother's surname */}
              <div>
                <label
                  htmlFor="new-mother"
                  className="block text-sm font-medium text-gray-700"
                >
                  Last Name (Mother)
                </label>
                <input
                  id="new-mother"
                  type="text"
                  required
                  value={newPatientData.mother_surname}
                  onChange={(e) =>
                    setNewPatientData((prev) => ({
                      ...prev,
                      mother_surname: e.target.value,
                    }))
                  }
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Mother's surname"
                />
              </div>
              {/* Birth date */}
              <div>
                <label
                  htmlFor="new-birthdate"
                  className="block text-sm font-medium text-gray-700"
                >
                  Birth Date
                </label>
                <input
                  id="new-birthdate"
                  type="date"
                  required
                  value={newPatientData.birth_date}
                  onChange={(e) =>
                    setNewPatientData((prev) => ({
                      ...prev,
                      birth_date: e.target.value,
                    }))
                  }
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              {/* Sex */}
              <div>
                <label
                  htmlFor="new-sex"
                  className="block text-sm font-medium text-gray-700"
                >
                  Sex
                </label>
                <select
                  id="new-sex"
                  required
                  value={newPatientData.sex}
                  onChange={(e) =>
                    setNewPatientData((prev) => ({
                      ...prev,
                      sex: e.target.value,
                    }))
                  }
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Select Sex</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </div>
            </div>
            <div className="pt-4 border-t border-gray-200 flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Create Patient
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
