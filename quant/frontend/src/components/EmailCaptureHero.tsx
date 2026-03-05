import { EmailCapture } from '@/components/EmailCapture'

export function EmailCaptureHero() {
  return (
    <EmailCapture
      site="quant"
      supabaseUrl="https://jznljskfvhlqlshofkvd.supabase.co"
      headline="Get Weekly Trading Strategies"
      subheading="Join 5,000+ traders getting exclusive tips on quantitative strategies, backtesting, and market insights."
      bgGradient="from-purple-600 to-purple-800"
      theme="purple"
    />
  )
}
