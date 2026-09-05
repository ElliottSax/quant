/**
 * HowTo extraction for HowTo structured data.
 *
 * Mirrors extractFaqs() in src/lib/faq-extract.ts: only emit schema for content
 * that is genuinely, visibly present in the rendered article -- never fabricate
 * steps that aren't there.
 *
 * A grep across content/blog for `^#{2,4} Step [0-9]+` turned up 18 posts
 * written as numbered walkthroughs ("## Step 1: ...", "### Step 2: ...", etc).
 * Some of those only have two steps, or a step sequence is interrupted partway
 * through by an unrelated same-level heading -- neither of those should produce
 * a HowTo block, so this only fires on a contiguous, sequentially-numbered run
 * of three or more same-level "Step N" headings.
 *
 * "Contiguous" allows deeper headings inside a step (e.g. a "### Sub-heading"
 * nested under "## Step 1") -- those are part of the step's own content. It is
 * broken by any heading at the same level or shallower that isn't the next
 * step in sequence.
 */

export interface HowToStepItem {
  name: string;
  text: string;
}

const HEADING = /^(#{1,6})\s+(.*)$/;
// "## Step 1: Title" / "### Step 2 - Title" / "#### Step 3. Title" / bare "## Step 4"
const STEP_HEADING = /^(#{2,4})\s+Step\s*\d+\s*[:.\-)]?\s*(.*)$/i;
const STEP_NUMBER = /^#{2,4}\s+Step\s*(\d+)/i;

function clean(text: string): string {
  return text
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/`/g, '')
    .replace(/\*+/g, '')
    .replace(/#+/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

interface StepAccumulator {
  level: number;
  num: number;
  title: string;
  body: string[];
}

export function extractHowTo(markdown: string): HowToStepItem[] {
  if (!markdown) return [];

  const lines = markdown.replace(/\r\n?/g, '\n').split('\n');
  const runs: StepAccumulator[][] = [];
  let current: StepAccumulator[] = [];
  let inCodeFence = false;

  const pushBodyLine = (line: string) => {
    if (!current.length) return;
    if (line.trim().startsWith('|')) return;
    current[current.length - 1].body.push(line);
  };

  const endRun = () => {
    if (current.length >= 3) runs.push(current);
    current = [];
  };

  for (const raw of lines) {
    // A fenced code block's contents are kept as step text (several of these
    // posts are code-first walkthroughs with barely any prose, and the code
    // is genuinely part of what's visible on the page) -- but critically, a
    // Python comment like "# Usage" inside a fence must never be mistaken for
    // a markdown heading (both start with "#"), or a code sample would
    // silently truncate a real step run.
    if (/^```/.test(raw.trim())) {
      inCodeFence = !inCodeFence;
      continue;
    }
    if (inCodeFence) {
      pushBodyLine(raw);
      continue;
    }

    const heading = raw.match(HEADING);
    if (heading) {
      const level = heading[1].length;
      const stepMatch = raw.match(STEP_HEADING);
      if (stepMatch) {
        const stepLevel = stepMatch[1].length;
        const num = Number(raw.match(STEP_NUMBER)![1]);
        const title = stepMatch[2].trim();
        const last = current[current.length - 1];
        if (!(last && last.level === stepLevel && num === last.num + 1)) {
          // Not a continuation of the current run -- close it out and start fresh.
          endRun();
        }
        current.push({ level: stepLevel, num, title, body: [] });
        continue;
      }
      // A non-step heading. Headings nested deeper than the run's step level
      // belong to the current step's own content; anything at the same level
      // or shallower breaks the run.
      if (current.length && level > current[0].level) {
        pushBodyLine(raw);
      } else {
        endRun();
      }
      continue;
    }
    pushBodyLine(raw);
  }
  endRun();

  if (!runs.length) return [];

  // Longest qualifying run wins; ties keep the first (earliest) one.
  const best = runs.reduce((a, b) => (b.length > a.length ? b : a));

  const steps = best
    .map((s) => ({
      name: clean(s.title) || `Step ${s.num}`,
      text: clean(s.body.join(' ')),
    }))
    .filter((s) => s.name.length > 0 && s.text.length > 10);

  // A step with no real body content (filtered out above) can drop a
  // qualifying run below the minimum -- re-check rather than emit a
  // two-step HowTo.
  return steps.length >= 3 ? steps : [];
}
