import { EmailCapture } from '@/components/EmailCapture'

// Most of quantengines.com's real readers land directly on a blog post (28d GA4, US-only), but the only
// email capture lived on the homepage and two congress pages, so the posts had no conversion path besides
// the tool link. Copy deliberately avoids a send schedule ("weekly"): promise only what is true.
export function BlogEmailCapture() {
  return (
    <div className="my-10">
      <EmailCapture
        site="quant"
        headline="Get new strategy write-ups by email"
        subheading="New backtesting guides and strategy breakdowns as we publish them. Free, unsubscribe anytime."
        bgGradient="from-purple-600 to-purple-800"
        theme="purple"
      />
    </div>
  )
}
