// src/API/result.ts

// ─────────────────────────────────────────────────────────────────────────────
// Environment variable validation with helpful error messages
// ─────────────────────────────────────────────────────────────────────────────
const BACKEND_BASE = process.env.NEXT_PUBLIC_BACKEND_URL!;
const RESULT_BASE = process.env.NEXT_PUBLIC_KALMAN_URL!;

// Validate environment variables are set
if (!BACKEND_BASE) {
  throw new Error(
    "NEXT_PUBLIC_BACKEND_BASE_URL is not set. Please add it to your .env.local file "
  );
}

if (!RESULT_BASE) {
  throw new Error(
    "NEXT_PUBLIC_RESULT_BASE_URL is not set. Please add it to your .env.local file"
  );
}

console.log("API Configuration:", { BACKEND_BASE, RESULT_BASE });

// ─────────────────────────────────────────────────────────────────────────────
// (1) "SessionSummary" shape matches what GET /sessions returns on port 8000.
//     We have added "algorithm_name" and "processing_time" on the backend.
// ─────────────────────────────────────────────────────────────────────────────
export interface SessionSummary {
  id: string;
  name: string;
  description: string;
  size: string;
  lastUpdated: string;

  // ─────────── NEW ───────────
  algorithm_name: string; // e.g. "Carlson_GramSchmidt"
  processing_time: number; // e.g. 59.3813 (seconds)
}

// ─────────────────────────────────────────────────────────────────────────────
// 1️⃣  Fetch all sessions for the current authenticated user.
//     We read the JWT from localStorage and send it in the Authorization header.
// ─────────────────────────────────────────────────────────────────────────────
export async function getSessionsForPatient(
  patientId: number
): Promise<SessionSummary[]> {
  // 1) Read the token that AuthContext stored in localStorage
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  if (!token) {
    throw new Error("No access token found. You must be logged in.");
  }

  console.log("Fetching sessions for patient:", patientId);

  try {
    const res = await fetch(`${BACKEND_BASE}/patients/${patientId}/sessions`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(
        `Failed to load sessions (status ${res.status}): ${errorText}`
      );
    }

    return (await res.json()) as SessionSummary[];
  } catch (error) {
    if (
      error instanceof TypeError &&
      error.message.includes("Failed to fetch")
    ) {
      throw new Error(
        `Cannot connect to backend server at ${BACKEND_BASE}. Please ensure the backend is running on port 8000.`
      );
    }
    throw error;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 2️⃣  Build "download CSV" URLs on the RESULTS server (port 8001)
// ─────────────────────────────────────────────────────────────────────────────
export function getResultsCSVUrl(
  sessionId: number,
  kind: "y" | "amp" | "welch"
): string {
  return `${RESULT_BASE}/sessions/${sessionId}/results/csv?type=${kind}`;
}

// ─────────────────────────────────────────────────────────────────────────────
// 3️⃣  Fetch raw amplitude arrays from RESULTS server
// ─────────────────────────────────────────────────────────────────────────────
export interface AmplitudeResponse {
  All: number[];
  Original: number[];
  WC: number[];
  NWC: number[];
}
export async function fetchAmplitudeArrays(
  sessionId: number
): Promise<AmplitudeResponse> {
  try {
    const res = await fetch(
      `${RESULT_BASE}/sessions/${sessionId}/results/amplitude`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(
        `Failed to fetch amplitude arrays (status ${res.status}): ${errorText}`
      );
    }
    return (await res.json()) as AmplitudeResponse;
  } catch (error) {
    if (
      error instanceof TypeError &&
      error.message.includes("Failed to fetch")
    ) {
      throw new Error(
        `Cannot connect to results server at ${RESULT_BASE}. Please ensure the results server is running on port 8001.`
      );
    }
    throw error;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 4️⃣  Fetch raw Welch arrays from RESULTS server
// ─────────────────────────────────────────────────────────────────────────────
export interface WelchResponse {
  frequencies: number[];
  power: {
    All: number[];
    Original: number[];
    WC: number[];
    NWC: number[];
  };
}
export async function fetchWelchArrays(
  sessionId: number
): Promise<WelchResponse> {
  try {
    const res = await fetch(
      `${RESULT_BASE}/sessions/${sessionId}/results/welch`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(
        `Failed to fetch Welch arrays (status ${res.status}): ${errorText}`
      );
    }
    return (await res.json()) as WelchResponse;
  } catch (error) {
    if (
      error instanceof TypeError &&
      error.message.includes("Failed to fetch")
    ) {
      throw new Error(
        `Cannot connect to results server at ${RESULT_BASE}. Please ensure the results server is running on port 8001.`
      );
    }
    throw error;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 5️⃣  Build "plot" URLs on RESULTS server (port 8001)
// ─────────────────────────────────────────────────────────────────────────────
export function getAmplitudePlotUrl(sessionId: number): string {
  return `${RESULT_BASE}/sessions/${sessionId}/plot/amplitude.png`;
}
export function getWelchPlotUrl(sessionId: number): string {
  return `${RESULT_BASE}/sessions/${sessionId}/plot/welch.png`;
}
