"use client"

import { useEffect, useState } from "react"

export default function Error({ error, resetError }: { error: Error & { digest?: string }; resetError: () => void }) {
  const [message, setMessage] = useState("")

  useEffect(() => {
    if (error.message) {
      setMessage(error.message)
    } else {
      setMessage("An unexpected error occurred")
    }
  }, [error])

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-red-500 mb-4">Something went wrong</h1>
        <p className="text-lg text-gray-600 mb-6">{message}</p>
        <button
          onClick={resetError}
          className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-md"
        >
          Try again
        </button>
      </div>
    </main>
  )
}