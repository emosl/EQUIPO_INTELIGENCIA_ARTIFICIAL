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
import { useRouter } from "next/router";
import { useSearchParams } from "next/navigation";
import {
  Brain,
  History,
  Database,
  Clock,
  BarChart3,
  Download,
  CheckCircle,
  Calendar,
  HardDrive,
  Activity,
} from "lucide-react";

const KALMAN_URL = process.env.NEXT_PUBLIC_KALMAN_URL;

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
function SessionIdReader({ onSessionId }: { onSessionId: (id: number | null) => void }) {
  const searchParams = useSearchParams();
  const sessionIdParam = searchParams.get("sessionId");

  useEffect(() => {
    if (sessionIdParam) {
      const parsed = parseInt(sessionIdParam, 10);
      onSessionId(isNaN(parsed) ? null : parsed);
    } 
  }, [sessionIdParam, onSessionId]);

  return null;
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
  // const searchParams = useSearchParams();
  // const sessionIdParam = searchParams.get("sessionId");

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

  // useEffect(() => {
  //   if (sessionIdParam && selectedPatient && typeof sessionIdParam === "string") {
  //     const parsed = parseInt(sessionIdParam, 10);
  //     if (!isNaN(parsed)) {
  //       setActiveSessionId(parsed);
  //     }
  //   }
  // }, [sessionIdParam, selectedPatient]);
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
    setLoadingSessions(true);
    setErrorSessions(null);

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
        setLoadingSessions(false);
      })
      .catch((err) => {
        console.error("Session loading error:", err);
        setErrorSessions("Failed to load sessions");
        setLoadingSessions(false);
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
      console.log("DEBUG: activeSessionId is null → clearing activeSessionDetail");
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
    console.log("DEBUG: found session =", found);
    if (found) {
      console.log("DEBUG: Setting activeSessionDetail from found session:", found);
      setActiveSessionDetail({
        
        algorithm_name: found.algorithm_name || "N/A",
        processing_time: found.processing_time || 0,
        session_timestamp: found.lastUpdated, // we'll treat lastUpdated as timestamp
        name: found.name,
        // console.log("finding")
      });
      
    } else {
      console.log(
      `DEBUG: SessionId ${activeSessionId} not found in sessions — will show Loading...`);
      setActiveSessionDetail({
        algorithm_name: "Loding Session",
        processing_time: 0,
        session_timestamp: "",
        name: "N/A",
      });
    }
  }, [activeSessionId, sessions]);

  return (
    <>
      {/* If no patient is selected */}
      {!selectedPatient ? (
        <div className="py-16 text-center content-wrapper">
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
      ) : (
        <>
          {/* Add SessionIdReader here to safely read searchParams */}
          <SessionIdReader onSessionId={(id) => setActiveSessionId(id)} />
  
          {/* Results Dashboard UI */}
          <div className="px-6 py-8 content-wrapper">
            {/* TITLE & Change Patient button */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
              <div>
                <h1 className="page-title mb-2">Results Dashboard</h1>
                <p className="text-gray-600">
                  Analysis results for {selectedPatient.name}
                </p>
              </div>
  
              <button
                onClick={() => setShowPatientModal(true)}
                className="flex items-center px-4 py-2 bg-blue-600 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700"
              >
                Change Patient
              </button>
            </div>
  
            {/* PATIENT INFO CARD */}
            <div className="card mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
              <div className="flex items-center p-2">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {selectedPatient.name}{" "}
                    {`${selectedPatient.father_surname || "N/A"} ${
                      selectedPatient.mother_surname || "N/A"
                    }`}
                  </h2>
                  <p className="text-sm text-gray-500">
                    Birth Date: {selectedPatient.birth_date || "N/A"}
                  </p>
                </div>
              </div>
            </div>
  
            {/* LOADING / ERROR while fetching sessions */}
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
  
            {/* SESSION DETAILS */}
            {activeSessionId ? (
              <div className="mb-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Session {activeSessionId} Analysis
                </h3>
  
                {/* You had the full grid with plots and info cards here — insert it back here */}
                {/* You can copy/paste your original Session Details JSX here — it is unchanged */}
              </div>
            ) : (
              <div className="mb-8 text-center text-gray-500">
                No session selected. Please click a session from Patient Historics.
              </div>
            )}
  
            {/* PATIENT HISTORICS GRID */}
            <div className="card mb-8 shadow-lg">
              <h3
                id="patient-historics"
                className="text-xl font-bold text-gray-900 mb-4"
              >
                Patient Historics
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8 max-h-96 overflow-y-auto">
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
                        <Activity className="h-8 w-8 text-blue-600" />
                      </div>
                    </div>
                    <div className="mt-4 px-4 pb-4 space-y-1">
                      <p className="text-sm text-gray-600">
                        Size:{" "}
                        <span className="font-semibold">{sess.size}</span>
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
          </div>
        </>
      )}
  
      {/* PATIENT SELECTION MODAL (always rendered) */}
      <PatientSelectionModal
        isOpen={showPatientModal}
        onClose={() => setShowPatientModal(false)}
      />
    </>
  );
  
}
