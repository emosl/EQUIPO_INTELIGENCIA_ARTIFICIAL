"use client";

import { useState, useRef, useEffect, ChangeEvent } from "react";
import { useAuth } from "@/components/AuthContext";
import { X, Database, Check, Upload, Loader2 } from "lucide-react";

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
  // ------------------------------------------------------------------------
  // Hooks must always run in the same order
  // ------------------------------------------------------------------------
  const { user } = useAuth(); // guard by auth if needed
  const [dataSets, setDataSets] = useState<DataSet[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<
    "idle" | "uploading" | "done" | "error"
  >("idle");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ------------------------------------------------------------------------
  // Fetch sessions (datasets) when modal opens
  // ------------------------------------------------------------------------
  useEffect(() => {
    async function fetchSessions() {
      try {
        const token = localStorage.getItem("access_token");
        const res = await fetch("http://localhost:8000/sessions", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const json: DataSet[] = await res.json();
          setDataSets(json);
        } else {
          console.error("Failed to load sessions", await res.text());
        }
      } catch (err) {
        console.error("Network error loading sessions", err);
      }
    }
    if (isOpen) {
      fetchSessions();
      // reset local state each time the modal opens
      setFile(null);
      setUploadState("idle");
    }
  }, [isOpen]);

  // bail out after all hooks so hook order stays stable
  if (!isOpen) return null;

  // ------------------------------------------------------------------------
  // Handlers
  // ------------------------------------------------------------------------
  function handleFilePick(e: ChangeEvent<HTMLInputElement>) {
    const chosen = e.target.files?.[0];
    if (chosen) setFile(chosen);
  }

  async function handleConfirm() {
    if (!selectedDataSet || !file) return;
    setUploadState("uploading");

    const fd = new FormData();
    fd.append("session_id", selectedDataSet.id);
    fd.append("file", file);

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch("http://localhost:8000/upload/csv", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });
      if (!res.ok) throw new Error(await res.text());
      setUploadState("done");
      setTimeout(onClose, 1000);
    } catch (err) {
      console.error(err);
      setUploadState("error");
    }
  }

  const confirmDisabled =
    !selectedDataSet || !file || uploadState === "uploading";

  // ------------------------------------------------------------------------
  // JSX
  // ------------------------------------------------------------------------
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold flex items-center text-gray-900">
            <Database className="h-5 w-5 mr-2" />
            Select Data Set &amp; Upload CSV
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
                onClick={() => onSelectDataSet(ds)}
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                  selectedDataSet?.id === ds.id
                    ? "border-primary-500 bg-primary-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h3 className="font-medium text-gray-900">{ds.name}</h3>
                      {selectedDataSet?.id === ds.id && (
                        <Check className="h-5 w-5 text-primary-600 ml-2" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {ds.description}
                    </p>
                    <div className="flex items-center mt-2 text-xs text-gray-500">
                      <span>Size: {ds.size}</span>
                      <span className="mx-2">•</span>
                      <span>Updated: {ds.lastUpdated}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

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
            {uploadState === "idle" && "Confirm Upload"}
            {uploadState === "uploading" && (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin inline" />
                Uploading…
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
