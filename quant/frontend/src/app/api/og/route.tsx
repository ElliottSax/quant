import { ImageResponse } from 'next/og'
import { NextRequest } from 'next/server'

export const runtime = 'edge'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const title = searchParams.get('title') || 'QuantEngines'

    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #334155 100%)',
            color: 'white',
            position: 'relative',
          }}
        >
          {/* Amber accent glow */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background:
                'radial-gradient(ellipse at 50% 0%, rgba(245,158,11,0.15) 0%, transparent 60%), radial-gradient(ellipse at 80% 100%, rgba(245,158,11,0.08) 0%, transparent 50%)',
            }}
          />

          {/* Content */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1,
              maxWidth: 900,
              padding: '0 40px',
              textAlign: 'center',
            }}
          >
            {/* Logo mark */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 64,
                height: 64,
                borderRadius: 12,
                background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                fontSize: 32,
                fontWeight: 800,
                color: '#0f172a',
                marginBottom: 24,
              }}
            >
              Q
            </div>

            {/* Site name */}
            <div
              style={{
                fontSize: 28,
                fontWeight: 600,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: '#f59e0b',
                marginBottom: 20,
              }}
            >
              QuantEngines
            </div>

            {/* Page title */}
            <div
              style={{
                fontSize: 52,
                fontWeight: 700,
                lineHeight: 1.2,
                marginBottom: 24,
                maxWidth: 800,
              }}
            >
              {title}
            </div>

            {/* Tagline */}
            <div
              style={{
                fontSize: 22,
                fontWeight: 400,
                opacity: 0.7,
              }}
            >
              Quantitative Trading Platform
            </div>
          </div>

          {/* Bottom bar */}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: 4,
              background: 'linear-gradient(90deg, #f59e0b, #d97706, #b45309)',
            }}
          />
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    )
  } catch (e) {
    console.log(`Failed to generate OG image: ${e}`)

    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#0f172a',
            color: 'white',
          }}
        >
          <div style={{ fontSize: 48, fontWeight: 700, color: '#f59e0b' }}>QuantEngines</div>
          <div style={{ fontSize: 24, opacity: 0.7, marginTop: 12 }}>
            Quantitative Trading Platform
          </div>
        </div>
      ),
      { width: 1200, height: 630 }
    )
  }
}
