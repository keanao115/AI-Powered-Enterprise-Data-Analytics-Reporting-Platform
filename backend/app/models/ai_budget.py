from sqlalchemy import Column, String, Float
from app.core.database import Base


class AIBudget(Base):
    __tablename__ = "ai_budgets"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, unique=True, index=True, nullable=False)
    daily_budget_usd = Column(Float, default=50.0)
    current_daily_spend_usd = Column(Float, default=0.0)
    monthly_budget_usd = Column(Float, default=1000.0)
    current_monthly_spend_usd = Column(Float, default=0.0)
    last_reset_date = Column(String, nullable=False)
