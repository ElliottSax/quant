// Affiliate pre-wiring rules: nothing renders without a real tracking URL; with one, the link is
// marked sponsored and carries the disclosure; the disclosure page flips from the same data.
// Run with `npm run test` (node's built-in runner, no browser, no network).

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  PARTNERS,
  isValidAffiliateUrl,
  getLivePartners,
  partnerBlockModel,
  disclosureStatus,
} from '../affiliate-partners.ts'

const GOOD = 'https://www.partner-network.com/click?pid=8841&sub=quantengines'

describe('isValidAffiliateUrl', () => {
  test('accepts a normal https tracking URL', () => {
    assert.equal(isValidAffiliateUrl(GOOD), true)
  })
  test('rejects empty, missing and whitespace values', () => {
    assert.equal(isValidAffiliateUrl(undefined), false)
    assert.equal(isValidAffiliateUrl(null), false)
    assert.equal(isValidAffiliateUrl(''), false)
    assert.equal(isValidAffiliateUrl('   '), false)
  })
  test('rejects http, javascript:, relative and credentialed URLs', () => {
    assert.equal(isValidAffiliateUrl('http://partner.com/x'), false)
    assert.equal(isValidAffiliateUrl('javascript:alert(1)'), false)
    assert.equal(isValidAffiliateUrl('/go/ibkr'), false)
    assert.equal(isValidAffiliateUrl('https://user:pw@partner.com/x'), false)
  })
  test('rejects localhost, bare IPs and dotless hosts', () => {
    assert.equal(isValidAffiliateUrl('https://localhost/x'), false)
    assert.equal(isValidAffiliateUrl('https://10.0.0.1/x'), false)
    assert.equal(isValidAffiliateUrl('https://intranet/x'), false)
  })
  test('rejects the placeholder ids that used to ship (affiliate=quant2024) and stubs', () => {
    assert.equal(isValidAffiliateUrl('https://broker.com/?affiliate=quant2024'), false)
    assert.equal(isValidAffiliateUrl('https://partner.com/?id=TODO'), false)
    assert.equal(isValidAffiliateUrl('https://example.com/?id=1'), false)
    assert.equal(isValidAffiliateUrl('https://partner.com/?id=your_id'), false)
  })
})

describe('nothing renders without a tracking URL', () => {
  test('empty environment: no live partners, no block, disclosure not live', () => {
    assert.deepEqual(getLivePartners({}), [])
    assert.equal(partnerBlockModel({}), null)
    assert.deepEqual(disclosureStatus({}), { live: false, partnerNames: [] })
  })
  test('invalid values in the environment are ignored', () => {
    const env: Record<string, string> = {}
    for (const p of PARTNERS) env[p.envVar] = 'https://broker.com/?affiliate=quant2024'
    assert.equal(partnerBlockModel(env), null)
    assert.equal(disclosureStatus(env).live, false)
  })
  test('unrelated environment variables never create a partner', () => {
    assert.equal(partnerBlockModel({ NEXT_PUBLIC_BROKER_AFFILIATES_ENABLED: '1', AFFILIATE_URL_UNKNOWN: GOOD }), null)
  })
})

describe('with a tracking URL', () => {
  const env = { AFFILIATE_URL_IBKR: GOOD }
  test('exactly that partner is live', () => {
    const live = getLivePartners(env)
    assert.equal(live.length, 1)
    assert.equal(live[0].id, 'ibkr')
    assert.equal(live[0].url, GOOD)
  })
  test('the link is sponsored, opens safely, is marked, and the disclosure text is present', () => {
    const model = partnerBlockModel(env)
    assert.ok(model)
    assert.equal(model.links.length, 1)
    const l = model.links[0]
    assert.ok(l.rel.split(' ').includes('sponsored'))
    assert.ok(l.rel.split(' ').includes('noopener'))
    assert.equal(l.marker, 'Affiliate link')
    assert.equal(l.url, GOOD)
    assert.match(model.disclosure, /affiliate links/i)
    assert.match(model.disclosure, /commission/i)
    assert.match(model.disclosure, /no extra cost/i)
  })
  test('the disclosure page status flips to live and names the partner', () => {
    assert.deepEqual(disclosureStatus(env), { live: true, partnerNames: ['Interactive Brokers'] })
  })
  test('blurbs make no ratings, bonus, ranking or performance claims', () => {
    for (const p of PARTNERS) {
      assert.doesNotMatch(p.blurb, /best|#1|top|rated|stars?|bonus|\$\d|%|guarantee|free money|returns?/i, p.id)
    }
  })
})

describe('wiring in the source files', () => {
  const here = path.dirname(fileURLToPath(import.meta.url))
  const appDir = path.resolve(here, '..', '..', 'app')
  const compDir = path.resolve(here, '..', '..', 'components')
  test('PartnerBlock returns null when the model is null and never hardcodes a URL', () => {
    const src = fs.readFileSync(path.join(compDir, 'affiliate', 'PartnerBlock.tsx'), 'utf8')
    assert.match(src, /if \(!model\) return null/)
    assert.doesNotMatch(src, /href="https?:/)
  })
  test('the disclosure page derives its status from the same module', () => {
    const src = fs.readFileSync(path.join(appDir, 'affiliate-disclosure', 'page.tsx'), 'utf8')
    assert.match(src, /disclosureStatus\(process\.env\)/)
    assert.match(src, /no affiliate links/)
  })
  test('the data-vendors page renders the block (which renders nothing by default)', () => {
    const src = fs.readFileSync(path.join(appDir, 'data-vendors', 'page.tsx'), 'utf8')
    assert.match(src, /<PartnerBlock \/>/)
  })
})
