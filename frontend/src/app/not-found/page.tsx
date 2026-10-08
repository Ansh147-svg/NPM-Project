import Link from "next/link"

export default function NotFoundPage() {
  return (
    <main className="container mx-auto p-8 text-center">
      <h1 className="text-2xl font-bold">Page not found</h1>
      <p className="mt-2">The page you requested could not be found.</p>
      <Link className="mt-4 inline-block underline" href="/">
        Return home
      </Link>
    </main>
  )
}