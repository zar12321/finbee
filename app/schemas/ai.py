from typing import Optional
from typing import List

from pydantic import BaseModel
from pydantic import Field


# =====================================================
# CHAT REQUEST
# =====================================================

class AIChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=5000
    )


# =====================================================
# CHAT RESPONSE
# =====================================================

class AIChatResponse(BaseModel):

    response: str

    provider: str


# =====================================================
# CHAT HISTORY
# =====================================================

class AIChatMessage(BaseModel):

    role: str

    content: str


# =====================================================
# AI SETTINGS
# =====================================================

class AISettings(BaseModel):

    provider: str

    model_name: Optional[str] = None

    temperature: float = 0.7

    max_tokens: int = 1000


# =====================================================
# FINANCIAL SUMMARY
# =====================================================

class FinancialSummary(BaseModel):

    total_income: float = 0

    total_expense: float = 0

    total_topup: float = 0

    balance: float = 0

    top_categories: List[str] = []

    transaction_count: int = 0


# =====================================================
# AI ANALYSIS REQUEST
# =====================================================

class AIAnalysisRequest(BaseModel):

    summary: FinancialSummary

    user_question: Optional[str] = None


# =====================================================
# AI ANALYSIS RESPONSE
# =====================================================

class AIAnalysisResponse(BaseModel):

    insight: str

    recommendation: str

    risk_level: str

    provider: str