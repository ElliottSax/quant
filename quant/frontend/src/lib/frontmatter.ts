// ---------------------------------------------------------------------------
// Frontmatter value sanitizer
// ---------------------------------------------------------------------------
//
// WHY THIS EXISTS
//
// The generated articles in content/blog/*.md were written by a pipeline that
// re-quoted YAML scalars on every pass. The result is frontmatter values
// wrapped in runs of stray single quotes, e.g.
//
//   title: '''''''Bitcoin Trading Strategies for Beginners 2026: Complete Guide'''''''
//   published_date: '''''''2026-03-21'''''''
//   reading_time: '''11'''
//
// ...and a nested form where a real apostrophe was itself re-escaped:
//
//   title: '''''''Economic Indicators Explained: A Trader''''''''s Guide...'''''''
//
// The previous inline parsers stripped at most ONE leading/trailing DOUBLE
// quote (`^title:\s*"?(.*?)"?\s*$`), so:
//   * 193 titles reached <title>/og:title with literal ''''''' runs attached;
//   * a further 83 titles wrapped in ordinary single quotes ('Title') also
//     rendered their quotes literally, because only `"` was ever stripped;
//   * 39 titles that YAML had line-folded across two lines were TRUNCATED
//     mid-sentence, because the `$` in the old regex stopped at the first
//     newline.
//
// A sibling site shipped the identical bug and it surfaced in Google's results
// as '''Descript vs Runway ML 2026'''.
//
// WHAT THIS DOES
//
// cleanFrontmatterValue() collapses quote runs to a single quote (which also
// resolves YAML's '' escape into a real apostrophe), then strips any remaining
// leading/trailing quote+whitespace run, then normalises internal whitespace.
//
// readFrontmatterValue() additionally understands YAML line folding, so a value
// continued on following indented lines is read whole instead of truncated.
//
// SLUGS ARE NOT AFFECTED. Every route derives its slug from the FILE NAME
// (`file.replace(/\.md$/, '')`), never from a frontmatter value, so sanitising
// frontmatter cannot change or orphan an indexed URL.
// ---------------------------------------------------------------------------

/**
 * Normalise a raw YAML scalar that may be wrapped in stray runs of quotes.
 *
 *   "'''''''Complete Guide'''''''"  -> "Complete Guide"
 *   "'''2026-03-19'''"              -> "2026-03-19"
 *   "'''\"Stock Market Outlook\"'''" -> "Stock Market Outlook"
 *   "'''''''A Trader''''''''s Guide'''''''" -> "A Trader's Guide"
 */
export function cleanFrontmatterValue(raw: string): string {
  if (!raw) return ''

  // Fold YAML line continuations / stray newlines into single spaces first so
  // the quote-run logic sees one flat string.
  let v = raw.replace(/\s+/g, ' ').trim()

  // Collapse runs of repeated quotes down to one. This simultaneously undoes
  // the pipeline's quote duplication AND YAML's '' -> ' escape, so a genuine
  // apostrophe inside the value survives as a single '.
  v = v.replace(/'{2,}/g, "'")
  v = v.replace(/"{2,}/g, '"')

  // Strip whatever quoting remains on the outside.
  v = v.replace(/^[\s'"]+/, '').replace(/[\s'"]+$/, '')

  return v.replace(/\s+/g, ' ').trim()
}

/**
 * Read a single scalar key out of a YAML frontmatter block, honouring YAML line
 * folding (continuation lines are indented) and sanitising the result.
 *
 * Returns '' when the key is absent.
 */
export function readFrontmatterValue(yamlBlock: string, key: string): string {
  const m = yamlBlock.match(
    new RegExp(`^${key}:[ \\t]*(.*(?:\\r?\\n[ \\t]+\\S.*)*)$`, 'm'),
  )
  return m ? cleanFrontmatterValue(m[1]) : ''
}

/**
 * Read an inline YAML array (`tags: [a, b, c]`), sanitising each element.
 */
export function readFrontmatterArray(yamlBlock: string, key: string): string[] {
  const m = yamlBlock.match(new RegExp(`^${key}:\\s*\\[([^\\]]*)]`, 'm'))
  if (!m) return []
  return m[1]
    .split(',')
    .map((s) => cleanFrontmatterValue(s))
    .filter(Boolean)
}
