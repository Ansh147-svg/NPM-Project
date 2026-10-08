"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { useAuth } from "@/app/providers/auth-provider"

export default function Home() {
  const { user } = useAuth()

  return (
    <main className="container mx-auto p-4">
      {!user ? (
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Network Monitoring Platform</h1>
          <div className="flex gap-2">
            <Button asChild>
              <Link href="/login">Login</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/signup">Sign Up</Link>
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Network Monitoring Platform</h1>
          <div className="flex items-center space-x-4">
            <span className="text-sm">Welcome, {user.full_name || user.email}</span>
            <button
              onClick={() => {
                // TODO: Implement logout
                localStorage.removeItem("token")
                localStorage.removeItem("user")
                window.location.reload()
              }}
              className="text-sm text-muted-foreground hover:underline"
            >
              Logout
            </button>
          </div>
        </div>
      )}
      
      {user ? (
        <>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader>
              <CardTitle>Monitors</CardTitle>
              <CardDescription>Real-time monitoring status</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">128</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Agents</CardTitle>
              <CardDescription>Distributed agents</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">12</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Incidents</CardTitle>
              <CardDescription>Active issues</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-red-500">3</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Uptime</CardTitle>
              <CardDescription>Last 24h</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">99.98%</p>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="flex gap-2">
              <Button asChild>
                <Link href="/monitors">View Monitors</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/agents">Manage Agents</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/alerts">Alert Rules</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
        </>
      ) : (
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold">Welcome to Network Monitoring Platform</h2>
          <p className="text-lg text-muted-foreground mb-6">
            Monitor your network infrastructure with real-time alerts and distributed agents
          </p>
          <div className="flex justify-center gap-4">
            <Button asChild>
              <Link href="/login">Get Started</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/signup">Create Account</Link>
            </Button>
          </div>
        </div>
      )}
    </main>
  )
}