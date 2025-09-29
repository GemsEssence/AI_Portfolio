from typing import Dict, Any
from src.pipeline import abuse, crisis
from src.pipeline.escalation import EscalationDetector
from src.pipeline.content_filter import infer as cf_infer

class SafetyOrchestrator:
    def __init__(self, user_age: int = 16):
        self.user_age = user_age
        self.escalation = EscalationDetector()
        # lazy-loaded models
        self._abuse_model = None
        self._crisis_model = None

    def run_abuse(self, text: str) -> Dict[str, Any]:
        if self._abuse_model is None:
            self._abuse_model = abuse.load()
        return abuse.infer(text, self._abuse_model)

    def run_crisis(self, text: str) -> Dict[str, Any]:
        if self._crisis_model is None:
            self._crisis_model = crisis.load()
        return crisis.infer(text, self._crisis_model)

    def step(self, text: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        out["abuse"] = self.run_abuse(text)
        out["crisis"] = self.run_crisis(text)
        out["escalation"] = self.escalation.update(text)
        out["content_filter"] = cf_infer(text, self.user_age)

        # Policy routing
        action = "allow"
        reasons = []

        if out["crisis"]["label"] in {"self_harm", "suicidal_ideation"}:
            action = "escalate_to_human"
            reasons.append("crisis")

        if out["abuse"]["label"] in {"abusive", "threat"}:
            action = "warn" if action == "allow" else action
            reasons.append("abuse")

        if out["content_filter"]["label"] == "block":
            action = "block"
            reasons.append("age_block")
        elif out["content_filter"]["label"] == "warn" and action == "allow":
            action = "warn"
            reasons.append("age_warn")

        out["action"] = {"label": action, "details": ", ".join(reasons) or "-"}
        return out
