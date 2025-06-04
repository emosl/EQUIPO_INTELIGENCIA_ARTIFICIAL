// src/pages/results.tsx - FIXED VERSION

"use client";

import { useEffect, useState } from "react";
import {
  getSessionsForPatient,
  getResultsCSVUrl,
  getAmplitudePlotUrl,
  getWelchPlotUrl,
  fetchAmplitudeArrays,
  fetchWelchArrays,
  SessionSummary,
  AmplitudeResponse,
  WelchResponse,
} from "@/API/result";

import { usePatient } from "@/components/PatientContext";
import { Card } from "@/components/ui/card";

// If you already have a <Spinner /> somewhere in your ui library, import it.
// Otherwise, use a tiny stub here:
function Spinner() {
  return (
    <div className="flex justify-center">
      <div className="h-8 w-8 border-4 border-blue-300 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

export default function ResultsPage() {
  const { selectedPatient } = usePatient();

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
  // (1) Whenever the selectedPatient changes, fetch "/sessions" from port 8000:
  // ────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    // FIXED: Check if user is authenticated first
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;

    if (!token) {
      setErrorSessions("You must be logged in to view sessions");
      return;
    }

    // If no patient is selected, bail out early
    if (!selectedPatient?.id) {
      return;
    }

    setLoadingSessions(true);
    setErrorSessions(null);

    // The function now reads token from localStorage internally
    getSessionsForPatient()
      .then((list) => {
        setSessions(list);
        setLoadingSessions(false);
      })
      .catch((err) => {
        console.error("Session loading error:", err);

        // Better error handling
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
  // (2) Whenever a session is clicked, fetch amplitude & welch arrays
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
  // Check if user is authenticated
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

  // ────────────────────────────────────────────────────────────────────────────
  // If no patient is selected, show a prompt
  // ────────────────────────────────────────────────────────────────────────────
  if (!selectedPatient) {
    return (
      <div className="py-16 text-center">
        <p className="text-gray-600">
          No patient selected. Please go back and pick a patient first.
        </p>
      </div>
    );
  }

  return (
    <div className="px-6 py-8">
      <h1 className="text-2xl font-bold mb-4">
        Results for Patient: {selectedPatient.name}
      </h1>

      {/* show spinner / error if sessions are still loading */}
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
            Debug info: Check browser console and verify backend is running on
            port 8000
          </small>
        </div>
      )}

      {/* ──────────────────────────────────────────────────────────────────────── */}
      {/* 3️⃣  List all sessions in a responsive grid */}
      {/* ──────────────────────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {sessions.map((sess) => (
          <Card
            key={sess.id}
            className={`
              p-4 cursor-pointer border 
              ${
                activeSessionId === Number(sess.id)
                  ? "border-blue-500"
                  : "border-gray-200"
              }
            `}
            onClick={() => setActiveSessionId(Number(sess.id))}
          >
            <h2 className="text-lg font-semibold">Session #{sess.id}</h2>
            <p className="text-sm text-gray-500">{sess.description}</p>
            <p className="text-sm text-gray-600">Size: {sess.size}</p>
            <p className="text-sm text-gray-600">
              Last Updated: {sess.lastUpdated}
            </p>
          </Card>
        ))}
      </div>

      {/* Rest of the component remains the same... */}
      {activeSessionId && (
        <div className="space-y-6">
          <h2 className="text-xl font-bold mb-2">
            Details for Session #{activeSessionId}
          </h2>

          {/* 4a) CSV Download Links */}
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

          {/* 4b) Inline PNG Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border p-4">
              <h3 className="mb-2 font-semibold">Amplitude vs Time</h3>
              <img
                src={getAmplitudePlotUrl(activeSessionId)}
                alt={`Amplitude plot for session ${activeSessionId}`}
                className="w-full h-auto border"
              />
            </div>
            <div className="border p-4">
              <h3 className="mb-2 font-semibold">Welch PSD</h3>
              <img
                src={getWelchPlotUrl(activeSessionId)}
                alt={`Welch PSD plot for session ${activeSessionId}`}
                className="w-full h-auto border"
              />
            </div>
          </div>

          {/* 4c) Optionally show first 10 rows of raw arrays */}
          {loadingData && (
            <div className="my-4">
              <Spinner />
            </div>
          )}
          {errorData && <div className="text-red-600">{errorData}</div>}

          {amplitudeData && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">
                Amplitude Arrays (first 10 samples)
              </h3>
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
                  {Array.from({
                    length: Math.min(10, amplitudeData.Original.length),
                  }).map((_, idx) => (
                    <tr key={idx}>
                      <td className="border px-2 py-1">{idx}</td>
                      <td className="border px-2 py-1">
                        {amplitudeData.Original[idx].toFixed(5)}
                      </td>
                      <td className="border px-2 py-1">
                        {amplitudeData.All[idx].toFixed(5)}
                      </td>
                      <td className="border px-2 py-1">
                        {amplitudeData.WC[idx].toFixed(5)}
                      </td>
                      <td className="border px-2 py-1">
                        {amplitudeData.NWC[idx].toFixed(5)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {welchData && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Welch PSD (first 10 freqs)</h3>
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
                      <td className="border px-2 py-1">
                        {welchData.power.Original[idx].toFixed(3)}
                      </td>
                      <td className="border px-2 py-1">
                        {welchData.power.All[idx].toFixed(3)}
                      </td>
                      <td className="border px-2 py-1">
                        {welchData.power.WC[idx].toFixed(3)}
                      </td>
                      <td className="border px-2 py-1">
                        {welchData.power.NWC[idx].toFixed(3)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
