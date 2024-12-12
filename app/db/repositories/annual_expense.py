from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AnnualExpense
from app.db.repositories.expense_articles import BaseExpenseRepository


class MonthlyExpenseRepository(BaseExpenseRepository):
    def __init__(self, session: AsyncSession, model: AnnualExpense):
        super().__init__(session, model)
