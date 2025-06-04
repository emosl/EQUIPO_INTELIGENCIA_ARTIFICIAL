// API/auth.ts

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  // Build a URL‐encoded form (FastAPI’s OAuth2PasswordRequestForm expects "username" + "password")
  const form = new URLSearchParams();
  form.append("username", payload.email); // notice we call it "username"
  form.append("password", payload.password);

  const response = await fetch("http://localhost:8000/login", {
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
  return response.json(); // { access_token, token_type }
}
