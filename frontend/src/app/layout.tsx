"use client"

import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "next-themes"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"
import { Toaster } from "sonner"
import { AuthProvider } from "@/app/providers/auth-provider"

const inter = Inter({ subsets: ["latin"] })

const queryClient = new QueryClient()

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AuthProvider>
            <QueryClientProvider client={queryClient}>
              {children}
              <Toaster />
              <ReactQueryDevtools initialIsOpen={false} />
            </QueryClientProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}