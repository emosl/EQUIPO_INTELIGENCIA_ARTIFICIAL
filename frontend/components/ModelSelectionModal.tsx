"use client"

import { useState } from "react"
import { X, Brain, Check } from "lucide-react"

interface Model {
  id: string
  name: string
  description: string
  accuracy: string
  type: string
}

interface ModelSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  selectedModels: Model[]
  onSelectModels: (models: Model[]) => void
}

const availableModels: Model[] = [
  {
    id: "1",
    name: "Neural Network Classifier",
    description: "Deep learning model for pattern recognition",
    accuracy: "94.2%",
    type: "Classification",
  },
  {
    id: "2",
    name: "Random Forest Predictor",
    description: "Ensemble method for robust predictions",
    accuracy: "91.8%",
    type: "Prediction",
  },
  {
    id: "3",
    name: "Support Vector Machine",
    description: "High-dimensional data classification",
    accuracy: "89.5%",
    type: "Classification",
  },
  {
    id: "4",
    name: "Gradient Boosting Model",
    description: "Advanced ensemble learning technique",
    accuracy: "92.7%",
    type: "Prediction",
  },
  {
    id: "5",
    name: "Logistic Regression",
    description: "Statistical model for binary outcomes",
    accuracy: "87.3%",
    type: "Classification",
  },
]

export default function ModelSelectionModal({
  isOpen,
  onClose,
  selectedModels,
  onSelectModels,
}: ModelSelectionModalProps) {
  const [tempSelectedModels, setTempSelectedModels] = useState<Model[]>(selectedModels)

  const toggleModel = (model: Model) => {
    setTempSelectedModels((prev) => {
      const isSelected = prev.some((m) => m.id === model.id)
      if (isSelected) {
        return prev.filter((m) => m.id !== model.id)
      } else {
        return [...prev, model]
      }
    })
  }

  const handleConfirm = () => {
    onSelectModels(tempSelectedModels)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[80vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Brain className="h-5 w-5 mr-2" />
            Select Model Combination
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6">
          <p className="text-sm text-gray-600 mb-4">
            Select one or more models to combine for analysis. Multiple models can provide more robust results.
          </p>

          <div className="grid gap-3">
            {availableModels.map((model) => {
              const isSelected = tempSelectedModels.some((m) => m.id === model.id)
              return (
                <div
                  key={model.id}
                  onClick={() => toggleModel(model)}
                  className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                    isSelected ? "border-primary-500 bg-primary-50" : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h3 className="font-medium text-gray-900">{model.name}</h3>
                        {isSelected && <Check className="h-5 w-5 text-primary-600 ml-2" />}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{model.description}</p>
                      <div className="flex items-center mt-2 text-xs text-gray-500">
                        <span className="bg-gray-100 px-2 py-1 rounded">{model.type}</span>
                        <span className="mx-2">•</span>
                        <span>Accuracy: {model.accuracy}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {tempSelectedModels.length > 0 && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>{tempSelectedModels.length} model(s) selected:</strong>{" "}
                {tempSelectedModels.map((m) => m.name).join(", ")}
              </p>
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={tempSelectedModels.length === 0}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Confirm Selection ({tempSelectedModels.length})
          </button>
        </div>
      </div>
    </div>
  )
}
