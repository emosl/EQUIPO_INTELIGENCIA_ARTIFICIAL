// src/components/DataSetSelectionModal.tsx

"use client";

import { useState, useRef, useEffect, ChangeEvent } from "react";
import { X, Database, Check, Upload, Loader2, Plus } from "lucide-react";
import { useAuth } from "@/components/AuthContext";
import { usePatient } from "@/components/PatientContext";

export interface DataSet {
  id: string;
  name: string;
  description: string;
  size: string;
  lastUpdated: string;
}

interface DataSetSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDataSet: DataSet | null;
  onSelectDataSet: (ds: DataSet) => void;
}

export default function DataSetSelectionModal({
  isOpen,
  onClose,
  selectedDataSet,
  onSelectDataSet,
}: DataSetSelectionModalProps) {
  const { user } = useAuth();
  const { selectedPatient } = usePatient();
  const [dataSets, setDataSets] = useState<DataSet[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<
    "idle" | "uploading" | "done" | "error"
  >("idle");
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [newSessionName, setNewSessionName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const createNewOption: DataSet = {
      id: "create-new",
      name: "Create New Session",
      description: selectedPatient
        ? `Create new session for ${selectedPatient.name} ${selectedPatient.father_surname}`
        : "Select a patient first to create a new session",
      size: "New",
      lastUpdated: "Now",
    };

    async function fetchSessions() {
      try {
        const token = localStorage.getItem("access_token");
        const res = await fetch("http://localhost:8000/sessions", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const json: DataSet[] = await res.json();

          // Filter out sessions that have no EEG data (size === "0 B")
          const withData = json.filter((ds) => ds.size !== "0 B");
          setDataSets([createNewOption, ...withData]);
        } else {
          setDataSets([createNewOption]);
        }
      } catch (err) {
        console.error("Network error loading sessions", err);
        setDataSets([createNewOption]);
      }
    }

    if (isOpen) {
      fetchSessions();
      setFile(null);
      setUploadState("idle");
      setIsCreatingNew(false);
      setNewSessionName("");
    }
  }, [isOpen, selectedPatient]);

  if (!isOpen) return null;

  function handleFilePick(e: ChangeEvent<HTMLInputElement>) {
    const chosen = e.target.files?.[0];
    if (chosen) setFile(chosen);
  }

  function handleDataSetSelect(ds: DataSet) {
    onSelectDataSet(ds);
    setIsCreatingNew(ds.id === "create-new");
  }

  async function handleConfirm() {
    if (!selectedDataSet || !file) return;
    setUploadState("uploading");

    try {
      const token = localStorage.getItem("access_token");

      if (selectedDataSet.id === "create-new") {
        if (!selectedPatient) {
          throw new Error("Please select a patient first");
        }

        // Create new session for the selected patient
        const createRes = await fetch(
          "http://localhost:8000/create-session-for-patient",
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              patient_id: selectedPatient.id,
              session_name:
                newSessionName ||
                `Session ${new Date().toISOString().split("T")[0]}`,
            }),
          }
        );

        if (!createRes.ok) throw new Error(await createRes.text());
        const { session_id } = await createRes.json();

        // Upload CSV to the new session
        const fd = new FormData();
        fd.append("session_id", session_id);
        fd.append("file", file);

        const uploadRes = await fetch("http://localhost:8000/upload/csv", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: fd,
        });

        if (!uploadRes.ok) throw new Error(await uploadRes.text());
      } else {
        // Upload to existing session
        const fd = new FormData();
        fd.append("session_id", selectedDataSet.id);
        fd.append("file", file);

        const res = await fetch("http://localhost:8000/upload/csv", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: fd,
        });

        if (!res.ok) throw new Error(await res.text());
      }

      setUploadState("done");
      setTimeout(onClose, 1000);
    } catch (err) {
      console.error(err);
      setUploadState("error");
    }
  }

  const confirmDisabled =
    !selectedDataSet ||
    !file ||
    uploadState === "uploading" ||
    (isCreatingNew && (!newSessionName.trim() || !selectedPatient));

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl mx-4 max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold flex items-center text-gray-900">
            <Database className="h-5 w-5 mr-2" />
            {isCreatingNew ? "Create New Session" : "Select Data Set"} &amp;
            Upload CSV
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close dialog"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Data set grid */}
          <div className="grid gap-4">
            {dataSets.map((ds) => (
              <div
                key={ds.id}
                onClick={() => handleDataSetSelect(ds)}
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                  selectedDataSet?.id === ds.id
                    ? "border-primary-500 bg-primary-50"
                    : "border-gray-200 hover:border-gray-300"
                } ${ds.id === "create-new" ? "border-dashed" : ""}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      {ds.id === "create-new" && (
                        <Plus className="h-5 w-5 mr-2 text-primary-600" />
                      )}
                      <h3 className="font-medium text-gray-900">{ds.name}</h3>
                      {selectedDataSet?.id === ds.id && (
                        <Check className="h-5 w-5 text-primary-600 ml-2" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {ds.description}
                    </p>
                    {ds.id !== "create-new" && (
                      <div className="flex items-center mt-2 text-xs text-gray-500">
                        <span>Size: {ds.size}</span>
                        <span className="mx-2">•</span>
                        <span>Updated: {ds.lastUpdated}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* New session form */}
          {isCreatingNew && (
            <div className="bg-gray-50 p-4 rounded-lg space-y-4">
              <h4 className="font-medium text-gray-900">New Session Details</h4>
              {selectedPatient ? (
                <div className="bg-white p-3 rounded border">
                  <p className="text-sm text-gray-600">Creating session for:</p>
                  <p className="font-medium text-gray-900">
                    {selectedPatient.name} {selectedPatient.father_surname}
                  </p>
                </div>
              ) : (
                <div className="bg-red-50 p-3 rounded border border-red-200">
                  <p className="text-sm text-red-600">
                    Please select a patient first before creating a new session.
                  </p>
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Session Name
                </label>
                <input
                  type="text"
                  value={newSessionName}
                  onChange={(e) => setNewSessionName(e.target.value)}
                  placeholder="e.g., EEG Session - 2024-01-15"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  disabled={!selectedPatient}
                />
              </div>
            </div>
          )}

          {/* File picker */}
          <div>
            <input
              ref={fileInputRef}
              id="csv-file"
              type="file"
              accept=".csv"
              onChange={handleFilePick}
              className="hidden"
              aria-label="Choose EEG CSV file"
            />
            <label
              htmlFor="csv-file"
              className="flex items-center justify-center w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-md cursor-pointer hover:bg-gray-50"
            >
              <Upload className="h-5 w-5 mr-2" />
              {file ? file.name : "Click to choose EEG CSV…"}
            </label>
            {!file && (
              <p className="mt-1 text-xs text-gray-500">
                CSV must include af3, f7, f3, fc5, …, af4 columns.
              </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            disabled={uploadState === "uploading"}
          >
            Cancel
          </button>

          <button
            onClick={handleConfirm}
            disabled={confirmDisabled}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploadState === "idle" &&
              (isCreatingNew ? "Create & Upload" : "Confirm Upload")}
            {uploadState === "uploading" && (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin inline" />
                {isCreatingNew ? "Creating..." : "Uploading..."}
              </>
            )}
            {uploadState === "done" && (
              <>
                <Check className="h-4 w-4 mr-2" /> Done
              </>
            )}
            {uploadState === "error" && (
              <>
                <X className="h-4 w-4 mr-2" /> Failed — retry
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
