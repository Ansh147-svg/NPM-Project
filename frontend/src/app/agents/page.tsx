"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHeader, TableHead, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"

export default function AgentsPage() {
  const [loading, setLoading] = useState(true)
  const [agents, setAgents] = useState<any[]>([])
  const { toast } = useToast()

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch("/api/v1/agents/", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
      
      if (!res.ok) throw new Error("Failed to fetch agents")
      
      const data = await res.json()
      setAgents(Array.isArray(data) ? data : (data.items || []))
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to load agents",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="h-[60vh] flex items-center justify-center">Loading...</div>
  }

  return (
    <div>
      <CardHeader>
        <CardTitle>Agents</CardTitle>
        <CardDescription>
          Distributed monitoring agents
        </CardDescription>
      </CardHeader>
      
      <div className="overflow-x-auto">
        <Table className="w-full">
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Hostname</TableHead>
              <TableHead>IP Address</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Last Seen</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {agents.map((agent: any) => (
              <TableRow key={agent.id}>
                <TableCell>{agent.name}</TableCell>
                <TableCell>{agent.hostname}</TableCell>
                <TableCell>{agent.ip_address}</TableCell>
                <TableCell>{agent.version}</TableCell>
                <TableCell className={agent.is_online ? "text-green-500" : "text-red-500"}>
                  {agent.is_online ? "Online" : "Offline"}
                </TableCell>
                <TableCell>
                  {agent.last_heartbeat ? new Date(agent.last_heartbeat).toLocaleString() : "Never"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}