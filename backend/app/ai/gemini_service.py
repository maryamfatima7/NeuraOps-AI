import json
import os
from typing import Any

import httpx

from app.core.config import get_settings


class GeminiService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    async def analyze_incident(self, incident_context: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            return {
                "summary": "AI analysis unavailable because no Gemini API key is configured.",
                "suspected_root_cause": "Potential dependency degradation or traffic surge; verification pending.",
                "confidence": 0.0,
                "evidence": ["Missing API credential prevented live LLM analysis."],
                "affected_components": incident_context.get("affected_services", []),
                "recommended_actions": [
                    "Verify telemetry integrity and dashboard status.",
                    "Check dependency health and recent deployments.",
                    "Correlate logs with service latency and error spikes.",
                ],
                "investigation_steps": [
                    "Review service and dependency health.",
                    "Inspect recent anomaly and log timeline.",
                    "Confirm if the issue is caused by a recent change or saturation event.",
                ],
            }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "You are an incident analysis assistant. Use only observed evidence and clearly label uncertainty. "
                                "Return valid JSON with keys: summary, suspected_root_cause, confidence, evidence, affected_components, "
                                "recommended_actions, investigation_steps. Do not claim facts beyond the evidence."
                                f"\nContext: {json.dumps(incident_context, default=str)}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                cleaned = text.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(cleaned)
                return {
                    "summary": parsed.get("summary", "AI analysis produced no summary."),
                    "suspected_root_cause": parsed.get("suspected_root_cause", "Root cause remains uncertain."),
                    "confidence": float(parsed.get("confidence", 0.0)),
                    "evidence": parsed.get("evidence", []),
                    "affected_components": parsed.get("affected_components", incident_context.get("affected_services", [])),
                    "recommended_actions": parsed.get("recommended_actions", []),
                    "investigation_steps": parsed.get("investigation_steps", []),
                }
        except (KeyError, ValueError, httpx.HTTPError, TimeoutError):
            return {
                "summary": "AI analysis failed; using local fallback reasoning.",
                "suspected_root_cause": "Observed latency or dependency strain likely contributed to the incident; confirmation required.",
                "confidence": 0.4,
                "evidence": ["External AI request failed or returned malformed output."],
                "affected_components": incident_context.get("affected_services", []),
                "recommended_actions": [
                    "Validate external AI connectivity and credentials.",
                    "Review recent deployments and dependency health.",
                    "Inspect error and latency traces in the incident window.",
                ],
                "investigation_steps": [
                    "Check infrastructure and service health.",
                    "Correlate anomalies with recent deployment events.",
                    "Confirm the suspected dependency chain through logs.",
                ],
            }
