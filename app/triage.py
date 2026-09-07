from __future__ import annotations

# These strings are intentionally small and transparent. They are examples of
# coarse scanner heuristics, not authoritative attribution.
SCANNER_MARKERS = (
    "proofpoint",
    "mimecast",
    "safelinks",
    "urlscan",
    "virustotal",
    "curl/",
    "wget/",
)


def classify(user_agent: str, configured_severity: str = "high") -> tuple[str, str]:
    ua = (user_agent or "").lower()
    if any(marker in ua for marker in SCANNER_MARKERS):
        return "Possible automated scanner interaction", "medium"
    return "Honeytoken trigger - potential unauthorized access", configured_severity
