// components/CreatePatient.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, User, Save, X } from "lucide-react";
import { usePatient } from "./PatientContext";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

interface NewPatientData {
  name: string;
  father_surname: string;
  mother_surname: string;
  birth_date: string;
  sex: string;
  email: string;
}

interface CreatePatientProps {
  onClose: () => void;
}

export default function CreatePatient({ onClose }: CreatePatientProps) {
  const router = useRouter();
  const { fetchPatients, setSelectedPatient } = usePatient();

  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const [newPatientData, setNewPatientData] = useState<NewPatientData>({
    name: "",
    father_surname: "",
    mother_surname: "",
    birth_date: "",
    sex: "",
    email: "",
  });

  // Read token + userId from localStorage
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  let userId: string | null = null;
  if (typeof window !== "undefined") {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser) as { id: string };
        userId = parsed.id;
      } catch {
        userId = null;
      }
    }
  }

  // Handle any field change, including "email"
  const handleInputChange = (field: keyof NewPatientData, value: string) => {
    // console.log(Updating field "${field}" with value:, value);
    setNewPatientData((prev) => {
      const updated = {
        ...prev,
        [field]: value,
      };
      console.log("📊 Updated state:", updated);
      return updated;
    });
    if (error) setError("");
  };

  // Basic front‐end validation
  const validateForm = (): string | null => {
    const { name, father_surname, mother_surname, birth_date, sex, email } =
      newPatientData;

    console.log("🔍 Validating form data:", newPatientData);

    if (!name.trim()) return "First name is required";
    if (!father_surname.trim()) return "Father's surname is required";
    if (!mother_surname.trim()) return "Mother's surname is required";
    if (!birth_date) return "Birth date is required";
    if (!sex) return "Sex is required";

    // Simple email check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    console.log(
      "📧 Email validation - value:",
      email,
      "valid:",
      emailRegex.test(email)
    );
    if (!email.trim() || !emailRegex.test(email)) {
      return "A valid email is required";
    }

    const birthDate = new Date(birth_date);
    const today = new Date();
    if (birthDate > today) return "Birth date cannot be in the future";

    const age = today.getFullYear() - birthDate.getFullYear();
    if (age > 150) return "Invalid birth date";

    return null;
  };

  const handleCreatePatient = async () => {
    setError("");
    setIsCreating(true);

    try {
      if (!token || !userId) {
        throw new Error("Not authenticated. Please log in again.");
      }
      if (!BACKEND_URL) {
        throw new Error("Backend URL not configured.");
      }

      const validationError = validateForm();
      if (validationError) {
        throw new Error(validationError);
      }

      // Log the exact data being sent
      console.log("🚀 Creating patient with data:", newPatientData);
      console.log("📧 Email specifically:", {
        value: newPatientData.email,
        type: typeof newPatientData.email,
        length: newPatientData.email.length,
        trimmed: newPatientData.email.trim(),
      });

      // Create the request body
      const requestBody = JSON.stringify(newPatientData);
      console.log("📤 Request body:", requestBody);

      const url = `${BACKEND_URL}/users/${userId}/patients`;
      console.log("🔗 Request URL:", url);

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: requestBody,
      });

      console.log("📨 Response status:", response.status);

      if (!response.ok) {
        // Parse backend validation errors if any
        const errorData = await response.json().catch(() => ({} as any));
        console.log(
          "💥 CreatePatient payload was rejected, errorData =",
          errorData
        );

        let message = `Failed to create patient (${response.status})`;
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            message = errorData.detail
              .map((item: any) => item.msg || JSON.stringify(item))
              .join("; ");
          } else if (typeof errorData.detail === "string") {
            message = errorData.detail;
          } else {
            message = JSON.stringify(errorData.detail);
          }
        }

        throw new Error(message);
      }

      const createdPatient = await response.json();
      console.log("✅ Patient created successfully:", createdPatient);

      setSuccess(true);
      await fetchPatients();
      setSelectedPatient(createdPatient);

      // Close after brief delay for user to see success
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      console.error("❌ Error creating patient:", err);
      setError(err.message);
    } finally {
      setIsCreating(false);
    }
  };

  const handleCancel = () => {
    onClose();
  };

  // Show a small success overlay before closing
  if (success) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="h-8 w-8 text-green-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Patient Created Successfully!
            </h2>
            <p className="text-gray-600 mb-4">
              {newPatientData.name} {newPatientData.father_surname} has been
              added to your patients.
            </p>
            <p className="text-sm text-gray-500">Closing…</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center">
            <button
              type="button"
              onClick={handleCancel}
              aria-label="Go back"
              className="mr-4 p-2 text-gray-400 hover:text-gray-600 rounded-md"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <h1 className="text-xl font-semibold text-gray-900 flex items-center">
              <User className="h-6 w-6 mr-2 text-primary-600" />
              Create New Patient
            </h1>
          </div>
          <button
            type="button"
            onClick={handleCancel}
            aria-label="Close"
            className="p-2 text-gray-400 hover:text-gray-600 rounded-md"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Main Content */}
        <div className="p-6">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex">
                <X
                  className="h-5 w-5 text-red-400 mr-2 mt-0.5"
                  aria-hidden="true"
                />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Debug info - remove in production */}
          <div className="mb-4 p-3 bg-gray-100 rounded text-xs font-mono">
            <p>Current email value: "{newPatientData.email}"</p>
            <p>Email length: {newPatientData.email.length}</p>
          </div>

          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* First Name */}
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  First Name *
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  disabled={isCreating}
                  value={newPatientData.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
                  placeholder="Enter first name"
                />
              </div>

              {/* Father's Surname */}
              <div>
                <label
                  htmlFor="father_surname"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Father's Surname *
                </label>
                <input
                  id="father_surname"
                  type="text"
                  required
                  disabled={isCreating}
                  value={newPatientData.father_surname}
                  onChange={(e) =>
                    handleInputChange("father_surname", e.target.value)
                  }
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
                  placeholder="Enter father's surname"
                />
              </div>

              {/* Mother's Surname */}
              <div>
                <label
                  htmlFor="mother_surname"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Mother's Surname *
                </label>
                <input
                  id="mother_surname"
                  type="text"
                  required
                  disabled={isCreating}
                  value={newPatientData.mother_surname}
                  onChange={(e) =>
                    handleInputChange("mother_surname", e.target.value)
                  }
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
                  placeholder="Enter mother's surname"
                />
              </div>

              {/* Birth Date */}
              <div>
                <label
                  htmlFor="birth_date"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Birth Date *
                </label>
                <input
                  id="birth_date"
                  type="date"
                  required
                  disabled={isCreating}
                  value={newPatientData.birth_date}
                  onChange={(e) =>
                    handleInputChange("birth_date", e.target.value)
                  }
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
                />
              </div>

              {/* Sex */}
              <div>
                <label
                  htmlFor="sex"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Sex *
                </label>
                <select
                  id="sex"
                  required
                  disabled={isCreating}
                  value={newPatientData.sex}
                  onChange={(e) => handleInputChange("sex", e.target.value)}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
                >
                  <option value="">Select sex</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </div>

              {/* Email (required) */}
              <div className="md:col-span-2">
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Email *
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  disabled={isCreating}
                  value={newPatientData.email}
                  onChange={(e) => {
                    console.log(
                      "📧 Email onChange fired with:",
                      e.target.value
                    );
                    handleInputChange("email", e.target.value);
                  }}
                  onBlur={(e) => {
                    console.log(
                      "📧 Email onBlur - current value:",
                      e.target.value
                    );
                  }}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
                  placeholder="Enter patient's email"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg flex justify-end space-x-3">
          <button
            type="button"
            onClick={handleCancel}
            disabled={isCreating}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleCreatePatient}
            disabled={isCreating}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isCreating ? (
              <>
                <div
                  className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"
                  aria-hidden="true"
                ></div>
                Creating...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Create Patient
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}