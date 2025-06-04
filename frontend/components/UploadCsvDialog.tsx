// components/UploadCsvDialog.tsx
"use client";

import { useState, useRef, ChangeEvent } from "react";
import { useAuth } from "@/components/AuthContext";
import { Upload, Loader2, Check, X } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  sessionId: number; // pass the active Session row id here
}

export default function UploadCsvDialog({ isOpen, onClose, sessionId }: Props) {
  const { user } = useAuth(); // only to ensure we’re logged in
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">(
    "idle"
  );
  const inputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  function handlePick(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) setFile(f);
  }

  async function handleUpload() {
    if (!file) return;
    setStatus("uploading");

    const fd = new FormData();
    fd.append("session_id", String(sessionId));
    fd.append("file", file);

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("http://localhost:8000/upload/csv", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });

      if (!res.ok) throw new Error(await res.text());
      setStatus("done");
    } catch (err) {
      console.error(err);
      setStatus("error");
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
          className="w-full py-2 border rounded-md mb-4 hover:bg-gray-50"
        >
          {file ? file.name : "Choose CSV…"}
        </button>

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
            className="px-4 py-2 text-sm text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50"
          >
            {status === "uploading" && (
              <Loader2 className="w-4 h-4 mr-2 animate-spin inline" />
            )}
            {status === "idle" && "Upload"}
            {status === "done" && (
              <>
                <Check className="w-4 h-4 mr-2" /> Done
              </>
            )}
            {status === "error" && (
              <>
                <X className="w-4 h-4 mr-2" /> Failed — retry
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
