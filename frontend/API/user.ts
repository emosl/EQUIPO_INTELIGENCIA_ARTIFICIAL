// api/user.ts

export interface CreateUser {
    name: string
    father_surname: string
    mother_surname: string
    medical_department: string
    email: string
    password: string
  }
  
  export async function createUser(payload: CreateUser) {
    const response = await fetch("http://localhost:8000/users/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
  
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to create user")
    }
  
    return response.json()
  }
  