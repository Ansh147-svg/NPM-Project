"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHeader, TableHead, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"

interface MonitorTableProps {
  monitors: any[]
  onRefresh: () => Promise<void>
}

export const MonitorTable = ({ monitors, onRefresh }: MonitorTableProps) => {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)

  const refresh = async () => {
    setLoading(true)
    try {
      await onRefresh()
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to refresh",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  if (monitors.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No monitors found</p>
        <Button variant="outline" onClick={refresh}>
          Refresh
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Monitor Status</h2>
        <Button variant="outline" onClick={refresh}>
          {loading ? "Refreshing..." : "Refresh"}
        </Button>
      </div>
      
      <div className="overflow-x-auto">
        <Table className="w-full">
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Target</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Response Time</TableHead>
              <TableHead>Uptime</TableHead>
              <TableHead>Last Checked</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {monitors.map((monitor: any) => {
              const statusClass = 
                monitor.status === "up" ? "bg-green-100 text-green-800" :
                monitor.status === "down" ? "bg-red-100 text-red-800" :
                monitor.status === "degraded" ? "bg-yellow-100 text-yellow-800" :
                "bg-gray-100 text-gray-800"
              
              return (
                <TableRow key={monitor.id}>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full 
                        {monitor.status === 'up' ? 'bg-green-500' : 
                         monitor.status === 'down' ? 'bg-red-500' : 
                         monitor.status === 'degraded' ? 'bg-yellow-500' : 
                         'bg-gray-500'}"></div>
                        <span className="font-medium">{monitor.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-xs">{monitor.type}</span>
                  </TableCell>
                  <TableCell title={monitor.target}>
                    <span className="break-all max-w-[150px]">{monitor.target}</span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={monitor.status === "up" ? "default" : 
                      monitor.status === "down" ? "destructive" : 
                      monitor.status === "degraded" ? "secondary" : "outline"}>
                      {monitor.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {monitor.response_time_ms ? `${monitor.response_time_ms.toFixed(1)} ms` : "N/A"}
                  </TableCell>
                  <TableCell>
                    {monitor.availability_percentage !== undefined ? 
                      `${monitor.availability_percentage.toFixed(2)}%` : "N/A"}
                  </TableCell>
                  <TableCell>
                    {monitor.last_checked_at ? 
                      new Date(monitor.last_checked_at).toLocaleTimeString() : 
                      "Never"}
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}