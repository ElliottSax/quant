export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-4">
          Quant Analytics Platform
        </h1>
        <p className="text-center text-muted-foreground">
          Track government stock trades with statistical rigor
        </p>
        <div className="mt-8 p-6 bg-card border border-border rounded-lg">
          <h2 className="text-2xl font-semibold mb-2">Development Mode</h2>
          <p className="text-muted-foreground">
            Frontend is running. Next step: Connect to backend API.
          </p>
        </div>
      </div>
    </main>
  )
}
