from dataclasses import dataclass, asdict

SCANNER_MARKERS = ("proofpoint", "mimecast", "safelinks", "urlscan", "virustotal", "curl/", "wget/")


@dataclass(frozen=True)
class TriageResult:
    classification: str
    severity: str
    is_scanner: bool
    reason: str
    recommended_action: str

    def fields(self) -> dict:
        return asdict(self)


def classify(user_agent: str, configured_severity: str = "high") -> TriageResult:
    if any(marker in (user_agent or "").lower() for marker in SCANNER_MARKERS):
        return TriageResult("automated_scanner", "medium", True,
                            "User-Agent matched a scanner or command-line client heuristic.", "review")
    return TriageResult("honeytoken_access", configured_severity, False,
                        "Active honeytoken retrieved; no scanner marker matched. User-Agent is not proof of a human viewer.",
                        "investigate")
