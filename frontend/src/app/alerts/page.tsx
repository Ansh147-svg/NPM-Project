"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHeader, TableHead, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"

export default function AlertsPage() {
  const [loading, setLoading] = useState(true)
  const [alertRules, setAlertRules] = useState<any[]>([])
  const { toast } = useToast()

  useEffect(() => {
    loadAlertRules()
  }, [])

  const loadAlertRules = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch("/api/v1/alert_rules/", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
      
      if (!res.ok) throw new Error("Failed to fetch alert rules")
      
      const data = await res.json()
      setAlertRules(Array.isArray(data) ? data : (data.items || []))
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to load alert rules",
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
        <CardTitle>Alert Rules</CardTitle>
        <CardDescription>
          Configure alerting conditions
        </CardDescription>
      </CardHeader>
      
      <div className="overflow-x-auto">
        <Table className="w-full">
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Monitor</TableHead>
              <TableHead>Condition</TableHead>
              <TableHead>For Duration</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {alertRules.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6}>
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">No alert rules found</p>
                    <Button variant="outline" onClick={() => {}}>
                      Create Alert Rule
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              alertRules.map((rule: any) => (
                <TableRow key={rule.id}>
                  <TableCell>{rule.name}</TableCell>
                  <TableCell>{rule.monitor_id ? `Monitor #${rule.monitor_id}` : "Global"}</TableCell>
                  <TableCell>
                    <code className="bg-muted px-1 py-0.5 rounded">{JSON.stringify(rule.condition)}</code>
                  </TableCell>
                  <TableCell>{rule.for_duration || 0}s</TableCell>
                  <TableCell>
                    <span className={rule.is_active ? "text-green-500" : "text-gray-500"}>
                      {rule.is_active ? "Active" : "Inactive"}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm" onClick={() => {}}>
                        Edit
                      </Button>
                      <Button variant="destructive" size="sm" onClick={() => {}}>
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}