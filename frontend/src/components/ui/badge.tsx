"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

const Badge = React.forwardRef<
  HTMLSpanElement,
  React.ComponentPropsWithoutRef<"span"> & {
    variant?: "default" | "destructive" | "outline" | "secondary"
  }
>(({ className, variant = "default", ...props }) => {
  const variantClasses = {
    default: "bg-primary text-primary-foreground",
    destructive: "bg-destructive text-destructive-foreground",
    outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
    secondary: "bg-secondary text-secondary-foreground",
  }

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  )
})
Badge.displayName = "Badge"

export { Badge }