"use client"

import { useState, useCallback } from "react"

export const useToast = () => {
  const [toasts, setToasts] = useState<Array<{
    id: string
    title: string
    description?: string
    variant?: "default" | "destructive" | "outline" | "secondary"
  }>>([])

  const toast = useCallback(({ title, description = "", variant = "default" }: {
    title: string
    description?: string
    variant?: "default" | "destructive" | "outline" | "secondary"
  }) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts(prev => [
      ...prev,
      {
        id,
        title,
        description,
        variant
      }
    ])
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 5000)
  }, [])

  return { toast, toasts }
}