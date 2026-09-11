from typing import Dict, Any, List

class FusionEngine:
    """Combines text-based risk, URL-based risk, and domain security risk using confidence weighting."""

    @staticmethod
    def combine_predictions(
        text_risk: float = None, 
        url_risk: float = None, 
        domain_risk: float = None
    ) -> Dict[str, Any]:
        
        risks = []
        weights = []

        if text_risk is not None:
            risks.append(text_risk)
            weights.append(0.40)
        if url_risk is not None:
            risks.append(url_risk)
            weights.append(0.35)
        if domain_risk is not None:
            risks.append(domain_risk)
            weights.append(0.25)

        if not risks:
            final_risk = 0.0
        else:
            total_w = sum(weights)
            norm_weights = [w / total_w for w in weights]
            final_risk = sum(r * w for r, w in zip(risks, norm_weights))

        # Max risk override rule if URL or Domain is extremely high risk (>= 90%)
        if (url_risk and url_risk >= 90) or (domain_risk and domain_risk >= 90):
            final_risk = max(final_risk, 88.0)

        final_risk = round(min(max(final_risk, 0.0), 99.9), 1)

        if final_risk >= 75.0:
            prediction = "PHISHING"
            confidence = round(min(85.0 + (final_risk * 0.14), 99.0), 1)
        elif final_risk >= 40.0:
            prediction = "SUSPICIOUS"
            confidence = round(70.0 + (final_risk * 0.3), 1)
        else:
            prediction = "SAFE"
            confidence = 96.5

        return {
            "prediction": prediction,
            "risk_score": final_risk,
            "confidence": confidence
        }
