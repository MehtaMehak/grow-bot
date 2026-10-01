"""Phase 4: Guardrails — facts-only enforcement for the FAQ assistant.

This module contains reusable guardrail logic that prevents the assistant from:
- Providing investment advice or portfolio recommendations
- Making up answers not found in the sources
- Handling or requesting PII
- Making performance claims or calculating returns

It is designed to be imported and used by Phase 5 (Retrieval + LLM Answer).
"""

import re

# ============================================================================
# Constants
# ============================================================================

EDUCATIONAL_SOURCE_LINK = "https://www.hdfcfund.com/mutual-fund/education"

REFUSAL_OPINION_TEMPLATE = (
    "I can only provide factual information about HDFC mutual fund schemes "
    "and cannot offer investment advice or recommendations. "
    "For educational resources on mutual funds, visit: {link}"
)

REFUSAL_OFF_TOPIC_TEMPLATE = (
    "I can only answer factual questions about the five HDFC mutual fund schemes "
    "in my knowledge base (Large Cap, Flexi Cap, ELSS Tax Saver, Small Cap, "
    "and Balanced Advantage). Your question appears to be outside this scope."
)

REFUSAL_PII_TEMPLATE = (
    "I cannot process or store personal information such as PAN, Aadhaar, "
    "account numbers, OTPs, email addresses, or phone numbers. "
    "Please do not share any PII. I can only answer factual questions "
    "about HDFC mutual fund schemes."
)

NO_ANSWER_TEMPLATE = "I don't know based on the available sources."

# ============================================================================
# Opinion-Based Question Detection (G1, G2)
# ============================================================================

OPINION_PATTERNS = [
    r"\bshould\s+i\s+(buy|sell|invest|put\s+money|allocate|switch|redeem)\b",
    r"\b(is|are)\s+it\s+(good|bad|worth|wise|safe|risky)\s+to\s+(invest|buy|put)\b",
    r"\b(can|could|would|should)\s+i\s+invest\b",
    r"\b(should|can|could|would|is\s+it\s+ok(?:ay)?)\s+to\s+(buy|sell|invest|put)\b",
    r"\bwhat\s+(should|would|could)\s+i\s+(buy|sell|invest|do)\b",
    r"\b(which|what)\s+fund\s+(should|would|could)\s+i\s+(pick|choose|select|buy|invest)\b",
    r"\b(is|are)\s+(this|that|these|those)\s+(fund|scheme|mutual\s+fund)\s+(good|bad|worth|wise)\b",
    r"\bshould\s+i\s+(go\s+for|opt\s+for|prefer)\b",
    r"\b(is|are)\s+it\s+a\s+good\s+(time|idea)\s+to\s+(invest|buy|enter)\b",
    r"\bhow\s+much\s+should\s+i\s+(invest|put|allocate)\b",
    r"\bwhat\s+is\s+the\s+best\s+(fund|scheme|mutual\s+fund)\s+to\b",
    r"\bwhich\s+(fund|scheme|mutual\s+fund)\s+is\s+(best|better|top)\b",
    r"\bshould\s+i\s+(start|stop|increase|decrease|pause|continue)\s+(my\s+)?(sip|investment)\b",
    r"\b(is|are)\s+my\s+(portfolio|investments?|allocations?)\s+(good|bad|ok(?:ay)?|balanced)\b",
    r"\bshould\s+i\s+(rebalance|reallocate|diversify|consolidate)\b",
    r"\bcan\s+you\s+(recommend|suggest|advise)\b",
    r"\bwhat\s+do\s+you\s+(recommend|suggest|advise)\b",
    r"\bgive\s+me\s+(a\s+)?(recommendation|suggestion|advice)\b",
    r"\bwhich\s+(one|fund|scheme)\s+(should|would|could)\s+i\s+(go\s+for|pick|choose)\b",
    r"\bworth\s+(investing|buying|putting)\s+(in|into)\b",
    r"\bgood\s+(investment|pick|choice|option)\b",
    r"\b(is|are)\s+it\s+profitable\b",
    r"\bwill\s+i\s+(make|earn|get)\s+(money|profit|returns?)\b",
    r"\bhow\s+much\s+(money|profit|returns?)\s+will\s+i\s+(make|earn|get)\b",
    r"\bwhat\s+will\s+be\s+my\s+(returns?|profit|gains?)\b",
    r"\bguaranteed\s+(returns?|profit|gains?|income)\b",
    r"\bcan\s+i\s+(make|earn|get)\s+(money|profit|returns?)\s+from\b",
    r"\b(is|are)\s+it\s+a\s+safe\s+(investment|bet|option)\b",
    r"\bshould\s+i\s+(enter|exit)\b",
    r"\bwhen\s+should\s+i\s+(buy|sell|enter|exit)\b",
    r"\bwhat\s+should\s+my\s+(portfolio|allocation|investment\s+strategy)\s+be\b",
    r"\bhow\s+should\s+i\s+(allocate|distribute|split)\b",
    r"\bshould\s+i\s+(hold|exit|redeem|withdraw)\b",
    r"\b(is|are)\s+it\s+time\s+to\s+(buy|sell|enter|exit)\b",
    r"\bmarket\s+timing\b",
    r"\bwill\s+(the\s+)?(market|fund|scheme|nav)\s+(go\s+up|go\s+down|rise|fall|crash|recover)\b",
    r"\bwhat\s+will\s+happen\s+to\s+(my|the)\s+(investment|money|fund|scheme)\b",
    r"\bpredict(ion)?\s+(for|about|on)\s+(the\s+)?(market|fund|scheme|returns?)\b",
    r"\bforecast(ing)?\s+(for|about|on)\s+(the\s+)?(market|fund|scheme|returns?)\b",
    r"\bwhat\s+return\s+will\s+i\s+(get|earn|make|receive)\b",
    r"\bwhat\s+will\s+i\s+(earn|get|make)\s+from\b",
    r"\bhow\s+much\s+will\s+i\s+(earn|get|make)\s+from\b",
    r"\bwhat\s+(returns?|profit|gains?)\s+will\s+i\s+(get|earn|make|receive)\b",
    r"\bwhat\s+will\s+be\s+my\s+(returns?|profit|gains?|earnings?)\b",
    r"\bhow\s+much\s+(returns?|profit|gains?|money)\s+will\s+i\s+(get|earn|make)\b",
    r"\bwhat\s+is\s+the\s+expected\s+(return|yield|profit)\b",
    r"\bwhat\s+is\s+the\s+projected\s+(return|yield|profit)\b",
    r"\bhow\s+much\s+can\s+i\s+(earn|get|make)\s+from\b",
    r"\bwhat\s+can\s+i\s+(earn|get|make)\s+from\b",
]

_OPINION_REGEX = [re.compile(p, re.IGNORECASE) for p in OPINION_PATTERNS]


def is_opinion_based(question):
    """Check if the user is asking for investment advice.

    Args:
        question: The user's question string.

    Returns:
        bool: True if the question is opinion-based (seeking advice).
    """
    question_lower = question.lower().strip()
    return any(regex.search(question_lower) for regex in _OPINION_REGEX)


# ============================================================================
# Off-Topic Question Detection
# ============================================================================

IN_TOPIC_KEYWORDS = [
    "hdfc", "mutual fund", "scheme", "nav", "expense ratio", "exit load",
    "sip", "lumpsum", "aum", "asset under management", "fund manager",
    "benchmark", "riskometer", "risk", "lock-in", "lock in", "elss",
    "tax saver", "tax saving", "large cap", "small cap", "mid cap",
    "flexi cap", "balanced advantage", "equity", "debt", "hybrid",
    "portfolio", "holdings", "sector", "allocation", "diversification",
    "dividend", "growth", "direct", "regular", "plan", "statement",
    "account statement", "cas", "consolidated account statement",
    "minimum investment", "minimum sip", "minimum lumpsum",
    "redemption", "repurchase", "switch", "stp", "swp",
    "nfo", "new fund offer", "maturity", "tenure", "duration",
    "yield", "credit risk", "interest rate risk", "liquidity",
    "capital gains", "ltcg", "stcg", "tax", "indexation",
    "nifty", "sensex", "bse", "nse", "amc", "asset management company",
    "kim", "key information memorandum", "sid", "scheme information document",
    "sai", "statement of additional information", "fund facts",
    "groww", "demat", "kyc", "nominee", "nomination",
    "bank account", "ifsc", "mandate", "auto-pay", "standing instruction",
    "load", "entry load", "contingent deferred sales charge",
    "total expense ratio", "ter", "sharpe", "alpha", "beta",
    "standard deviation", "information ratio", "sortino",
    "tracking error", "active share", "number of stocks",
    "credit rating", "maturity profile", "average maturity",
    "macaulay duration", "modified duration", "convexity", "ytm",
    "coupon", "face value", "par value", "premium", "discount",
    "open-ended", "close-ended", "interval fund", "fof", "fund of funds",
    "etf", "index fund", "sectoral", "thematic", "contra", "value",
    "focused", "multi cap", "large & mid cap", "aggressive hybrid",
    "conservative hybrid", "dynamic asset allocation", "arbitrage",
    "overnight fund", "liquid fund", "money market", "short term",
    "medium term", "long term", "ultra short", "children's fund",
    "retirement", "pension", "nps", "systematic", "step-up sip",
    "flexi sip", "trigger", "target", "milestone", "goal-based",
    "fact sheet", "monthly", "quarterly", "annual", "auditor",
    "trustee", "custodian", "registrar", "transfer agent",
    "amfi", "sebi", "irdai", "rbi", "regulation", "compliance",
    "risk-o-meter", "potential risk class", "prc",
    "maximum drawdown", "recovery time", "investment objective",
    "asset allocation", "pattern", "investor", "unit holder",
    "nav history", "nav date", "repurchase price", "sale price",
    "face value", "unit capital", "corpus", "fund size",
    "inception date", "launch date", "date of allotment",
    "benchmark index", "total return index", "tri",
    "comparison", "peer", "category", "quartile", "ranking",
    "minimum application", "minimum additional", "minimum redemption",
    "load structure", "exit load period", "lock-in period",
    "tax treatment", "tax implication", "deduction", "80c",
    "section 80c", "dividend distribution tax", "ddt",
    "surcharge", "cess", "marginal tax rate", "tds",
    "tax deducted at source", "form 16a", "form 26as",
    "capital gains statement", "portfolio disclosure",
    "half yearly", "annual report", "scheme documents",
    "addendum", "modification", "change", "revision", "update",
    "investment strategy", "process", "philosophy", "approach",
    "top 10", "top holdings", "sector allocation", "market cap allocation",
    "debt instruments", "government securities", "g-sec",
    "corporate bonds", "cp", "cd", "ncd", "commercial paper",
    "certificate of deposit", "non convertible debenture",
    "treasury bills", "t-bills", "cash", "money market instruments",
    "repo", "reverse repo", "mibor", "floating rate", "fixed rate",
    "sovereign", "state government", "central government",
    "aaa", "aa", "a", "bbb", "bb", "b", "ccc", "cc", "c", "d",
    "rating agency", "crisil", "icra", "care", "brickwork",
    "india rating", "fitch", "moody's", "s&p",
    "maturity date", "coupon rate", "interest rate",
    "investment objective", "asset allocation", "pattern",
]


def is_off_topic(question):
    """Check if the question is outside the scope of HDFC mutual fund FAQs.

    Args:
        question: The user's question string.

    Returns:
        bool: True if the question is off-topic (no relevant keywords found).
    """
    question_lower = question.lower()
    return not any(keyword in question_lower for keyword in IN_TOPIC_KEYWORDS)


# ============================================================================
# PII Detection (FR6)
# ============================================================================

PII_PATTERNS = [
    (r"\b[A-Z]{5}\d{4}[A-Z]\b", "PAN"),
    (r"\b\d{12}\b", "Aadhaar"),
    (r"\b\d{9,18}\b", "Account number"),
    (r"\b\d{4,8}\b", "OTP"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "Email"),
    (r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b", "Phone number"),
]

_PII_REGEX = [(re.compile(p, re.IGNORECASE), label) for p, label in PII_PATTERNS]


def contains_pii(text):
    """Check if the text contains personally identifiable information (PII).

    Detects: PAN, Aadhaar, account numbers, OTPs, email addresses, phone numbers.

    Args:
        text: The text to check.

    Returns:
        bool: True if any PII is detected.
    """
    return any(regex.search(text) for regex, _ in _PII_REGEX)


def detect_pii_types(text):
    """Return a list of PII types detected in the text.

    Args:
        text: The text to check.

    Returns:
        list[str]: Labels of detected PII types (e.g., ["PAN", "Email"]).
    """
    return [label for regex, label in _PII_REGEX if regex.search(text)]


# ============================================================================
# Relevance Check (G3)
# ============================================================================

RELEVANCE_THRESHOLD = 0.3


def is_relevant(similarities, threshold=RELEVANCE_THRESHOLD):
    """Check if retrieved chunks are relevant enough to answer the question.

    Args:
        similarities: List of cosine similarity scores from ChromaDB.
        threshold: Minimum similarity score to consider relevant.

    Returns:
        bool: True if at least one chunk is relevant.
    """
    if not similarities:
        return False
    return any(score >= threshold for score in similarities)


# ============================================================================
# Response Builders
# ============================================================================

def build_opinion_refusal():
    """Build the polite refusal response for opinion-based questions."""
    return REFUSAL_OPINION_TEMPLATE.format(link=EDUCATIONAL_SOURCE_LINK)


def build_off_topic_refusal():
    """Build the refusal response for off-topic questions."""
    return REFUSAL_OFF_TOPIC_TEMPLATE


def build_pii_refusal():
    """Build the refusal response when PII is detected."""
    return REFUSAL_PII_TEMPLATE


def build_no_answer():
    """Build the 'I don't know' response."""
    return NO_ANSWER_TEMPLATE


# ============================================================================
# Main Guardrail Check (convenience function for Phase 5)
# ============================================================================

def check_guardrails(question, similarities=None):
    """Run all guardrail checks on a user question.

    This is the main entry point for Phase 5. It checks in order:
    1. PII detection
    2. Opinion-based question detection
    3. Off-topic detection
    4. Relevance check (if similarities provided)

    Args:
        question: The user's question string.
        similarities: Optional list of similarity scores from retrieval.

    Returns:
        dict: Result with keys:
            - 'allowed' (bool): True if the question passes all guardrails.
            - 'response' (str or None): Refusal message if not allowed, None if allowed.
            - 'reason' (str or None): Reason for refusal if not allowed.
    """
    # Check 1: PII
    if contains_pii(question):
        return {
            "allowed": False,
            "response": build_pii_refusal(),
            "reason": "pii_detected",
        }

    # Check 2: Opinion-based
    if is_opinion_based(question):
        return {
            "allowed": False,
            "response": build_opinion_refusal(),
            "reason": "opinion_based",
        }

    # Check 3: Off-topic
    if is_off_topic(question):
        return {
            "allowed": False,
            "response": build_off_topic_refusal(),
            "reason": "off_topic",
        }

    # Check 4: Relevance (only if similarities are provided)
    if similarities is not None and not is_relevant(similarities):
        return {
            "allowed": False,
            "response": build_no_answer(),
            "reason": "not_relevant",
        }

    return {
        "allowed": True,
        "response": None,
        "reason": None,
    }
