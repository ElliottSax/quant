import Link from 'next/link'

interface Article {
  slug: string
  title: string
  excerpt?: string
}

export function RelatedArticles({ currentSlug, articles }: { currentSlug: string; articles: Article[] }) {
  const related = articles.filter(a => a.slug !== currentSlug).slice(0, 3)
  if (!related.length) return null

  return (
    <section className="my-12 py-8 border-t border-gray-200">
      <h2 className="text-2xl font-bold mb-8">More Strategies</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {related.map(a => (
          <Link key={a.slug} href={`/strategies/${a.slug}`}>
            <div className="border rounded-lg p-4 hover:shadow-lg hover:border-purple-300 transition">
              <h3 className="font-bold text-lg mb-2 hover:text-purple-600">{a.title}</h3>
              <p className="text-gray-600 text-sm">{a.excerpt}</p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  )
}
