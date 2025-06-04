// src/API/result.ts

// ─────────────────────────────────────────────────────────────────────────────
// These two environment variables should point to port 8000 and 8001 respectively.
// Make sure you have in your .env.local:
//   NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
//   NEXT_PUBLIC_RESULT_BASE_URL=http://localhost:8001
// ─────────────────────────────────────────────────────────────────────────────
const BACKEND_BASE = process.env.NEXT_PUBLIC_BACKEND_BASE_URL!; // e.g. "http://localhost:8000"
const RESULT_BASE = process.env.NEXT_PUBLIC_RESULT_BASE_URL!; // e.g. "http://localhost:8001"

// ─────────────────────────────────────────────────────────────────────────────
// (1) “SessionSummary” shape matches what GET /sessions returns on port 8000
// ─────────────────────────────────────────────────────────────────────────────
export interface SessionSummary {
  id: string;
  name: string;
  description: string;
  size: string;
  lastUpdated: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// 1️⃣  Fetch all sessions *for the currently authenticated user*.
//     The back-end route is GET http://localhost:8000/sessions.
//     We simply read the JWT from localStorage and send it in the header.
// ─────────────────────────────────────────────────────────────────────────────
export async function getSessionsForPatient(): Promise<SessionSummary[]> {
  // 1) Read the token that AuthContext already stored in localStorage
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  // 2) If no token, bail early (the backend will also reject, but we can guard here)
  if (!token) {
    throw new Error("No access token found.  You must be logged in.");
  }

  const res = await fetch(`${BACKEND_BASE}/sessions`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error(`Failed to load sessions (status ${res.status})`);
  }

  return (await res.json()) as SessionSummary[];
}

// ─────────────────────────────────────────────────────────────────────────────
// 2️⃣  Build “download CSV” URLs on the Kalman results server (port 8001)
// ─────────────────────────────────────────────────────────────────────────────
export function getResultsCSVUrl(
  sessionId: number,
  kind: "y" | "amp" | "welch"
): string {
  // Example: http://localhost:8001/sessions/42/results/csv?type=y
  return `${RESULT_BASE}/sessions/${sessionId}/results/csv?type=${kind}`;
}

// ─────────────────────────────────────────────────────────────────────────────
// 3️⃣  Fetch raw amplitude arrays from RESULTS server (no auth‐header needed here)
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
  const res = await fetch(
    `${RESULT_BASE}/sessions/${sessionId}/results/amplitude`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    }
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch amplitude arrays (status ${res.status})`);
  }
  return (await res.json()) as AmplitudeResponse;
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
  const res = await fetch(
    `${RESULT_BASE}/sessions/${sessionId}/results/welch`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    }
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch Welch arrays (status ${res.status})`);
  }
  return (await res.json()) as WelchResponse;
}

// ─────────────────────────────────────────────────────────────────────────────
// 5️⃣  Build “plot” URLs on RESULTS server
// ─────────────────────────────────────────────────────────────────────────────
export function getAmplitudePlotUrl(sessionId: number): string {
  // e.g.  http://localhost:8001/sessions/42/plot/amplitude.png
  return `${RESULT_BASE}/sessions/${sessionId}/plot/amplitude.png`;
}

export function getWelchPlotUrl(sessionId: number): string {
  // e.g.  http://localhost:8001/sessions/42/plot/welch.png
  return `${RESULT_BASE}/sessions/${sessionId}/plot/welch.png`;
}
