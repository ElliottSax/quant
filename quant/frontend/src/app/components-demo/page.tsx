'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

export default function ComponentsDemo() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Component Showcase</h1>
        <p className="text-[hsl(215,20%,60%)]">
          A demonstration of all shadcn/ui components and custom components
        </p>
      </div>

      {/* Buttons */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold text-white">Buttons</h2>
        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Button Variants</CardTitle>
            <CardDescription className="text-[hsl(215,20%,55%)]">
              Different button styles and sizes
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Button>Default</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="link">Link</Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button size="sm">Small</Button>
              <Button size="default">Default</Button>
              <Button size="lg">Large</Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button disabled>Disabled</Button>
              <Button className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)]">
                Custom Color
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Cards */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold text-white">Cards</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
            <CardHeader>
              <CardTitle className="text-white">Simple Card</CardTitle>
              <CardDescription className="text-[hsl(215,20%,55%)]">
                Basic card with header and content
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-[hsl(215,20%,65%)]">
                This is a simple card component with header, description, and content.
              </p>
            </CardContent>
          </Card>

          <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
            <CardHeader>
              <CardTitle className="text-white">Card with Footer</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[hsl(215,20%,65%)]">
                This card includes a footer section.
              </p>
            </CardContent>
            <CardFooter>
              <Button size="sm" variant="outline" className="border-[hsl(215,40%,20%)]">
                Action
              </Button>
            </CardFooter>
          </Card>

          <Card className="border-green-500/30 bg-[hsl(220,55%,7%)]">
            <CardHeader>
              <CardTitle className="text-white">Highlighted Card</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[hsl(215,20%,65%)]">
                Card with custom border color.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Inputs */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold text-white">Input Fields</h2>
        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Input Variants</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 max-w-md">
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(215,20%,70%)]">
                Default Input
              </label>
              <Input
                placeholder="Enter text..."
                className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(215,20%,70%)]">
                Email Input
              </label>
              <Input
                type="email"
                placeholder="you@example.com"
                className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(215,20%,70%)]">
                Password Input
              </label>
              <Input
                type="password"
                placeholder="••••••••"
                className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(215,20%,70%)]">
                Disabled Input
              </label>
              <Input
                disabled
                placeholder="Disabled"
                className="bg-[hsl(220,60%,4%)] border-[hsl(215,40%,20%)] text-white"
              />
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Badges */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold text-white">Badges</h2>
        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Badge Variants</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="destructive">Destructive</Badge>
              <Badge variant="outline">Outline</Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge className="bg-green-500">Success</Badge>
              <Badge className="bg-yellow-500 text-black">Warning</Badge>
              <Badge className="bg-blue-500">Info</Badge>
              <Badge className="bg-purple-500">Custom</Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)]">
                Premium
              </Badge>
              <Badge className="bg-red-500/20 text-red-400 border border-red-500/30">
                Error
              </Badge>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Skeletons */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold text-white">Loading States</h2>
        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Skeleton Loaders</CardTitle>
            <CardDescription className="text-[hsl(215,20%,55%)]">
              Loading placeholders for content
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
            <div className="flex gap-4">
              <Skeleton className="h-12 w-12 rounded-full" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Colors */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold text-white">Color Palette</h2>
        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Theme Colors</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <ColorSwatch
                name="Primary Gold"
                color="hsl(45, 96%, 58%)"
                className="bg-[hsl(45,96%,58%)]"
              />
              <ColorSwatch
                name="Background Dark"
                color="hsl(220, 60%, 4%)"
                className="bg-[hsl(220,60%,4%)]"
              />
              <ColorSwatch
                name="Card Background"
                color="hsl(220, 55%, 7%)"
                className="bg-[hsl(220,55%,7%)]"
              />
              <ColorSwatch
                name="Border"
                color="hsl(215, 40%, 18%)"
                className="bg-[hsl(215,40%,18%)]"
              />
              <ColorSwatch
                name="Success Green"
                color="#22c55e"
                className="bg-green-500"
              />
              <ColorSwatch
                name="Error Red"
                color="#ef4444"
                className="bg-red-500"
              />
              <ColorSwatch
                name="Info Blue"
                color="hsl(210, 100%, 56%)"
                className="bg-[hsl(210,100%,56%)]"
              />
              <ColorSwatch
                name="Warning Yellow"
                color="#eab308"
                className="bg-yellow-500"
              />
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Typography */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold text-white">Typography</h2>
        <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
          <CardHeader>
            <CardTitle className="text-white">Text Styles</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-xs text-[hsl(215,20%,55%)] mb-2">Heading 1</p>
              <h1 className="text-4xl font-bold text-white">The quick brown fox</h1>
            </div>
            <div>
              <p className="text-xs text-[hsl(215,20%,55%)] mb-2">Heading 2</p>
              <h2 className="text-3xl font-bold text-white">The quick brown fox</h2>
            </div>
            <div>
              <p className="text-xs text-[hsl(215,20%,55%)] mb-2">Heading 3</p>
              <h3 className="text-2xl font-bold text-white">The quick brown fox</h3>
            </div>
            <div>
              <p className="text-xs text-[hsl(215,20%,55%)] mb-2">Body Text</p>
              <p className="text-[hsl(215,20%,65%)]">
                The quick brown fox jumps over the lazy dog. This is standard body text.
              </p>
            </div>
            <div>
              <p className="text-xs text-[hsl(215,20%,55%)] mb-2">Monospace</p>
              <p className="font-mono text-[hsl(215,20%,70%)]">
                const code = 'example';
              </p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}

function ColorSwatch({ name, color, className }: { name: string; color: string; className: string }) {
  return (
    <div className="space-y-2">
      <div className={`h-16 rounded-lg border border-white/10 ${className}`}></div>
      <div>
        <p className="text-xs font-medium text-white">{name}</p>
        <p className="text-[10px] font-mono text-[hsl(215,20%,55%)]">{color}</p>
      </div>
    </div>
  )
}
