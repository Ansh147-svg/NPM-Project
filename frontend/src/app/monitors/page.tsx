"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHeader, TableHead, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { MonitorForm } from "@/components/monitor-form"
import { MonitorTable } from "@/components/monitor-table"

export default function MonitorsPage() {
  const [loading, setLoading] = useState(true)
  const [monitors, setMonitors] = useState<any[]>([])
  const { toast } = useToast()

  useEffect(() => {
    loadMonitors()
  }, [])

  const loadMonitors = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch("/api/v1/monitors/?tenant_id=1", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
      
      if (!res.ok) throw new Error("Failed to fetch monitors")
      
      const data = await res.json()
      setMonitors(Array.isArray(data) ? data : (data.items || []))
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to load monitors",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const createMonitor = async (data: any) => {
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
      
      await loadMonitors()
      toast({
        title: "Success",
        description: "Monitor created successfully"
      })
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to create monitor",
        variant: "destructive"
      })
    }
  }

  if (loading) {
    return <div className="h-[60vh] flex items-center justify-center">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <CardHeader>
          <CardTitle>Monitors</CardTitle>
          <CardDescription>
            Monitor your network endpoints
          </CardDescription>
        </CardHeader>
        <Button variant="outline" asChild>
          <Link href="/monitors/create">Add Monitor</Link>
        </Button>
      </div>
      
      <MonitorTable monitors={monitors} onRefresh={loadMonitors} />
    </div>
  )
}