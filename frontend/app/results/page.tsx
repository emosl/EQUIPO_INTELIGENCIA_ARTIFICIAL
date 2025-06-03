"use client"

import { useState } from "react"
import { TrendingUp, Activity, Users, User, AlertCircle, Filter, Clock, Database, Brain, X } from "lucide-react"
import { usePatient } from "../../components/PatientContext"
import PatientSelectionModal from "../../components/PatientSelectionModal"

// Chart components
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

export default function ResultsPage() {
  const { selectedPatient } = usePatient()
  const [showPatientModal, setShowPatientModal] = useState(false)
  const [showFiltersModal, setShowFiltersModal] = useState(false)
  const [dateRange, setDateRange] = useState({ from: "2024-01-01", to: "2024-01-31" })
  const [searchTerm, setSearchTerm] = useState("")

  // Patient-specific metrics (would normally come from API)
  const getPatientMetrics = (patient) => {
    if (!patient) return []

    // Simulate different metrics based on patient
    const baseMetrics = [
      {
        name: "Risk Score",
        value: patient.id === "1" ? "7.2" : patient.id === "2" ? "4.1" : "8.9",
        change: patient.id === "1" ? "-0.3" : patient.id === "2" ? "+0.1" : "-1.2",
        changeType: patient.id === "1" ? "positive" : patient.id === "2" ? "negative" : "positive",
        icon: AlertCircle,
        unit: "/10",
      },
      {
        name: "Biomarker Level",
        value: patient.id === "1" ? "142" : patient.id === "2" ? "98" : "156",
        change: patient.id === "1" ? "+5%" : patient.id === "2" ? "-2%" : "+8%",
        changeType: patient.id === "1" ? "negative" : patient.id === "2" ? "positive" : "negative",
        icon: Activity,
        unit: "mg/dL",
      },
      {
        name: "Treatment Response",
        value: patient.id === "1" ? "78%" : patient.id === "2" ? "92%" : "65%",
        change: patient.id === "1" ? "+12%" : patient.id === "2" ? "+3%" : "+18%",
        changeType: "positive",
        icon: TrendingUp,
        unit: "",
      },
      {
        name: "Compliance Score",
        value: patient.id === "1" ? "85%" : patient.id === "2" ? "96%" : "72%",
        change: patient.id === "1" ? "+2%" : patient.id === "2" ? "-1%" : "+5%",
        changeType: patient.id === "1" ? "positive" : patient.id === "2" ? "negative" : "positive",
        icon: Users,
        unit: "",
      },
    ]
    return baseMetrics
  }

  // Generate patient-specific chart data
  const getPatientChartData = (patient) => {
    if (!patient) return []

    // Generate different data based on patient ID
    const baseData = [
      { date: "Jan 1", riskScore: 8.1, biomarker: 130 },
      { date: "Jan 5", riskScore: 7.9, biomarker: 135 },
      { date: "Jan 10", riskScore: 7.7, biomarker: 138 },
      { date: "Jan 15", riskScore: 7.5, biomarker: 140 },
      { date: "Jan 20", riskScore: 7.3, biomarker: 141 },
      { date: "Jan 25", riskScore: 7.2, biomarker: 142 },
    ]

    // Modify data based on patient
    if (patient.id === "2") {
      return baseData.map((item) => ({
        ...item,
        riskScore: item.riskScore - 3.5,
        biomarker: item.biomarker - 35,
      }))
    } else if (patient.id === "3") {
      return baseData.map((item) => ({
        ...item,
        riskScore: item.riskScore + 1.2,
        biomarker: item.biomarker + 15,
      }))
    }

    return baseData
  }

  // Generate patient-specific historical data
  const getPatientHistoricData = (patient) => {
    if (!patient) return []

    const baseData = [
      { date: "2024-01-25", metric: "Risk Score", value: "7.2", change: "-0.1" },
      { date: "2024-01-20", metric: "Risk Score", value: "7.3", change: "-0.2" },
      { date: "2024-01-15", metric: "Risk Score", value: "7.5", change: "-0.2" },
      { date: "2024-01-10", metric: "Risk Score", value: "7.7", change: "-0.2" },
      { date: "2024-01-05", metric: "Risk Score", value: "7.9", change: "-0.2" },
      { date: "2024-01-01", metric: "Risk Score", value: "8.1", change: "Baseline" },
      { date: "2024-01-25", metric: "Biomarker", value: "142 mg/dL", change: "+1" },
      { date: "2024-01-20", metric: "Biomarker", value: "141 mg/dL", change: "+1" },
      { date: "2024-01-15", metric: "Biomarker", value: "140 mg/dL", change: "+2" },
      { date: "2024-01-10", metric: "Biomarker", value: "138 mg/dL", change: "+3" },
      { date: "2024-01-05", metric: "Biomarker", value: "135 mg/dL", change: "+5" },
      { date: "2024-01-01", metric: "Biomarker", value: "130 mg/dL", change: "Baseline" },
      { date: "2024-01-25", metric: "Treatment Response", value: "78%", change: "+2%" },
      { date: "2024-01-15", metric: "Treatment Response", value: "76%", change: "+4%" },
      { date: "2024-01-05", metric: "Treatment Response", value: "72%", change: "+5%" },
      { date: "2024-01-01", metric: "Treatment Response", value: "67%", change: "Baseline" },
    ]

    // Modify data based on patient
    if (patient.id === "2") {
      return baseData.map((item) => {
        if (item.metric === "Risk Score") {
          return { ...item, value: (Number.parseFloat(item.value) - 3.5).toFixed(1) }
        } else if (item.metric === "Biomarker") {
          return { ...item, value: item.value.replace(/\d+/, (match) => Number.parseInt(match) - 35) }
        } else {
          return { ...item, value: item.value.replace(/\d+/, (match) => Number.parseInt(match) + 15) }
        }
      })
    } else if (patient.id === "3") {
      return baseData.map((item) => {
        if (item.metric === "Risk Score") {
          return { ...item, value: (Number.parseFloat(item.value) + 1.2).toFixed(1) }
        } else if (item.metric === "Biomarker") {
          return { ...item, value: item.value.replace(/\d+/, (match) => Number.parseInt(match) + 15) }
        } else {
          return { ...item, value: item.value.replace(/\d+/, (match) => Number.parseInt(match) - 10) }
        }
      })
    }

    return baseData
  }

  const metrics = getPatientMetrics(selectedPatient)
  const chartData = getPatientChartData(selectedPatient)
  const historicData = getPatientHistoricData(selectedPatient)

  // Filter historic data based on search and date range
  const filteredHistoricData = historicData.filter((item) => {
    const matchesSearch =
      !searchTerm ||
      item.metric.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.value.toLowerCase().includes(searchTerm.toLowerCase())

    const itemDate = new Date(item.date)
    const fromDate = new Date(dateRange.from)
    const toDate = new Date(dateRange.to)
    const inDateRange = itemDate >= fromDate && itemDate <= toDate

    return matchesSearch && inDateRange
  })

  if (!selectedPatient) {
    return (
      <div className="content-wrapper">
        <div className="text-center py-16">
          <User className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">No Patient Selected</h1>
          <p className="text-gray-600 mb-6">Please select a patient to view their results.</p>
          <button
            onClick={() => setShowPatientModal(true)}
            className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors font-medium"
          >
            Select Patient
          </button>
        </div>
        <PatientSelectionModal isOpen={showPatientModal} onClose={() => setShowPatientModal(false)} />
      </div>
    )
  }

  return (
    <div className="content-wrapper">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="page-title mb-2">Results Dashboard</h1>
          <p className="text-gray-600">Analysis results for {selectedPatient.name}</p>
        </div>
        <button
          onClick={() => setShowPatientModal(true)}
          className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <User className="h-4 w-4 mr-2" />
          Change Patient
        </button>
      </div>

      {/* Patient Info Card */}
      <div className="card mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <div className="flex items-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mr-4">
            <User className="h-8 w-8 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{selectedPatient.name}</h2>
            <p className="text-gray-600">
              Patient ID: {selectedPatient.id} • {selectedPatient.age} years old • {selectedPatient.gender}
            </p>
            <p className="text-sm text-gray-500">Last visit: {selectedPatient.lastVisit}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <div key={metric.name} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{metric.name}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {metric.value}
                    {metric.unit}
                  </p>
                </div>
                <div className="p-3 bg-primary-100 rounded-full">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              <div className="mt-4 flex items-center">
                <span
                  className={`text-sm font-medium ${
                    metric.changeType === "positive" ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {metric.change}
                </span>
                <span className="text-sm text-gray-500 ml-2">from last assessment</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Results Graph and Algorithm Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-2 card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Patient Results Trend</h3>
          <div className="h-80">
            <ChartContainer
              config={{
                riskScore: {
                  label: "Risk Score",
                  color: "hsl(var(--chart-1))",
                },
                biomarker: {
                  label: "Biomarker Level",
                  color: "hsl(var(--chart-2))",
                },
              }}
              className="h-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="riskScore"
                    stroke="var(--color-riskScore)"
                    name="Risk Score"
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="biomarker"
                    stroke="var(--color-biomarker)"
                    name="Biomarker Level (mg/dL)"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Information</h3>
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Algorithm Used</h4>
              <div className="flex items-center">
                <Brain className="h-5 w-5 text-purple-600 mr-2" />
                <p className="text-gray-900">Neural Network Classifier</p>
              </div>
              <p className="text-xs text-gray-500 mt-1">Accuracy: 94.2%</p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Secondary Model</h4>
              <div className="flex items-center">
                <Activity className="h-5 w-5 text-blue-600 mr-2" />
                <p className="text-gray-900">Random Forest Predictor</p>
              </div>
              <p className="text-xs text-gray-500 mt-1">Accuracy: 91.8%</p>
            </div>

            <div className="pt-2 border-t border-gray-100">
              <h4 className="text-sm font-medium text-gray-700 mb-1">Database Information</h4>
              <div className="flex items-center">
                <Database className="h-5 w-5 text-green-600 mr-2" />
                <p className="text-gray-900">Clinical Trial Dataset A</p>
              </div>
              <p className="text-xs text-gray-500 mt-1">Last updated: 2024-01-15</p>
            </div>

            <div className="pt-2 border-t border-gray-100">
              <h4 className="text-sm font-medium text-gray-700 mb-1">Processing Time</h4>
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-amber-600 mr-2" />
                <p className="text-gray-900">2.3 seconds</p>
              </div>
              <p className="text-xs text-gray-500 mt-1">Processed on: 2024-01-25 14:30</p>
            </div>
          </div>
        </div>
      </div>

      {/* Historical Data Section */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Historical Data</h3>
          <div className="flex space-x-3 mt-3 sm:mt-0">
            <div className="relative">
              <input
                type="text"
                placeholder="Search records..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <button
              onClick={() => setShowFiltersModal(true)}
              className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </button>
          </div>
        </div>

        {/* Date Range Filter (visible when filters modal is open) */}
        {showFiltersModal && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-medium text-gray-900">Filter by Date Range</h4>
              <button onClick={() => setShowFiltersModal(false)} className="text-gray-400 hover:text-gray-600">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
                <input
                  type="date"
                  value={dateRange.from}
                  onChange={(e) => setDateRange((prev) => ({ ...prev, from: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
                <input
                  type="date"
                  value={dateRange.to}
                  onChange={(e) => setDateRange((prev) => ({ ...prev, to: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
            <div className="flex justify-end mt-4">
              <button
                onClick={() => setDateRange({ from: "2024-01-01", to: "2024-01-31" })}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 mr-3"
              >
                Reset
              </button>
              <button
                onClick={() => setShowFiltersModal(false)}
                className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm font-medium hover:bg-primary-700"
              >
                Apply Filters
              </button>
            </div>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metric
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Change
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredHistoricData.length > 0 ? (
                filteredHistoricData.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.date}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.metric}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{row.value}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span
                        className={`${
                          row.change === "Baseline"
                            ? "text-gray-500"
                            : row.change.startsWith("+")
                              ? "text-green-600"
                              : "text-red-600"
                        }`}
                      >
                        {row.change}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                    No records found matching your criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <PatientSelectionModal isOpen={showPatientModal} onClose={() => setShowPatientModal(false)} />
    </div>
  )
}
