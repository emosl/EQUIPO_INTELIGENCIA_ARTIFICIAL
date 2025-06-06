// components/UploadCsvDialog.tsx
"use client";

import { useState, useRef, ChangeEvent } from "react";
import { useAuth } from "@/components/AuthContext";
import { Upload, Loader2, Check, X } from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

interface Props {
  isOpen: boolean;
  onClose: () => void;
  sessionId: number; // pass the active Session row id here
}

export default function UploadCsvDialog({ isOpen, onClose, sessionId }: Props) {
  const { user } = useAuth(); // only to ensure we're logged in
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">(
    "idle"
  );
  const [errorMessage, setErrorMessage] = useState<string>("");
  const inputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  function handlePick(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setStatus("idle");
      setErrorMessage("");
    }
  }

  async function handleUpload() {
    if (!file) return;

    if (!BACKEND_URL) {
      setStatus("error");
      setErrorMessage("Backend URL not configured");
      return;
    }

    setStatus("uploading");
    setErrorMessage("");

    const fd = new FormData();
    fd.append("session_id", String(sessionId));
    fd.append("file", file);

    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("No authentication token found");
      }

      const res = await fetch(`${BACKEND_URL}/upload/csv`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || `Upload failed with status ${res.status}`);
      }

      setStatus("done");
      // Auto-close after success (optional)
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      console.error("Upload error:", err);
      setStatus("error");
      setErrorMessage(err instanceof Error ? err.message : "Upload failed");
    }
  }

  const ready = file && status !== "uploading";

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl w-[26rem] p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center">
          <Upload className="w-5 h-5 mr-2" /> Upload EEG CSV
        </h2>

        <input
          ref={inputRef}
          id="csv-file"
          type="file"
          accept=".csv"
          onChange={handlePick}
          className="hidden"
        />
        <label htmlFor="csv-file" className="sr-only">
          Choose CSV file
        </label>

        <button
          onClick={() => inputRef.current?.click()}
          className="w-full py-2 border rounded-md mb-4 hover:bg-gray-50 disabled:opacity-50"
          disabled={status === "uploading"}
        >
          {file ? file.name : "Choose CSV…"}
        </button>

        {/* Error message display */}
        {status === "error" && errorMessage && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{errorMessage}</p>
          </div>
        )}

        {/* Success message */}
        {status === "done" && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-600">
              File uploaded successfully!
            </p>
          </div>
        )}

        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm border rounded-md hover:bg-gray-50"
            disabled={status === "uploading"}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!ready}
            className="px-4 py-2 text-sm text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50 flex items-center"
          >
            {status === "uploading" && (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            )}
            {status === "done" && <Check className="w-4 h-4 mr-2" />}
            {status === "error" && <X className="w-4 h-4 mr-2" />}

            {status === "idle" && "Upload"}
            {status === "uploading" && "Uploading..."}
            {status === "done" && "Done"}
            {status === "error" && "Retry"}
          </button>
        </div>
      </div>
    </div>
  );
}
