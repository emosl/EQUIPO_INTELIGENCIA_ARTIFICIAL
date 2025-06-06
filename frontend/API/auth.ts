// src/API/auth.ts

// Read the base URL from your .env (Next.js) or plain .env file.
// In Next.js, you must prefix it with NEXT_PUBLIC_ if you want it exposed to the browser.

const BACKEND_BASE = process.env.NEXT_PUBLIC_BACKEND_URL!;

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  // FastAPI’s OAuth2PasswordRequestForm expects "username" + "password"
  const form = new URLSearchParams();
  form.append("username", payload.email);
  form.append("password", payload.password);

  // Use BACKEND_BASE from env instead of hard-coding
  const response = await fetch(`${BACKEND_BASE}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form.toString(),
  });

  if (!response.ok) {
    const errorJson = await response.json().catch(() => ({}));
    throw new Error(errorJson.detail || "Login failed");
  }
  return response.json();
}
