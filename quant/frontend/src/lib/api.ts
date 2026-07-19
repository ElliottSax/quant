/**
 * Compatibility shim: several pages import `{ api }` from '@/lib/api', while the
 * implementation lives in './api-client'. Re-export everything so both paths work.
 */
export * from './api-client';
export { api as default } from './api-client';
