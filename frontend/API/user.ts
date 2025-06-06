// api/user.ts

//  🎯 This file is solely responsible for “user + patient” CRUD,
//      so it always points at port 8000 (your main FastAPI server).

const USER_API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL;

export interface CreateUser {
  name: string;
  father_surname: string;
  mother_surname: string;
  medical_department: string;
  email: string;
  password: string;
}

/**
 * Create a new user (POST /users/).
 */
export async function createUser(payload: CreateUser) {
  const response = await fetch(`${USER_API_BASE}/users/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    // Attempt to parse JSON error message from backend
    const errorJson = await response.json().catch(() => ({} as any));
    throw new Error(errorJson.detail || "Failed to create user");
  }

  return response.json();
}

/**
 * Example: Fetch all patients for a given user (GET /users/{user_id}/patients).
 * Returns an array of Patient objects (shape defined in your backend's schemas).
 */
export interface PatientSummary {
  id: number;
  name: string;
  father_surname: string;
  mother_surname: string;
  birth_date: string; // e.g. "1985-02-10"
  sex: string; // "M" or "F"
  email: string;
}

export async function getPatientsForUser(
  userToken: string,
  userId: number
): Promise<PatientSummary[]> {
  const res = await fetch(`${USER_API_BASE}/users/${userId}/patients`, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${userToken}`,
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to load patients (status ${res.status})`);
  }
  return (await res.json()) as PatientSummary[];
}

/**
 * Example: Create a new patient for a given user (POST /users/{user_id}/patients).
 */
export interface CreatePatient {
  name: string;
  father_surname: string;
  mother_surname: string;
  birth_date: string;
  sex: string;
  email: string;
}

export async function createPatientForUser(
  userToken: string,
  userId: number,
  payload: CreatePatient
): Promise<PatientSummary> {
  const response = await fetch(`${USER_API_BASE}/users/${userId}/patients`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${userToken}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errJson = await response.json().catch(() => ({} as any));
    throw new Error(errJson.detail || "Failed to create patient");
  }

  return response.json() as Promise<PatientSummary>;
}

/**
 * If you have a “login” endpoint that returns a JWT token,
 * you can add a helper here, for example:
 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function loginUser(
  email: string,
  password: string
): Promise<TokenResponse> {
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const response = await fetch(`${USER_API_BASE}/loginApi`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  if (!response.ok) {
    const errJson = await response.json().catch(() => ({} as any));
    throw new Error(errJson.detail || "Login failed");
  }

  return response.json();
}
