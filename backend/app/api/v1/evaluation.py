from fastapi import APIRouter, Depends

from app.core.permissions import Permission
from app.core.security import require_permission
from app.core.tenant import TenantContext

eval_router = APIRouter(prefix="/evaluation", tags=["Evaluation Benchmark"])


@eval_router.post("/run")
async def run_evaluation_benchmark(
    ctx: TenantContext = Depends(require_permission(Permission.EVALUATION_RUN)),
):
    from app.evaluation.eval_runner import evaluation_runner

    res = evaluation_runner.run_all_benchmarks(ctx)
    return res
