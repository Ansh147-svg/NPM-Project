"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { MonitorForm } from "@/components/monitor-form"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"

export default function CreateMonitorPage() {
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  const handleSubmit = async (data: any) => {
    setLoading(true)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch("/api/v1/monitors/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          ...data,
          tenant_id: 1 // TODO: get from user context
        })
      })
      
      if (!res.ok) throw new Error("Failed to create monitor")
      
      toast({
        title: "Success",
        description: "Monitor created successfully"
      })
      router.push("/monitors")
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to create monitor: " + (err instanceof Error ? err.message : String(err)),
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <CardHeader>
        <CardTitle>Create New Monitor</CardTitle>
        <CardDescription>
          Configure a new network monitor
        </CardDescription>
      </CardHeader>
      
      <MonitorForm onSubmit={handleSubmit} />
      
      <div className="flex justify-end">
        <Button
          variant="outline"
          onClick={() => router.back()}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={loading}
          className="ml-2"
        >
          {loading ? "Creating..." : "Create Monitor"}
        </Button>
      </div>
    </div>
  )
}