"use client"
import { X, Database, Check } from "lucide-react"

interface DataSet {
  id: string
  name: string
  description: string
  size: string
  lastUpdated: string
}

interface DataSetSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  selectedDataSet: DataSet | null
  onSelectDataSet: (dataSet: DataSet) => void
}

const dataSets: DataSet[] = [
  {
    id: "1",
    name: "Clinical Trial Dataset A",
    description: "Comprehensive patient data from clinical trials 2023-2024",
    size: "2.3 GB",
    lastUpdated: "2024-01-15",
  },
  {
    id: "2",
    name: "Historical Patient Records",
    description: "Patient records spanning the last 5 years",
    size: "1.8 GB",
    lastUpdated: "2024-01-10",
  },
  {
    id: "3",
    name: "Laboratory Results Dataset",
    description: "Laboratory test results and biomarkers",
    size: "950 MB",
    lastUpdated: "2024-01-12",
  },
  {
    id: "4",
    name: "Imaging Data Collection",
    description: "Medical imaging data with annotations",
    size: "4.1 GB",
    lastUpdated: "2024-01-08",
  },
]

export default function DataSetSelectionModal({
  isOpen,
  onClose,
  selectedDataSet,
  onSelectDataSet,
}: DataSetSelectionModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl mx-4 max-h-[80vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Database className="h-5 w-5 mr-2" />
            Select Data Set
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6">
          <div className="grid gap-4">
            {dataSets.map((dataSet) => (
              <div
                key={dataSet.id}
                onClick={() => onSelectDataSet(dataSet)}
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                  selectedDataSet?.id === dataSet.id
                    ? "border-primary-500 bg-primary-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h3 className="font-medium text-gray-900">{dataSet.name}</h3>
                      {selectedDataSet?.id === dataSet.id && <Check className="h-5 w-5 text-primary-600 ml-2" />}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{dataSet.description}</p>
                    <div className="flex items-center mt-2 text-xs text-gray-500">
                      <span>Size: {dataSet.size}</span>
                      <span className="mx-2">•</span>
                      <span>Updated: {dataSet.lastUpdated}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={onClose}
            disabled={!selectedDataSet}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Confirm Selection
          </button>
        </div>
      </div>
    </div>
  )
}
