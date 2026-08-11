/**
 * FAQ extraction for FAQPage structured data.
 *
 * Articles here have no `faq` frontmatter field — the site's equivalent shape
 * is a "Frequently Asked Questions" section inside the markdown body. Three
 * authoring styles appear in content/blog:
 *
 *   **Q1: How long should I hold positions with this strategy?**
 *   A: The typical holding period ...
 *
 *   **Q1**: What's the maximum profit on this strategy?
 *   **A**: Maximum profit occurs ...
 *
 *   ### Q1: What is the best entry point ...?
 *   **Answer**: Current valuations ...
 *
 * Only Q&A that is genuinely present (and therefore visible on the rendered
 * page, as Google requires) is returned; posts without a FAQ section yield [].
 */

export interface FaqItem {
  question: string;
  answer: string;
}

// Headings that open a FAQ block ("## FAQ", "## Frequently Asked Questions (FAQ)", ...)
const FAQ_HEADING = /^#{1,4}\s*\**\s*(?:FAQs?|Frequently Asked Questions|Common Questions)\b/i;
const HEADING = /^(#{1,6})\s+(.*)$/;
// "**Q: ...**" / "**Q1: ...**". The separator after Q/Qn is required so ordinary
// bold lines such as "**Quick math**:" are not mistaken for questions.
const BOLD_QUESTION = /^\*\*\s*Q\s*\d*\s*[:.)\-]\s*(.+?)\s*\*\*:?\s*$/;
// "**Q1**: ..." — the label is bold and the question sits outside it.
const BOLD_LABEL_QUESTION = /^\*\*\s*Q\s*\d*\s*\*\*\s*[:.)\-]\s*(.+?)\s*$/;
// Inside a FAQ section only: a bare "Q: ..." line (the answer follows below).
const PLAIN_QUESTION = /^Q\s*\d*\s*[:.)\-]\s*(.+)$/;
// Inside a FAQ section only: "1. **What is X?**: answer on the same line".
const INLINE_QUESTION = /^(?:\d+[.)]\s*)?\*\*\s*(.+?\?)\s*\*\*\s*[:.]?\s*(.*)$/;
// Inside a FAQ section only: a plain numbered question ("1. What is X?"),
// optionally with the answer running on after it on the same line.
const NUMBERED_QUESTION = /^\d+[.)]\s+(.+\?)\s*$/;
const NUMBERED_INLINE_QUESTION = /^\d+[.)]\s+(.+?\?)\s+(.+)$/;
// Leading "A:" / "Answer:" / "**Answer**:" marker on the first answer line.
const ANSWER_PREFIX = /^(?:\*\*\s*(?:A|Answer)\s*\*\*\s*[:.]?|A\s*[:.]|Answer\s*[:.])\s*/i;
const LIST_MARKER = /^(?:[-*+]\s+|\d+[.)]\s+)/;

function clean(text: string): string {
  return text
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/`/g, '')
    .replace(/\*+/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function cleanQuestion(text: string): string {
  return clean(text)
    .replace(/^(?:Q\s*\d*\s*[:.)\-]\s*|\d+[.)]\s*)/i, '')
    .trim();
}

export function extractFaqs(markdown: string): FaqItem[] {
  if (!markdown) return [];

  const lines = markdown.replace(/\r\n?/g, '\n').split('\n');
  const items: FaqItem[] = [];
  let inFaqSection = false;
  let faqLevel = 0;
  let current: { question: string; answer: string[] } | null = null;

  const flush = () => {
    const cur = current;
    current = null;
    if (!cur) return;
    const question = cleanQuestion(cur.question);
    const answer = clean(cur.answer.join(' '));
    if (question.length <= 3 || answer.length <= 10) return;
    // Leftover square brackets mean unfilled template placeholders such as
    // "[specific conditions]" — never publish those as structured data.
    if (/[[\]]/.test(question + answer)) return;
    items.push({ question, answer });
  };

  for (const raw of lines) {
    const line = raw.trim();
    const heading = line.match(HEADING);

    if (heading) {
      const level = heading[1].length;
      if (FAQ_HEADING.test(line)) {
        flush();
        inFaqSection = true;
        faqLevel = level;
        continue;
      }
      // A sub-heading inside the FAQ section starts a new question. Require a
      // question mark so descriptive sub-headings are not picked up.
      if (inFaqSection && level > faqLevel && heading[2].includes('?')) {
        flush();
        current = { question: heading[2], answer: [] };
        continue;
      }
      flush();
      if (level <= faqLevel) inFaqSection = false;
      continue;
    }

    const boldQuestion = line.match(BOLD_QUESTION) || line.match(BOLD_LABEL_QUESTION);
    if (boldQuestion) {
      flush();
      current = { question: boldQuestion[1], answer: [] };
      continue;
    }

    if (inFaqSection) {
      const inlineQuestion = line.match(INLINE_QUESTION) || line.match(NUMBERED_INLINE_QUESTION);
      if (inlineQuestion) {
        flush();
        current = { question: inlineQuestion[1], answer: inlineQuestion[2] ? [inlineQuestion[2]] : [] };
        continue;
      }
      const plainQuestion = line.match(PLAIN_QUESTION) || line.match(NUMBERED_QUESTION);
      if (plainQuestion) {
        flush();
        current = { question: plainQuestion[1], answer: [] };
        continue;
      }
    }

    const cur = current;
    if (!cur) continue;
    if (!line) continue;
    // A table or a horizontal rule ends the answer text.
    if (line.startsWith('|') || /^(?:---+|\*\*\*+|___+)$/.test(line)) {
      flush();
      continue;
    }
    cur.answer.push(line.replace(ANSWER_PREFIX, '').replace(LIST_MARKER, ''));
  }
  flush();

  const seen = new Set<string>();
  return items.filter((item) => {
    const key = item.question.toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
