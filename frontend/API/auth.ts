// API/auth.ts

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

/**
 * Envía las credenciales al endpoint POST /login y devuelve el token.
 */
export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  // Build a URLSearchParams instance:
  const formBody = new URLSearchParams();
  formBody.append("username", payload.email);
  formBody.append("password", payload.password);

  const response = await fetch("http://localhost:8000/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formBody.toString(),
  });

  if (!response.ok) {
    // If FastAPI returned a JSON error, extract the 'detail' field
    const errorJson = await response.json().catch(() => ({}));
    throw new Error(errorJson.detail || "Login failed");
  }
  return response.json();
}
