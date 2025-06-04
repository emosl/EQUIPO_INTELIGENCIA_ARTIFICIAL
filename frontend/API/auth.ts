// API/auth.ts

export interface LoginPayload {
    email: string
    password: string
  }
  
  export interface TokenResponse {
    access_token: string
    token_type: string
  }
  
  /**
   * Envía las credenciales al endpoint POST /login y devuelve el token.
   */
  export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
    const response = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
  
    if (!response.ok) {
      // Extraemos el mensaje de error que haya devuelto FastAPI
      const error = await response.json()
      throw new Error(error.detail || "Login Failed")
    }
  
    return response.json()
  }
  