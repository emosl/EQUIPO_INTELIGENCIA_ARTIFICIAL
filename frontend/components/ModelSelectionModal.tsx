// src/components/ModelSelectionModal.tsx
"use client";

import { useEffect, useState } from "react";
import { X, Brain, Check } from "lucide-react";

export interface Model {
  id: string;
  name: string;
  description: string;
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
  // We’ll no longer maintain a “tempSelected” array,
  // because we want to exit immediately upon picking exactly one model.
  const [currentlySelected, setCurrentlySelected] = useState<Model[]>(
    selectedModels
  );

  // When the modal opens, reset our internal “currentlySelected” to whatever was passed in
  useEffect(() => {
    if (isOpen) {
      setCurrentlySelected(selectedModels);
    }
  }, [isOpen, selectedModels]);

  // Called when a user clicks on one of the availableModels
  const chooseModelAndClose = (m: Model) => {
    // Immediately set that one model as the selection
    onSelectModels([m]);
    // Then close the modal
    onClose();
  };

  // If modal isn't open, render nothing
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold flex items-center text-gray-900">
            <Brain className="h-5 w-5 mr-2" /> Choose Kalman Filter Variant
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4 overflow-y-auto max-h-[55vh]">
          <p className="text-sm text-gray-600">
            Select exactly one square‐root Kalman variant. As soon as you click
            on a model below, this dialog will close and your selection will be applied.
          </p>

          <div className="grid gap-3">
            {availableModels.map((m) => {
              // Highlight if it was already selected before opening
              const isAlreadySelected = selectedModels.some((x) => x.id === m.id);

              return (
                <div
                  key={m.id}
                  onClick={() => chooseModelAndClose(m)}
                  className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                    isAlreadySelected
                      ? "border-primary-500 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h3 className="font-medium text-gray-900">{m.name}</h3>
                        {isAlreadySelected && (
                          <Check className="h-5 w-5 text-primary-600 ml-2" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{m.description}</p>
                      <p className="text-xs text-gray-500 mt-1">{m.type}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        {/* No footer buttons—clicking an item already closes the modal */}
      </div>
    </div>
  );
}
