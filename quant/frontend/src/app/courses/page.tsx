import Link from 'next/link'
import type { Metadata } from 'next'
import { courses } from '@/data/courses'

export const metadata: Metadata = {
  title: 'Free Quant Trading Courses | QuantEngines',
  description:
    'Free, self-paced courses on quantitative trading — backtesting honestly, choosing strategies with a real edge, the metrics that matter, and avoiding overfitting. No signup required.',
}

export default function CoursesPage() {
  return (
    <main className="container mx-auto px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-3 text-white">Free Courses</h1>
        <p className="text-lg text-gray-400 mb-10">
          Self-paced quant trading courses. Free, no signup, no email required.
        </p>

        <div className="grid gap-6">
          {courses.map((course) => (
            <Link
              key={course.slug}
              href={`/courses/${course.slug}`}
              className="block rounded-lg border border-gray-700 p-6 hover:border-blue-500 transition-colors"
            >
              <div className="flex items-center gap-3 mb-2 text-xs">
                <span className="font-medium uppercase tracking-wide text-blue-400">{course.level}</span>
                <span className="text-gray-500">{course.estimatedTime}</span>
                <span className="text-gray-500">{course.lessons.length} lessons</span>
              </div>
              <h2 className="text-2xl font-semibold mb-2 text-white">{course.title}</h2>
              <p className="text-gray-400">{course.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </main>
  )
}
