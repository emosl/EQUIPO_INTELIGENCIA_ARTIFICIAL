"use client";

import { useState, useEffect } from "react";
import { X, Brain, Check } from "lucide-react";

export interface Model {
  id: string;
  name: string;
  description: string;
  accuracy?: string;
  type: string;
}

interface ModelSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedModels: Model[];
  onSelectModels: (models: Model[]) => void;
}

// -----------------------------------------------------------------------------
//  Kalman-filter variants available in the backend
// -----------------------------------------------------------------------------
const availableModels: Model[] = [
  {
    id: "1",
    name: "Potter_GramSchmidt",
    description: "Potter with Gram-Schmidt orthogonalization",
    type: "Square-root filter",
  },
  {
    id: "2",
    name: "Carlson_GramSchmidt",
    description: "Carlson with Gram-Schmidt orthogonalization",
    type: "Square-root filter",
  },
  {
    id: "3",
    name: "Bierman_GramSchmidt",
    description: "Bierman with Gram-Schmidt orthogonalization",
    type: "Square-root filter",
  },
  {
    id: "4",
    name: "Potter_Givens",
    description: "Potter with Givens rotations",
    type: "Square-root filter",
  },
  {
    id: "5",
    name: "Carlson_Givens",
    description: "Carlson with Givens rotations",
    type: "Square-root filter",
  },
  {
    id: "6",
    name: "Bierman_Givens",
    description: "Bierman with Givens rotations",
    type: "Square-root filter",
  },
  {
    id: "7",
    name: "Potter_Householder",
    description: "Potter with Householder reflections",
    type: "Square-root filter",
  },
  {
    id: "8",
    name: "Carlson_Householder",
    description: "Carlson with Householder reflections",
    type: "Square-root filter",
  },
  {
    id: "9",
    name: "Bierman_Householder",
    description: "Bierman with Householder reflections",
    type: "Square-root filter",
  },
];

export default function ModelSelectionModal({
  isOpen,
  onClose,
  selectedModels,
  onSelectModels,
}: ModelSelectionModalProps) {
  // Initialize temp state with current selection when modal opens
  const [tempSelected, setTempSelected] = useState<Model[]>(selectedModels);

  // Update temp state when selectedModels prop changes or modal opens
  useEffect(() => {
    if (isOpen) {
      setTempSelected(selectedModels);
    }
  }, [isOpen, selectedModels]);

  const toggle = (m: Model) => {
    setTempSelected((prev) =>
      prev.some((x) => x.id === m.id)
        ? prev.filter((x) => x.id !== m.id)
        : [...prev, m]
    );
  };

  const confirm = () => {
    onSelectModels(tempSelected);
    onClose();
  };

  const cancel = () => {
    setTempSelected(selectedModels); // Reset to original selection
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[80vh] overflow-hidden">
        {/* header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold flex items-center text-gray-900">
            <Brain className="h-5 w-5 mr-2" /> Choose Kalman Filter Variant(s)
          </h2>
          <button
            onClick={cancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* body */}
        <div className="p-6 space-y-4 overflow-y-auto max-h-[55vh]">
          <p className="text-sm text-gray-600">
            You can run multiple square-root Kalman variants in parallel to
            compare numerical stability and performance.
          </p>

          <div className="grid gap-3">
            {availableModels.map((m) => {
              const selected = tempSelected.some((x) => x.id === m.id);
              return (
                <div
                  key={m.id}
                  onClick={() => toggle(m)}
                  className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                    selected
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h3 className="font-medium text-gray-900">{m.name}</h3>
                        {selected && (
                          <Check className="h-5 w-5 text-primary-600 ml-2" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {m.description}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{m.type}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {tempSelected.length > 0 && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>
                  {tempSelected.length} model
                  {tempSelected.length !== 1 ? "s" : ""} selected:
                </strong>
              </p>
              <p className="text-sm text-blue-700 mt-1">
                {tempSelected.map((m) => m.name).join(", ")}
              </p>
            </div>
          )}

          {tempSelected.length === 0 && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">
                Please select at least one Kalman filter variant to proceed.
              </p>
            </div>
          )}
        </div>

        {/* footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={cancel}
            className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={confirm}
            disabled={tempSelected.length === 0}
            className="px-4 py-2 text-sm text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Confirm ({tempSelected.length})
          </button>
        </div>
      </div>
    </div>
  );
}
