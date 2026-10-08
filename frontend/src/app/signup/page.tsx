"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "sonner"

export default function SignupPage() {
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      email: "",
      password: "",
      full_name: "",
      tenant_name: "",
      tenant_slug: ""
    }
  })

  const onSubmit = async (data: any) => {
    setLoading(true)
    try {
      // First create tenant
      const tenantRes = await fetch("/api/v1/tenants/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: data.tenant_name,
          slug: data.tenant_slug,
          description: "Auto-created tenant"
        })
      })

      if (!tenantRes.ok) throw new Error("Failed to create tenant")

      const tenantData = await tenantRes.json()

      // Then create user
      const userRes = await fetch("/api/v1/users/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
          full_name: data.full_name,
          tenant_id: tenantData.id
        })
      })

      if (!userRes.ok) throw new Error("Failed to create user")

      toast.success("Account created! Please login.")
      router.push("/login")
    } catch (err) {
      toast.error("Signup failed: " + (err instanceof Error ? err.message : String(err)))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create Your Account</CardTitle>
          <CardDescription>
            Sign up for Network Monitoring Platform
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                {...register("email", { required: "Email is required" })}
                className={errors.email ? "border-red-500" : ""}
              />
              {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Create password"
                {...register("password", { required: "Password is required" })}
                className={errors.password ? "border-red-500" : ""}
              />
              {errors.password && <p className="text-sm text-red-500">{errors.password.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input
                id="full_name"
                type="text"
                placeholder="Your full name"
                {...register("full_name", { required: "Full name is required" })}
                className={errors.full_name ? "border-red-500" : ""}
              />
              {errors.full_name && <p className="text-sm text-red-500">{errors.full_name.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="tenant_name">Organization Name</Label>
              <Input
                id="tenant_name"
                type="text"
                placeholder="Your organization name"
                {...register("tenant_name", { required: "Organization name is required" })}
                className={errors.tenant_name ? "border-red-500" : ""}
              />
              {errors.tenant_name && <p className="text-sm text-red-500">{errors.tenant_name.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="tenant_slug">Organization Slug</Label>
              <Input
                id="tenant_slug"
                type="text"
                placeholder="e.g., my-company"
                {...register("tenant_slug", { required: "Slug is required" })}
                className={errors.tenant_slug ? "border-red-500" : ""}
              />
              {errors.tenant_slug && <p className="text-sm text-red-500">{errors.tenant_slug.message}</p>}
            </div>
            <Button
              type="submit"
              disabled={loading}
              className="w-full"
            >
              {loading ? "Creating account..." : "Create Account"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center pt-0">
          <p className="text-sm text-muted-foreground">
            Already have an account? <a href="/login" className="font-medium text-primary hover:underline">Sign in</a>
          </p>
        </CardFooter>
      </Card>
    </main>
  )
}