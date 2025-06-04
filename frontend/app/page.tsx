// app/page.tsx (or pages/index.tsx)

"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import {
  BarChart3,
  BookOpen,
  ArrowRight,
  User as UserIcon,
  Database,
  Brain,
  Users as UsersIcon,
} from "lucide-react";
import { usePatient } from "../components/PatientContext";
import PatientSelectionModal from "../components/PatientSelectionModal";
import DataSetSelectionModal from "../components/DataSetSelectionModal";
import ModelSelectionModal from "../components/ModelSelectionModal";

interface Doctor {
  id: number;
  name: string;
  father_surname: string;
  mother_surname: string;
  medical_department: string;
  email: string;
  is_active: boolean;
}

export default function HomePage() {
  const { selectedPatient } = usePatient();
  const [showPatientModal, setShowPatientModal] = useState(false);
  const [showDataSetModal, setShowDataSetModal] = useState(false);
  const [showModelModal, setShowModelModal] = useState(false);
  const [selectedDataSet, setSelectedDataSet] = useState<any>(null);
  const [selectedModels, setSelectedModels] = useState<any[]>([]);

  // State for doctor’s info
  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  // Fetch /users/me on mount
  useEffect(() => {
    if (!token) return;

    (async () => {
      try {
        const res = await fetch("http://localhost:8000/users/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          console.error("Failed to fetch /users/me");
          return;
        }
        const json: Doctor = await res.json();
        setDoctor(json);
      } catch (e) {
        console.error(e);
      }
    })();
  }, [token]);

  const features = [
    {
      name: "Results",
      description: selectedPatient
        ? `View comprehensive analysis results and historical data for ${selectedPatient.name}`
        : "View and analyze your latest results, metrics, and historical data.",
      href: "/results",
      icon: BarChart3,
      color: "bg-blue-500",
    },
    {
      name: "User Manual",
      description:
        "Learn how to use the application with our comprehensive guide.",
      href: "/user-manual",
      icon: BookOpen,
      color: "bg-purple-500",
    },
  ];

  return (
    <div className="content-wrapper">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Medical Analysis Dashboard
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Your comprehensive solution for patient data analysis, historical
          tracking, and medical insights.
        </p>
      </div>

      {/* Patient Selection Section */}
      <div className="card mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <UsersIcon className="h-5 w-5 mr-2" />
            Patient Selection
          </h2>
        </div>

        {selectedPatient ? (
          <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4">
                <UserIcon className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">
                  {selectedPatient.name}
                </h3>
                <p className="text-sm text-gray-600">
                  ID: {selectedPatient.id} •{" "}
                  {/** compute age from birth_date if you like */}
                  {/* example: {selectedPatient.age} years • {selectedPatient.sex} */}
                  {new Date().getFullYear() -
                    new Date(selectedPatient.birth_date).getFullYear()}{" "}
                  years • {selectedPatient.sex}
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowPatientModal(true)}
              className="px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-md hover:bg-green-200 transition-colors"
            >
              Change Patient
            </button>
          </div>
        ) : (
          <div className="text-center py-8">
            <UserIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No patient selected</p>
            <button
              onClick={() => setShowPatientModal(true)}
              className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors font-medium"
            >
              Select Patient
            </button>
          </div>
        )}
      </div>

      {/* Configuration Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center mb-4">
            <Database className="h-6 w-6 text-blue-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">
              Data Set Selection
            </h3>
          </div>
          {selectedDataSet ? (
            <div className="mb-4">
              <p className="font-medium text-gray-900">
                {selectedDataSet.name}
              </p>
              <p className="text-sm text-gray-600">
                {selectedDataSet.description}
              </p>
            </div>
          ) : (
            <p className="text-gray-500 mb-4">No data set selected</p>
          )}
          <button
            onClick={() => setShowDataSetModal(true)}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
          >
            {selectedDataSet ? "Change Data Set" : "Select Data Set"}
          </button>
        </div>

        <div className="card">
          <div className="flex items-center mb-4">
            <Brain className="h-6 w-6 text-purple-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">
              Model Combination
            </h3>
          </div>
          {selectedModels.length > 0 ? (
            <div className="mb-4">
              <p className="font-medium text-gray-900">
                {selectedModels.length} model(s) selected
              </p>
              <p className="text-sm text-gray-600">
                {selectedModels.map((m) => m.name).join(", ")}
              </p>
            </div>
          ) : (
            <p className="text-gray-500 mb-4">No models selected</p>
          )}
          <button
            onClick={() => setShowModelModal(true)}
            className="w-full px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors font-medium"
          >
            {selectedModels.length > 0 ? "Change Models" : "Select Models"}
          </button>
        </div>
      </div>

      {/* Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((feature) => {
          const Icon = feature.icon;
          const isDisabled =
            (feature.name === "Results" || feature.name === "Historic Data") &&
            !selectedPatient;

          return (
            <div
              key={feature.name}
              className={`card hover:shadow-lg transition-shadow duration-300 group ${
                isDisabled ? "opacity-50" : ""
              }`}
            >
              <div className="flex items-center mb-4">
                <div className={`${feature.color} p-3 rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="ml-4 text-xl font-semibold text-gray-900">
                  {feature.name}
                </h3>
              </div>
              <p className="text-gray-600 mb-4">{feature.description}</p>
              {isDisabled ? (
                <div className="flex items-center text-gray-400">
                  <span className="text-sm font-medium">
                    Select a patient first
                  </span>
                </div>
              ) : (
                <Link
                  href={feature.href}
                  className="flex items-center text-primary-600 group-hover:text-primary-700"
                >
                  <span className="text-sm font-medium">Learn more</span>
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              )}
            </div>
          );
        })}
      </div>

      {/* Modals */}
      <PatientSelectionModal
        isOpen={showPatientModal}
        onClose={() => setShowPatientModal(false)}
      />
      <DataSetSelectionModal
        isOpen={showDataSetModal}
        onClose={() => setShowDataSetModal(false)}
        selectedDataSet={selectedDataSet}
        onSelectDataSet={setSelectedDataSet}
      />
      <ModelSelectionModal
        isOpen={showModelModal}
        onClose={() => setShowModelModal(false)}
        selectedModels={selectedModels}
        onSelectModels={setSelectedModels}
      />
    </div>
  );
}
