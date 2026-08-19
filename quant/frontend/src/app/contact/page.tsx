import { Metadata } from 'next'
import Link from 'next/link'
import { Mail, AlertCircle, Code2 } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Contact | QuantEngines',
  description:
    'How to reach QuantEngines: general questions, data corrections, and API enquiries.',
}

const CHANNELS = [
  {
    icon: Mail,
    colour: 'text-blue-400',
    title: 'General questions',
    email: 'hello@quantengines.com',
    body: 'Anything about the site, the tools, your account, or privacy and data-removal requests.',
  },
  {
    icon: AlertCircle,
    colour: 'text-amber-400',
    title: 'Corrections',
    email: 'errors@quantengines.com',
    body: 'Spotted a wrong figure, a misattributed trade, or a filing we have read incorrectly? Send it here and we will check it.',
  },
  {
    icon: Code2,
    colour: 'text-emerald-400',
    title: 'API',
    email: 'api@quantengines.com',
    body: 'Questions about programmatic access and the data endpoints.',
  },
]

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">Contact</h1>
          <p className="text-slate-400 max-w-2xl mx-auto">
            We read everything that comes in. Email is the only channel — we have no
            phone line and no live chat.
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6">
          {CHANNELS.map(({ icon: Icon, colour, title, email, body }) => (
            <section
              key={email}
              className="bg-slate-900/60 border border-slate-700 rounded-xl p-6"
            >
              <div className="flex items-start gap-3 mb-2">
                <Icon className={`h-6 w-6 ${colour} shrink-0 mt-0.5`} />
                <h2 className="text-2xl font-bold text-white">{title}</h2>
              </div>
              <p className="text-slate-300 leading-relaxed mb-3">{body}</p>
              <a
                href={`mailto:${email}`}
                className="text-blue-400 underline font-mono text-sm"
              >
                {email}
              </a>
            </section>
          ))}

          <section className="bg-slate-900/60 border border-slate-700 rounded-xl p-6">
            <h2 className="text-2xl font-bold text-white mb-3">Before you write</h2>
            <ul className="list-disc pl-5 space-y-2 text-slate-300 leading-relaxed">
              <li>
                For a data error, our{' '}
                <Link href="/corrections-policy" className="text-blue-400 underline">
                  Corrections Policy
                </Link>{' '}
                explains what we need in order to act on it quickly.
              </li>
              <li>
                We cannot give investment advice, recommend securities, or comment on
                your personal portfolio — see the{' '}
                <Link href="/disclaimer" className="text-blue-400 underline">
                  Disclaimer
                </Link>
                .
              </li>
              <li>
                To have your email address or account removed, write to{' '}
                <a
                  href="mailto:hello@quantengines.com"
                  className="text-blue-400 underline"
                >
                  hello@quantengines.com
                </a>{' '}
                and we will action it — see the{' '}
                <Link href="/privacy" className="text-blue-400 underline">
                  Privacy Policy
                </Link>
                .
              </li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}
