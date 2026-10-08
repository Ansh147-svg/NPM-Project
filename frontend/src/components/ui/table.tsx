"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

const Table = React.forwardRef<
  HTMLTableElement,
  React.TableHTMLAttributes<HTMLTableElement>
>(({ className, ...props }, ref) => (
  <table
    ref={ref}
    className={cn(
      "w-full text-sm text-left rtl:text-right border-collapse",
      className
    )}
    {...props}
  />
))
Table.displayName = "Table"

const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.TableHTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <thead
    ref={ref}
    className={cn(className)}
    {...props}
  />
))
TableHeader.displayName = "TableHeader"

const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.TableHTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody
    ref={ref}
    className={cn(className)}
    {...props}
  />
))
TableBody.displayName = "TableBody"

const TableCell = React.forwardRef<
  HTMLTableDataCellElement,
  React.TdHTMLAttributes<HTMLTableDataCellElement>
>(({ className, ...props }, ref) => (
  <td
    ref={ref}
    className={cn("px-4 py-2", className)}
    {...props}
  />
))
TableCell.displayName = "TableCell"

const TableHead = React.forwardRef<
  HTMLTableHeaderCellElement,
  React.ThHTMLAttributes<HTMLTableHeaderCellElement>
>(({ className, ...props }, ref) => (
  <th
    ref={ref}
    className={cn("px-4 py-2", className)}
    {...props}
  />
))
TableHead.displayName = "TableHead"

const TableRow = React.forwardRef<
  HTMLTableRowElement,
  React.TableHTMLAttributes<HTMLTableRowElement>
>(({ className, ...props }, ref) => (
  <tr
    ref={ref}
    className={cn(className)}
    {...props}
  />
))
TableRow.displayName = "TableRow"

export { Table, TableHeader, TableBody, TableCell, TableHead, TableRow }