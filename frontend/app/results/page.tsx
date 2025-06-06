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
    } else {
      onSessionId(null);
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
  
          {/* Your existing Results Dashboard UI */}
          <div className="px-6 py-8 content-wrapper">
            {/* ... everything else exactly as you already have it ... */}
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
