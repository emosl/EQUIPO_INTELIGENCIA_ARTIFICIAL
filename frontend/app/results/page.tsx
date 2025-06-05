// src/pages/results.tsx

"use client";

import { useEffect, useState } from "react";
import {
  getSessionsForPatient,
  getResultsCSVUrl,
  fetchAmplitudeArrays,
  fetchWelchArrays,
  SessionSummary,
  AmplitudeResponse,
  WelchResponse,
} from "@/API/result";

import { usePatient } from "@/components/PatientContext";
import { Card } from "@/components/ui/card";
import PatientSelectionModal from "../../components/PatientSelectionModal";

// Spinner stub (replace/import your own spinner if you already have one)
function Spinner() {
  return (
    <div className="flex justify-center">
      <div className="h-8 w-8 border-4 border-blue-300 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

export default function ResultsPage() {
  const { selectedPatient } = usePatient();
  const [showPatientModal, setShowPatientModal] = useState(false);

  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [errorSessions, setErrorSessions] = useState<string | null>(null);

  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [amplitudeData, setAmplitudeData] = useState<AmplitudeResponse | null>(
    null
  );
  const [welchData, setWelchData] = useState<WelchResponse | null>(null);
  const [loadingData, setLoadingData] = useState(false);
  const [errorData, setErrorData] = useState<string | null>(null);
  

  // ────────────────────────────────────────────────────────────────────────────
  // Fetch all sessions, then keep only those that have amplitude arrays present
  // ────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;

    if (!token) {
      setErrorSessions("You must be logged in to view sessions");
      return;
    }

    if (!selectedPatient?.id) {
      return;
    }

    setLoadingSessions(true);
    setErrorSessions(null);

    getSessionsForPatient()
      .then(async (allSessions) => {
        const checks = await Promise.all(
          allSessions.map(async (sess) => {
            try {
              const ampResp = await fetchAmplitudeArrays(Number(sess.id));
              const hasResults =
                Array.isArray(ampResp.All) && ampResp.All.length > 0;
              return { sess, hasResults };
            } catch {
              return { sess, hasResults: false };
            }
          })
        );

        const filtered = checks.filter((c) => c.hasResults).map((c) => c.sess);
        setSessions(filtered);
        setLoadingSessions(false);
      })
      .catch((err) => {
        console.error("Session loading error:", err);
        if (
          err.message.includes("401") ||
          err.message.includes("Unauthorized")
        ) {
          setErrorSessions("Your session has expired. Please log in again.");
        } else if (err.message.includes("404")) {
          setErrorSessions(
            "Sessions endpoint not found. Please check if the backend server is running on port 8000."
          );
        } else {
          setErrorSessions(err.message || "Failed to load sessions");
        }
        setLoadingSessions(false);
      });
  }, [selectedPatient]);

  // ────────────────────────────────────────────────────────────────────────────
  // On session click, fetch amplitude & welch arrays
  // ────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (activeSessionId === null) {
      setAmplitudeData(null);
      setWelchData(null);
      return;
    }

    setLoadingData(true);
    setErrorData(null);

    Promise.all([
      fetchAmplitudeArrays(activeSessionId),
      fetchWelchArrays(activeSessionId),
    ])
      .then(([ampResp, welchResp]) => {
        setAmplitudeData(ampResp);
        setWelchData(welchResp);
        setLoadingData(false);
      })
      .catch((err) => {
        console.error(err);
        setErrorData(err.message || "Failed to load result arrays");
        setLoadingData(false);
      });
  }, [activeSessionId]);

  // ────────────────────────────────────────────────────────────────────────────
  // Check authentication
  // ────────────────────────────────────────────────────────────────────────────
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  if (!token) {
    return (
      <div className="py-16 text-center">
        <p className="text-red-600 text-lg mb-4">
          You must be logged in to view results.
        </p>
        <p className="text-gray-600">
          Please log in first, then return to this page.
        </p>
      </div>
    );
  }

 

  return (
    <>
    {/* If no patient is selected */}
    {!selectedPatient ?(
      <div className="py-16 text-center">
          <p className="text-gray-600 mb-4">
            No patient selected. Please choose a patient to view their results.
          </p>
          <button
            onClick={() => setShowPatientModal(true)}
            className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors font-medium"
          >
            Select Patient
          </button>
        </div>
    ):(
      <div className="px-6 py-8">
        {/* TITLE */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="page-title mb-2">Results Dashboard</h1>
            <p className="text-gray-600">
              Analysis results for {selectedPatient.name}
            </p>
          </div>
          <button
            onClick={() => setShowPatientModal(true)}
            className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Change Patient
          </button>
        </div>
  
        {/* Loading and Error States */}
        {loadingSessions && (
          <div className="my-4">
            <Spinner />
          </div>
        )}
  
        {errorSessions && (
          <div className="text-red-600 mb-4 p-4 bg-red-50 border border-red-200 rounded">
            <strong>Error:</strong> {errorSessions}
            <br />
            <small className="text-red-500 mt-2 block">
              Debug info: Check browser console and verify backend is running on port 8000.
            </small>
          </div>
        )}
  
        {/* Patient Card */}
        <div className="card mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <div className="flex items-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mr-4">
              {/* Optional icon */}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{selectedPatient.name}</h2>
              <p className="text-sm text-gray-500">Last visit: {selectedPatient.lastVisit}</p>
            </div>
          </div>
        </div>
  
        {/* Sessions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {sessions.map((sess) => (
            <Card
              key={sess.id}
              className={`card cursor-pointer border ${
                activeSessionId === Number(sess.id) ? "border-blue-500" : "border-gray-200"
              }`}
              onClick={() => setActiveSessionId(Number(sess.id))}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Session {sess.id}</p>
                  <p className="text-sm text-gray-500">{sess.description}</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="h-6 w-6 text-blue-600 font-bold">S</span>
                </div>
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  Size: <span className="font-semibold">{sess.size}</span>
                </p>
                <p className="text-sm text-gray-600">
                  Last Updated: <span className="font-medium">{sess.lastUpdated}</span>
                </p>
              </div>
            </Card>
          ))}
        </div>
  
        {/* Session Details */}
        {activeSessionId && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold mb-2">
              Details for Session #{activeSessionId}
            </h2>
  
            {/* CSV Links */}
            <div className="flex flex-wrap gap-3">
              <a
                href={getResultsCSVUrl(activeSessionId, "y")}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                target="_blank"
                rel="noopener noreferrer"
              >
                Download results_y.csv
              </a>
              <a
                href={getResultsCSVUrl(activeSessionId, "amp")}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                target="_blank"
                rel="noopener noreferrer"
              >
                Download results_amplitude.csv
              </a>
              <a
                href={getResultsCSVUrl(activeSessionId, "welch")}
                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                target="_blank"
                rel="noopener noreferrer"
              >
                Download results_welch.csv
              </a>
            </div>
  
            {/* Plots */}
            <div className="border p-4">
              <h3 className="mb-2 font-semibold">Original vs All</h3>
              <img
                src={`http://localhost:8001/sessions/${activeSessionId}/plot/amplitude_orig_vs_all.png`}
                alt={`Original vs All plot for session ${activeSessionId}`}
                className="w-full h-auto border"
              />
            </div>
  
            {welchData && (
              <div className="border p-4">
                <h3 className="mb-2 font-semibold">Welch PSD Plot</h3>
                <img
                  src={`http://localhost:8001/sessions/${activeSessionId}/plot/welch.png`}
                  alt={`Welch PSD plot for session ${activeSessionId}`}
                  className="w-full h-auto border"
                />
              </div>
            )}
  
            {/* Data Tables */}
            {loadingData && <Spinner />}
            {errorData && <div className="text-red-600">{errorData}</div>}
  
            {amplitudeData && (
              <div className="mt-4">
                <h3 className="font-semibold mb-2">Amplitude Arrays (first 10 samples)</h3>
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border px-2 py-1">Index</th>
                      <th className="border px-2 py-1">Original</th>
                      <th className="border px-2 py-1">All</th>
                      <th className="border px-2 py-1">WC</th>
                      <th className="border px-2 py-1">NWC</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Array.from({ length: Math.min(10, amplitudeData.Original.length) }).map((_, idx) => (
                      <tr key={idx}>
                        <td className="border px-2 py-1">{idx}</td>
                        <td className="border px-2 py-1">{amplitudeData.Original[idx].toFixed(5)}</td>
                        <td className="border px-2 py-1">{amplitudeData.All[idx].toFixed(5)}</td>
                        <td className="border px-2 py-1">{amplitudeData.WC[idx].toFixed(5)}</td>
                        <td className="border px-2 py-1">{amplitudeData.NWC[idx].toFixed(5)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
  
            {welchData && (
              <div className="mt-4">
                <h3 className="font-semibold mb-2">Welch PSD Data (first 10 freqs)</h3>
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border px-2 py-1">Freq (Hz)</th>
                      <th className="border px-2 py-1">Power Original</th>
                      <th className="border px-2 py-1">Power All</th>
                      <th className="border px-2 py-1">Power WC</th>
                      <th className="border px-2 py-1">Power NWC</th>
                    </tr>
                  </thead>
                  <tbody>
                    {welchData.frequencies.slice(0, 10).map((f, idx) => (
                      <tr key={idx}>
                        <td className="border px-2 py-1">{f.toFixed(2)}</td>
                        <td className="border px-2 py-1">{welchData.power.Original[idx].toFixed(3)}</td>
                        <td className="border px-2 py-1">{welchData.power.All[idx].toFixed(3)}</td>
                        <td className="border px-2 py-1">{welchData.power.WC[idx].toFixed(3)}</td>
                        <td className="border px-2 py-1">{welchData.power.NWC[idx].toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>)}
  
      {/* Patient Selection Modal */}
      <PatientSelectionModal
        isOpen={showPatientModal}
        onClose={() => setShowPatientModal(false)}
      />
    </>
  );
}  