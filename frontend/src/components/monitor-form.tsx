"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { useForm } from "react-hook-form"
import { useToast } from "@/hooks/use-toast"

interface MonitorFormProps {
  onSubmit: (data: any) => Promise<void>
}

export const MonitorForm = ({ onSubmit }: MonitorFormProps) => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      name: "",
      type: "ping",
      target: "",
      port: "",
      interval: "60",
      timeout: "10",
      config: ""
    }
  })

  const { toast } = useToast()

  const onHandleSubmit = async (data: any) => {
    try {
      await onSubmit(data)
      toast({
        title: "Success",
        description: "Monitor saved successfully"
      })
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to save monitor",
        variant: "destructive"
      })
    }
  }

  return (
    <form onSubmit={handleSubmit(onHandleSubmit)} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="name">Monitor Name</Label>
          <Input
            id="name"
            type="text"
            placeholder="Enter monitor name"
            {...register("name", { required: "Name is required" })}
            className={errors.name ? "border-red-500" : ""}
          />
          {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="type">Monitor Type</Label>
          <Select defaultValue="ping" onValueChange={v => {}} {...register("type")}>
            <SelectTrigger>
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ping">Ping (ICMP)</SelectItem>
              <SelectItem value="http">HTTP/HTTPS</SelectItem>
              <SelectItem value="tcp">TCP Port</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="target">Target</Label>
          <Input
            id="target"
            type="text"
            placeholder="Hostname, IP, or URL"
            {...register("target", { required: "Target is required" })}
            className={errors.target ? "border-red-500" : ""}
          />
          {errors.target && <p className="text-sm text-red-500">{errors.target.message}</p>}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="port">Port (Optional)</Label>
          <Input
            id="port"
            type="number"
            placeholder="TCP port"
            {...register("port")}
            className={errors.port ? "border-red-500" : ""}
          />
          {errors.port && <p className="text-sm text-red-500">{errors.port.message}</p>}
        </div>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="interval">Check Interval (seconds)</Label>
          <Input
            id="interval"
            type="number"
            placeholder="60"
            defaultValue="60"
            {...register("interval", { 
              validate: (value) => 
                value === "" || (Number(value) > 0 && Number(value) <= 86400)
            })}
            className={errors.interval ? "border-red-500" : ""}
          />
          {errors.interval && <p className="text-sm text-red-500">{errors.interval.message}</p>}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="timeout">Timeout (seconds)</Label>
          <Input
            id="timeout"
            type="number"
            placeholder="10"
            defaultValue="10"
            {...register("timeout", { 
              validate: (value) => 
                value === "" || (Number(value) > 0 && Number(value) <= 300)
            })}
            className={errors.timeout ? "border-red-500" : ""}
          />
          {errors.timeout && <p className="text-sm text-red-500">{errors.timeout.message}</p>}
        </div>
      </div>
      
      <div className="space-y-4">
        <Label htmlFor="config">Advanced Configuration (JSON)</Label>
        <Textarea
          id="config"
          placeholder='{"headers": {"User-Agent": "MonitoringBot"}}'
          {...register("config")}
          className={errors.config ? "border-red-500" : ""}
          rows={4}
        />
        {errors.config && <p className="text-sm text-red-500">{errors.config.message}</p>}
      </div>
      
      <Button
        type="submit"
        className="w-full"
      >
        Save Monitor
      </Button>
    </form>
  )
}