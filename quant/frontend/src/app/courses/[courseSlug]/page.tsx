import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { courses, getCourse, type Block } from '@/data/courses'

export function generateStaticParams() {
  return courses.map((c) => ({ courseSlug: c.slug }))
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ courseSlug: string }>
}): Promise<Metadata> {
  const { courseSlug } = await params
  const course = getCourse(courseSlug)
  if (!course) return { title: 'Course Not Found | QuantEngines' }
  return {
    title: `${course.title} — Free Course | QuantEngines`,
    description: course.description,
  }
}

/** Renders inline **bold** without needing a markdown dependency. */
function Inline({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return (
    <>
      {parts.map((p, i) =>
        p.startsWith('**') && p.endsWith('**') ? (
          <strong key={i} className="font-semibold text-white">
            {p.slice(2, -2)}
          </strong>
        ) : (
          <span key={i}>{p}</span>
        )
      )}
    </>
  )
}

function Blocks({ blocks }: { blocks: Block[] }) {
  return (
    <>
      {blocks.map((b, i) => {
        if (b.type === 'h2') return <h3 key={i} className="text-2xl font-bold mt-8 mb-3 text-white"><Inline text={b.text} /></h3>
        if (b.type === 'h3') return <h4 key={i} className="text-lg font-semibold mt-6 mb-2 text-white"><Inline text={b.text} /></h4>
        if (b.type === 'p') return <p key={i} className="mb-4 leading-7 text-gray-300"><Inline text={b.text} /></p>
        const items = b.items.map((it, j) => (
          <li key={j} className="leading-7 text-gray-300"><Inline text={it} /></li>
        ))
        return b.type === 'ul' ? (
          <ul key={i} className="list-disc pl-6 mb-4 space-y-1">{items}</ul>
        ) : (
          <ol key={i} className="list-decimal pl-6 mb-4 space-y-1">{items}</ol>
        )
      })}
    </>
  )
}

export default async function CoursePage({ params }: { params: Promise<{ courseSlug: string }> }) {
  const { courseSlug } = await params
  const course = getCourse(courseSlug)
  if (!course) notFound()

  return (
    <main className="container mx-auto px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <nav className="text-sm text-gray-500 mb-6">
          <Link href="/courses" className="hover:text-white">Free Courses</Link>
          {' / '}
          <span className="text-white">{course.title}</span>
        </nav>

        <h1 className="text-4xl font-bold mb-3 text-white">{course.title}</h1>
        <p className="text-lg text-gray-400 mb-6">{course.description}</p>
        <p className="text-sm text-gray-500 mb-10">
          {course.lessons.length} lessons · {course.estimatedTime} · free, no signup
        </p>

        <div className="rounded-lg border border-gray-700 p-5 mb-12">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500 mb-3">Contents</h2>
          <ol className="list-decimal pl-5 space-y-1">
            {course.lessons.map((l) => (
              <li key={l.slug}>
                <a href={`#${l.slug}`} className="text-blue-400 hover:underline">{l.title}</a>
                <span className="text-gray-500 text-sm"> · {l.readTime}</span>
              </li>
            ))}
          </ol>
        </div>

        {course.lessons.map((lesson, i) => (
          <section key={lesson.slug} id={lesson.slug} className="mb-14 scroll-mt-20">
            <p className="text-sm font-medium text-blue-400 mb-1">
              Lesson {i + 1} of {course.lessons.length} · {lesson.readTime}
            </p>
            <h2 className="text-3xl font-bold mb-2 text-white">{lesson.title}</h2>
            <p className="text-gray-400 mb-6">{lesson.description}</p>

            <Blocks blocks={lesson.blocks} />

            {lesson.tryIt && (
              <div className="mt-6 rounded-lg border border-blue-900 bg-blue-950/30 p-5">
                <h3 className="font-semibold mb-1 text-white">{lesson.tryIt.title}</h3>
                <p className="text-gray-300 mb-3">{lesson.tryIt.description}</p>
                <Link href={lesson.tryIt.href} className="inline-block rounded-md bg-blue-600 px-4 py-2 text-white font-medium hover:bg-blue-700">
                  {lesson.tryIt.label}
                </Link>
              </div>
            )}
          </section>
        ))}

        <div className="border-t border-gray-700 pt-8">
          <p className="text-gray-400 mb-4">Put it into practice with the backtesting tools.</p>
          <Link href="/backtesting" className="inline-block rounded-md bg-blue-600 px-5 py-2.5 text-white font-medium hover:bg-blue-700">
            Open Backtesting
          </Link>
        </div>
      </div>
    </main>
  )
}
