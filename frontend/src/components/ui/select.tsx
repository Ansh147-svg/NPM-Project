"use client"

import * as React from "react"
import * as SelectPrimitive from "@radix-ui/react-select"
import { cn } from "@/lib/utils"

const Select = ({
  children,
  ...props
}: React.ComponentPropsWithoutRef<typeof SelectPrimitive.Root>) => (
  <SelectPrimitive.Root
    {...props}
  >
    {children}
  </SelectPrimitive.Root>
)

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    {...props}
    children={children}
  />
))
SelectTrigger.displayName = SelectPrimitive.Trigger.displayName

const SelectValue = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Value>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Value>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Value
    ref={ref}
    className={cn(className)}
    {...props}
    children={children}
  />
))
SelectValue.displayName = SelectPrimitive.Value.displayName

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Content
    ref={ref}
    className={cn(
      "z-50 min-h-[8rem] w-full max-h-96 overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md",
      className
    )}
    {...props}
    children={children}
  />
))
SelectContent.displayName = SelectPrimitive.Content.displayName

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn(
      "flex cursor-default select-none items-center rounded-sm px-2 py-1 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    {...props}
    children={children}
  />
))
SelectItem.displayName = SelectPrimitive.Item.displayName

export {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
}