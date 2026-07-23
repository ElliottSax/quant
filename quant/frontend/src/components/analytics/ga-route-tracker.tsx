"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";

/**
 * Sends a GA4 pageview on client-side route changes.
 *
 * The initial pageview is already sent by gtag's `config` (send_page_view: true)
 * in the root layout, so the first effect run is skipped to avoid double
 * counting. Without this, only full page loads were tracked and internal
 * navigation went uncounted.
 */
export function GaRouteTracker() {
  const pathname = usePathname();
  const isFirst = useRef(true);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (isFirst.current) {
      isFirst.current = false;
      return;
    }
    const gtag = (window as unknown as { gtag?: (...a: unknown[]) => void }).gtag;
    if (typeof gtag !== "function") return;
    gtag("event", "page_view", {
      page_path: pathname,
      page_location: window.location.href,
      page_title: document.title,
    });
  }, [pathname]);

  return null;
}
