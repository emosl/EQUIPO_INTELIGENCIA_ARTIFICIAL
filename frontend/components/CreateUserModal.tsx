"use client"

import { useState } from "react"
import { createUser } from "../API/user"

export default function CreateUserModal({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState("")
  const [fatherSurname, setFatherSurname] = useState("")
  const [motherSurname, setMotherSurname] = useState("")
  const [medicalDept, setMedicalDept] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")

    try {
      await createUser({
        name,
        father_surname: fatherSurname,
        mother_surname: motherSurname,
        medical_department: medicalDept,
        email,
        password,
      })
      setSuccess("Usuario creado correctamente")
      // Opcional: limpiar campos
      setName("")
      setFatherSurname("")
      setMotherSurname("")
      setMedicalDept("")
      setEmail("")
      setPassword("")
      // Cierra el modal (tras un breve retraso):
      setTimeout(onClose, 1500)
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
        >
          ✖
        </button>
        <h2 className="text-xl font-semibold mb-4 text-center">Crear Usuario</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Nombre"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="block w-full mt-1 rounded-md border-gray-300 shadow-sm"
          />
          <input
            type="text"
            placeholder="Apellido paterno"
            value={fatherSurname}
            onChange={(e) => setFatherSurname(e.target.value)}
            required
            className="block w-full mt-1 rounded-md border-gray-300 shadow-sm"
          />
          <input
            type="text"
            placeholder="Apellido materno"
            value={motherSurname}
            onChange={(e) => setMotherSurname(e.target.value)}
            required
            className="block w-full mt-1 rounded-md border-gray-300 shadow-sm"
          />
          <input
            type="text"
            placeholder="Departamento médico"
            value={medicalDept}
            onChange={(e) => setMedicalDept(e.target.value)}
            required
            className="block w-full mt-1 rounded-md border-gray-300 shadow-sm"
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="block w-full mt-1 rounded-md border-gray-300 shadow-sm"
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="block w-full mt-1 rounded-md border-gray-300 shadow-sm"
          />
          <button
            type="submit"
            className="mt-2 w-full py-2 px-4 bg-blue-600 text-white rounded-md shadow hover:bg-blue-700"
          >
            Enviar
          </button>
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          {success && <p className="mt-2 text-sm text-green-600">{success}</p>}
        </form>
      </div>
    </div>
  )
}
