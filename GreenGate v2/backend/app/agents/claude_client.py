from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger("sustaingate.claude")


class ClaudeClient:
    """Wrapper around the configured LLM SDK for governed AI completions.

    Despite the class name, this client can run against Anthropic or OpenAI.
    Keeping the class name avoids broad refactors and makes provider swaps easy.
    """

    MODEL = "claude-sonnet-4-6"

    def __init__(
        self,
        anthropic_api_key: str,
        provider: str = "anthropic",
        openai_api_key: str = "",
        openai_model: str = "gpt-4.1-mini",
    ):
        self.provider = (provider or "anthropic").lower()
        self.anthropic_api_key = anthropic_api_key
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self._client = None
        self._backend = "mock"

        if self.provider == "openai" and openai_api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=openai_api_key)
                self._backend = "openai"
            except Exception as e:
                logger.warning("Failed to initialise OpenAI client: %s", e)
        elif anthropic_api_key:
            try:
                import anthropic

                self._client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
                self._backend = "anthropic"
            except Exception as e:
                logger.warning("Failed to initialise Anthropic client: %s", e)

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        policy_constraints: Optional[List[str]] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Send a governed completion request to Claude.

        Appends policy constraints to the system prompt. Falls back to a mock
        response when no API key is configured.
        """
        # Build governed system prompt
        governed_prompt = system_prompt
        if policy_constraints:
            constraints_block = "\n".join(
                f"- {c}" for c in policy_constraints
            )
            governed_prompt += (
                f"\n\n## Governance Constraints\n"
                f"You MUST adhere to the following constraints:\n{constraints_block}"
            )

        if not self._client:
            logger.info("No LLM client configured, returning mock response")
            return self._mock_response(user_message)

        try:
            if self._backend == "openai":
                response = await self._client.responses.create(
                    model=self.openai_model,
                    input=[
                        {"role": "system", "content": governed_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    max_output_tokens=max_tokens,
                )
                return response.output_text

            response = await self._client.messages.create(
                model=self.MODEL,
                max_tokens=max_tokens,
                system=governed_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        except Exception as e:
            logger.error("LLM API call failed: %s", e)
            return self._mock_response(user_message)

    def _mock_response(self, user_message: str) -> str:
        """Generate a structured mock response for development without API key."""
        msg_lower = user_message.lower()

        if "crp" in msg_lower or "carbon reduction" in msg_lower:
            return self._mock_crp_response()
        elif "confidence" in msg_lower or "tier" in msg_lower or "quality" in msg_lower:
            return self._mock_confidence_response()
        elif "framework" in msg_lower or "recommend" in msg_lower:
            return self._mock_framework_recommendation()
        elif "remediation" in msg_lower or "security" in msg_lower:
            return self._mock_remediation_response()
        else:
            return (
                "Based on the analysis of the provided data, the following "
                "observations and recommendations have been identified:\n\n"
                "1. Data quality is generally adequate for baseline reporting.\n"
                "2. Additional data collection is recommended for Scope 3 categories.\n"
                "3. Governance compliance checks have passed with minor warnings.\n\n"
                "Note: This is a mock response generated in development mode. "
                "Configure OPENAI_API_KEY (or ANTHROPIC_API_KEY if using Anthropic) "
                "for production-quality AI outputs."
            )

    def _mock_crp_response(self) -> str:
        return """{
  "title": "Carbon Reduction Plan",
  "version": "1.0",
  "sections": {
    "commitment": "This organisation is committed to achieving Net Zero emissions by 2050, with an interim target of 50% reduction by 2030 against a 2024/25 baseline.",
    "baseline_emissions": {
      "reporting_year": "2024/25",
      "scope1": "Direct emissions from owned/controlled sources",
      "scope2": "Indirect emissions from purchased electricity",
      "scope3": "Other indirect emissions across the value chain"
    },
    "current_emissions": "As per the GHG inventory compiled using the GHG Protocol Corporate Standard with DEFRA 2025 emission factors.",
    "reduction_targets": {
      "near_term": "42% reduction by 2030 (SBTi 1.5C aligned, 4.2% annual linear reduction)",
      "long_term": "Net Zero by 2050"
    },
    "reduction_measures": [
      "Transition to 100% renewable electricity by 2027",
      "Fleet electrification programme: 50% EV by 2028",
      "Energy efficiency improvements in premises (LED, insulation, smart controls)",
      "Supply chain engagement programme targeting top 20 suppliers",
      "Remote/hybrid working policy reducing commuting emissions",
      "Circular economy principles in procurement",
      "Carbon offsetting for residual emissions (verified schemes only)"
    ],
    "governance": {
      "board_oversight": "Quarterly sustainability committee reviews",
      "director_responsibility": "Chief Operations Officer as named director",
      "monitoring": "Annual GHG inventory with quarterly KPI tracking"
    },
    "ppn006_declaration": "This Carbon Reduction Plan has been completed in accordance with PPN 06/21 and associated guidance and reporting standard for Carbon Reduction Plans."
  },
  "director_sign_off_required": true
}"""

    def _mock_confidence_response(self) -> str:
        return """{
  "assessment": [
    {"category": "Electricity", "tier": "high", "reason": "Direct meter readings from utility bills, monthly data"},
    {"category": "Natural gas", "tier": "high", "reason": "Direct meter readings, verified invoices"},
    {"category": "Company vehicles", "tier": "medium", "reason": "Fuel card data, some estimated mileage"},
    {"category": "Business travel", "tier": "medium", "reason": "Expense claims data, rail booking records"},
    {"category": "Employee commuting", "tier": "low", "reason": "Based on annual survey, limited sample size"},
    {"category": "Purchased goods", "tier": "estimated", "reason": "Spend-based estimates using DEFRA factors"},
    {"category": "Waste", "tier": "medium", "reason": "Waste contractor reports, limited composition data"},
    {"category": "Water", "tier": "high", "reason": "Metered water supply data from utility bills"}
  ],
  "overall_quality": "medium",
  "recommendations": [
    "Install sub-meters for major energy consuming equipment",
    "Implement digital mileage tracking for company vehicles",
    "Conduct more frequent commuting surveys with better coverage",
    "Engage key suppliers for product-level carbon data"
  ]
}"""

    def _mock_framework_recommendation(self) -> str:
        return """{
  "recommended_frameworks": [
    {
      "name": "GHG Protocol Corporate Standard",
      "priority": "essential",
      "reason": "Foundation for all emissions reporting. Required for SBTi and CDP."
    },
    {
      "name": "PPN 006",
      "priority": "high",
      "reason": "Mandatory for UK government contracts over GBP 5 million."
    },
    {
      "name": "SBTi",
      "priority": "high",
      "reason": "Science-based targets demonstrate credible commitment to 1.5C pathway."
    },
    {
      "name": "CDP",
      "priority": "medium",
      "reason": "Provides stakeholder visibility and benchmarking against peers."
    },
    {
      "name": "NHS Evergreen",
      "priority": "conditional",
      "reason": "Required if supplying to NHS. Growing requirement across healthcare."
    }
  ],
  "recommended_sequence": "Start with GHG Protocol baseline (Gate 1), then PPN 006 CRP (Gate 2), followed by SBTi commitment."
}"""

    def _mock_remediation_response(self) -> str:
        return """{
  "remediation_plan": [
    {
      "area": "Access Control",
      "finding": "No multi-factor authentication on critical systems",
      "severity": "high",
      "recommendation": "Implement MFA for all admin accounts and remote access within 30 days",
      "effort": "medium",
      "timeline": "30 days"
    },
    {
      "area": "Data Protection",
      "finding": "Data classification policy not formally documented",
      "severity": "medium",
      "recommendation": "Document and implement a 4-tier data classification scheme",
      "effort": "low",
      "timeline": "14 days"
    },
    {
      "area": "Incident Response",
      "finding": "No documented incident response procedure",
      "severity": "high",
      "recommendation": "Develop IR plan covering detection, response, recovery, and reporting",
      "effort": "medium",
      "timeline": "30 days"
    },
    {
      "area": "Supplier Management",
      "finding": "No security requirements in supplier contracts",
      "severity": "medium",
      "recommendation": "Add security clauses to standard supplier agreements and conduct annual reviews",
      "effort": "medium",
      "timeline": "60 days"
    }
  ],
  "priority_order": "Address high-severity findings first. MFA and IR plan are the most critical."
}"""
