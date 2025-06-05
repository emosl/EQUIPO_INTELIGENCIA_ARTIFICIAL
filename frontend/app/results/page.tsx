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
import PatientSelectionModal from "@/components/PatientSelectionModal";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Brain,
  Database,
  Clock,
  BarChart3,
  Download,
  CheckCircle,
  Calendar,
  HardDrive,
} from "lucide-react";

// ─────────────────────────────────────────────────────────────────────────────
// Simple Spinner stub—replace or import your own if you have one.
// ─────────────────────────────────────────────────────────────────────────────
function Spinner() {
  return (
    <div className="flex justify-center">
      <div className="h-8 w-8 border-4 border-blue-300 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// (We won't actually fetch "detail" from GET /sessions/{id}, since it doesn't exist.)
// So we keep a placeholder type here.
// ─────────────────────────────────────────────────────────────────────────────
interface SessionDetail {
  algorithm_name: string;
  processing_time: number;
  session_timestamp: string;
  name: string; // e.g. "Session 123"
}

export default function ResultsPage() {
  const { selectedPatient } = usePatient();
  const [showPatientModal, setShowPatientModal] = useState(false);

  // ────────────────────────────────────────────────────────────────────────────
  // State: all sessions for this user
  // ────────────────────────────────────────────────────────────────────────────
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [errorSessions, setErrorSessions] = useState<string | null>(null);

  // ────────────────────────────────────────────────────────────────────────────
  // State: which session is "expanded" / selected
  // ────────────────────────────────────────────────────────────────────────────
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);

  // ────────────────────────────────────────────────────────────────────────────
  // State: raw amplitude + welch arrays for the expanded session
  // ────────────────────────────────────────────────────────────────────────────
  const [amplitudeData, setAmplitudeData] = useState<AmplitudeResponse | null>(
    null
  );
  const [welchData, setWelchData] = useState<WelchResponse | null>(null);
  const [loadingData, setLoadingData] = useState(false);
  const [errorData, setErrorData] = useState<string | null>(null);

  // ────────────────────────────────────────────────────────────────────────────
  // State: session‐detail placeholder (algorithm_name, processing_time, timestamp)
  // ────────────────────────────────────────────────────────────────────────────
  const [activeSessionDetail, setActiveSessionDetail] = useState<SessionDetail>(
    {
      algorithm_name: "N/A",
      processing_time: 0,
      session_timestamp: "",
      name: "N/A",
    }
  );

  // ────────────────────────────────────────────────────────────────────────────
  // (1️⃣) Fetch all sessions for the user whenever the selected patient changes.
  //       Then filter to keep only those sessions that have amplitude data on port 8001.
  // ────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!selectedPatient?.id) return;

    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    if (!token) return;

    getSessionsForPatient()
      .then(async (allSessions) => {
        // filter out those without amplitude data, as before…
        const checks = await Promise.all(
          allSessions.map(async (sess) => {
            try {
              const ampResp = await fetchAmplitudeArrays(Number(sess.id));
              return { sess, hasResults: ampResp.All.length > 0 };
            } catch {
              return { sess, hasResults: false };
            }
          })
        );
        const filtered = checks.filter((c) => c.hasResults).map((c) => c.sess);
        setSessions(filtered);
      })
      .catch((err) => {
        console.error("Session loading error:", err);
        setErrorSessions("Failed to load sessions");
      });
  }, [selectedPatient]);

  // ────────────────────────────────────────────────────────────────────────────
  // (2) Whenever activeSessionId changes, fetch amplitude + welch arrays…
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
      .then(([amps, welch]) => {
        setAmplitudeData(amps);
        setWelchData(welch);
        setLoadingData(false);
      })
      .catch((err) => {
        console.error("Data loading error:", err);
        setErrorData("Failed to load result arrays");
        setLoadingData(false);
      });
  }, [activeSessionId]);

  // ────────────────────────────────────────────────────────────────────────────
  // (3) Populate activeSessionDetail from the sessions array
  // ────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (activeSessionId === null) {
      setActiveSessionDetail({
        algorithm_name: "N/A",
        processing_time: 0,
        session_timestamp: "",
        name: "N/A",
      });
      return;
    }

    // Find the matching SessionSummary in sessions by ID:
    const found = sessions.find((s) => Number(s.id) === activeSessionId);
    if (found) {
      setActiveSessionDetail({
        algorithm_name: found.algorithm_name || "N/A",
        processing_time: found.processing_time || 0,
        session_timestamp: found.lastUpdated, // we'll treat lastUpdated as timestamp
        name: found.name,
      });
    } else {
      // fallback to placeholders
      setActiveSessionDetail({
        algorithm_name: "N/A",
        processing_time: 0,
        session_timestamp: "",
        name: "N/A",
      });
    }
  }, [activeSessionId, sessions]);

  return (
    <>
      {!selectedPatient ? (
        <div className="py-16 text-center content-wrapper">
          <p className="text-gray-600 mb-4">
            No patient selected. Please choose a patient to view their results.
          </p>
        </div>
      ) : (

        <div className="px-6 py-8">
          {/* ─────────────────────────────────────────────────────────── */}
          {/* TITLE & "Change Patient" BUTTON                            */}
          {/* ─────────────────────────────────────────────────────────── */}

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

          {/* ─────────────────────────────────────────────────────────── */}
          {/* LOADING / ERROR while fetching "all sessions"              */}
          {/* ─────────────────────────────────────────────────────────── */}
          {loadingSessions && (
            <div className="card shadow-lg">
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Spinner />
                  <p className="mt-4 text-lg text-gray-600">
                    Loading session data...
                  </p>
                </div>
              </div>
            </div>
          )}
          {errorSessions && (
            <div className="card shadow-lg bg-red-50 border-red-200">
              <div className="flex items-start p-4">
                <div>
                  <h4 className="text-lg font-semibold text-red-800 mb-2">
                    Error Loading Data
                  </h4>
                  <p className="text-red-700">{errorSessions}</p>
                </div>
              </div>
            </div>
          )}

          {/* ─────────────────────────────────────────────────────────── */}
          {/* PATIENT INFO CARD                                         */}
          {/* ─────────────────────────────────────────────────────────── */}
          <div className="card mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
            <div className="flex items-center p-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                {/* You could place an avatar or icon here */}
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {selectedPatient.name}
                </h2>
                <p className="text-sm text-gray-500">
                  Last visit: {selectedPatient.lastVisit || "N/A"}
                </p>
              </div>
            </div>
          </div>

          {/* ─────────────────────────────────────────────────────────── */}
          {/* SESSION DETAILS (when a session is selected)               */}
          {/* ─────────────────────────────────────────────────────────── */}
          {activeSessionId && (
            <div className="mb-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Session {activeSessionId} Analysis
              </h3>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-4">
                {/* ─────────────────────────────────────────────────────── */}
                {/* Left: Plots (span 2 columns on lg)                    */}
                {/* ─────────────────────────────────────────────────────── */}
                <div className="lg:col-span-2 overflow-y-auto p-4 space-y-4">
                  <div>
                    <img
                      src={`http://localhost:8001/sessions/${activeSessionId}/plot/amplitude_orig_vs_all.png`}
                      alt={`Original vs All plot for session ${activeSessionId}`}
                      className="w-full h-auto border rounded-md"
                    />
                  </div>
                  {welchData && (
                    <div>
                      <img
                        src={`http://localhost:8001/sessions/${activeSessionId}/plot/welch.png`}
                        alt={`Welch PSD plot for session ${activeSessionId}`}
                        className="w-full h-auto border rounded-md"
                      />
                    </div>
                  )}
                </div>

                {/* ─────────────────────────────────────────────────────── */}
                {/* Right: Info Cards (span 1 column on lg)               */}
                {/* ─────────────────────────────────────────────────────── */}
                <div className="lg:col-span-1 space-y-4 p-4 sticky top-16">
                  {/* ─────────────────────────────────────────────── */}
                  {/* Model Used Card (border‐purple)                 */}
                  {/* ─────────────────────────────────────────────── */}
                  <Card className="border-l-4 border-l-purple-500 mb-2 py-3">
                    <CardHeader className="py-1">
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Brain className="h-5 w-5 text-purple-600" />
                        Model Used
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 py-1">
                      <p className="font-semibold text-gray-900 text-sm">
                        {activeSessionDetail.algorithm_name}
                      </p>
                    </CardContent>
                  </Card>

                  {/* ─────────────────────────────────────────────── */}
                  {/* Dataset Used Card (border‐blue)                */}
                  {/* ─────────────────────────────────────────────── */}
                  <Card className="border-l-4 border-l-blue-500 mb-2 py-3">
                    <CardHeader className="py-1">
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Database className="h-5 w-5 text-blue-600" />
                        Dataset Used
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 py-1">
                      <p className="font-semibold text-gray-900 text-sm">
                        {activeSessionDetail.name}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-gray-600">
                        <div className="flex items-center gap-1">
                          <HardDrive className="h-4 w-4" />
                          <span>2.3 GB</span>
                        </div>
                        <div className="flex gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>
                            {activeSessionDetail.session_timestamp
                              ? new Date(
                                  activeSessionDetail.session_timestamp
                                ).toLocaleDateString()
                              : "N/A"}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* ─────────────────────────────────────────────── */}
                  {/* Processing Info Card (border‐green)             */}
                  {/* ─────────────────────────────────────────────── */}
                  <Card className="border-l-4 border-l-green-500 mb-2 py-3">
                    <CardHeader className="py-1">
                      <CardTitle className="flex gap-2 text-base">
                        <Clock className="h-5 w-5 text-green-600" />
                        Processing Info
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-1 py-1 text-center text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Processing Time:</span>
                        <span className="font-semibold">
                          {activeSessionDetail.processing_time.toFixed(2)} s
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-600">
                        <span>Processed:</span>
                        <span className="text-gray-900">
                          {activeSessionDetail.session_timestamp
                            ? new Date(
                                activeSessionDetail.session_timestamp
                              ).toLocaleString()
                            : "N/A"}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="mb-2">
                    <CardHeader className="py-1">
                      <CardTitle className="flex  gap-2 text-base">
                        <Download className="h-5 w-5 text-gray-600" />
                        Export Data
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="py-1">
                      <div className="flex gap-2 text-xs text-center">
                        <Button
                          asChild
                          variant="outline"
                          className="justify-center border-green-200 hover:bg-green-50 py-1 text-sm flex-1"
                        >
                          <a
                            href={getResultsCSVUrl(activeSessionId, "y")}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-center gap-1"
                          >
                            <Download className="h-4 w-4" />
                            Results Y
                          </a>
                        </Button>

                        <Button
                          asChild
                          variant="outline"
                          className="justify-center border-blue-200 hover:bg-blue-50 py-1 text-sm"
                        >
                          <a
                            href={getResultsCSVUrl(activeSessionId, "amp")}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-center gap-1 flex-1"
                          >
                            <Download className="h-4 w-4" />
                            Amplitude
                          </a>
                        </Button>

                        <Button
                          asChild
                          variant="outline"
                          className="justify-center border-purple-200 hover:bg-purple-50 py-1 text-sm"
                        >
                          <a
                            href={getResultsCSVUrl(activeSessionId, "welch")}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-center gap-1 flex-1"
                          >
                            <Download className="h-4 w-4" />
                            Welch
                          </a>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* ─────────────────────────────────────────────── */}
              {/* Data Tables (first 10 rows of amplitude + welch) */}
              {/* ─────────────────────────────────────────────── */}
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
                  <h3 className="font-semibold mb-2">
                    Welch PSD Data (first 10 frequencies)
                  </h3>
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

          {/* ─────────────────────────────────────────────────────────── */}
          {/* SESSIONS GRID (below the details)                         */}
          {/* ─────────────────────────────────────────────────────────── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {sessions.map((sess) => (
              <Card
                key={sess.id}
                className={`cursor-pointer border ${
                  activeSessionId === Number(sess.id)
                    ? "border-blue-500"
                    : "border-gray-200"
                }`}
                onClick={() => setActiveSessionId(Number(sess.id))}
              >
                <div className="flex items-center justify-between p-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Session: {sess.name}
                    </p>
                    <p className="text-sm text-gray-500">{sess.description}</p>
                  </div>
                  <div className="p-3 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="h-6 w-6 text-blue-600 font-bold">S</span>
                  </div>
                </div>
                <div className="mt-4 px-4 pb-4 space-y-1">
                  <p className="text-sm text-gray-600">
                    Size: <span className="font-semibold">{sess.size}</span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Last Updated:{" "}
                    <span className="font-medium">{sess.lastUpdated}</span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Algorithm:{" "}
                    <span className="font-medium">
                      {sess.algorithm_name || "N/A"}
                    </span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Processing Time:{" "}
                    <span className="font-medium">
                      {sess.processing_time.toFixed(2)} s
                    </span>
                  </p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────────────── */}
      {/* PATIENT SELECTION MODAL                                            */}
      {/* ───────────────────────────────────────────────────────────────────── */}
      <PatientSelectionModal
        isOpen={showPatientModal}
        onClose={() => setShowPatientModal(false)}
      />
    </>
  );
}
