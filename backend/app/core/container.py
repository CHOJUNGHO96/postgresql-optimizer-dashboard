"""DI 컨테이너 설정 모듈.

dependency_injector를 사용하여 전체 의존성 그래프를 관리한다.
"""

from dependency_injector import containers, providers

from app.application.ai_optimization.use_cases import (
    CreateOptimizationTaskUseCase,
    GetOptimizationTaskUseCase,
    GetOptimizationUseCase,
    GetOptimizationsUseCase,
    OptimizeQueryUseCase,
    ProcessOptimizationTaskUseCase,
)
from app.application.query_analysis.use_cases import (
    AnalyzePlanUseCase,
    AnalyzeQueryUseCase,
    GetQueryPlanUseCase,
    ListQueryPlansUseCase,
)
from app.core.config import Settings
from app.core.database import create_engine, create_session_factory
from app.core.model_configs import get_model_limits
from app.infrastructure.ai_optimization.clients import (
    ClaudeAIClient,
    GeminiAIClient,
    GLMAIClient,
)
from app.infrastructure.ai_optimization.repositories import (
    SQLAlchemyAIOptimizationRepository,
)
from app.infrastructure.query_analysis.repositories import (
    SQLAlchemyQueryAnalysisRepository,
)


# ─── Helper functions for timeout configuration ───
def get_claude_timeout(model: str) -> int:
    """Get timeout for Claude model."""
    return get_model_limits(model).timeout_seconds


def get_glm_timeout(model: str) -> int:
    """Get timeout for GLM model."""
    return get_model_limits(model).timeout_seconds


def get_gemini_timeout(model: str) -> int:
    """Get timeout for Gemini model."""
    return get_model_limits(model).timeout_seconds


class Container(containers.DeclarativeContainer):
    """애플리케이션 DI 컨테이너.

    presentation 모듈에만 주입하여 계층 분리를 유지한다.
    """

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.presentation.query_analysis.router",
            "app.presentation.ai_optimization.router",
        ]
    )

    # ─── 설정 ───
    config = providers.Singleton(Settings)

    # ─── 내부 DB (분석 결과 저장용) ───
    db_engine = providers.Singleton(
        create_engine,
        database_url=config.provided.DATABASE_URL,
        schema=config.provided.DB_SCHEMA,
    )

    db_session_factory = providers.Singleton(
        create_session_factory,
        engine=db_engine,
    )

    # ─── 대상 DB (EXPLAIN 실행용) ───
    target_db_engine = providers.Singleton(
        create_engine,
        database_url=config.provided.TARGET_DATABASE_URL,
        schema=config.provided.TARGET_DB_SCHEMA,
    )

    target_db_session_factory = providers.Singleton(
        create_session_factory,
        engine=target_db_engine,
    )

    # ─── 리포지토리 ───
    query_analysis_repository = providers.Factory(
        SQLAlchemyQueryAnalysisRepository,
        session_factory=db_session_factory,
        target_session_factory=target_db_session_factory,
    )

    ai_optimization_repository = providers.Factory(
        SQLAlchemyAIOptimizationRepository,
        session_factory=db_session_factory,
    )

    # ─── 유스케이스 ───
    analyze_query_use_case = providers.Factory(
        AnalyzeQueryUseCase,
        repository=query_analysis_repository,
    )

    analyze_plan_use_case = providers.Factory(
        AnalyzePlanUseCase,
        repository=query_analysis_repository,
    )

    get_query_plan_use_case = providers.Factory(
        GetQueryPlanUseCase,
        repository=query_analysis_repository,
    )

    list_query_plans_use_case = providers.Factory(
        ListQueryPlansUseCase,
        repository=query_analysis_repository,
    )

    # ─── AI 클라이언트 (모델별 최적화된 타임아웃) ───
    claude_client = providers.Singleton(
        ClaudeAIClient,
        api_key=config.provided.CLAUDE_API_KEY,
        model_name=config.provided.CLAUDE_MODEL,
        timeout=providers.Factory(
            get_claude_timeout,
            model=config.provided.CLAUDE_MODEL,
        ),
    )

    glm_client = providers.Singleton(
        GLMAIClient,
        api_key=config.provided.GLM_API_KEY,
        model_name=config.provided.GLM_MODEL,
        timeout=providers.Factory(
            get_glm_timeout,
            model=config.provided.GLM_MODEL,
        ),
    )

    gemini_client = providers.Singleton(
        GeminiAIClient,
        api_key=config.provided.GEMINI_API_KEY,
        model_name=config.provided.GEMINI_MODEL,
        timeout=providers.Factory(
            get_gemini_timeout,
            model=config.provided.GEMINI_MODEL,
        ),
    )

    ai_clients = providers.Dict(
        claude=claude_client,
        glm=glm_client,
        gemini=gemini_client,
    )

    # ─── AI 최적화 유스케이스 ───
    optimize_query_use_case = providers.Factory(
        OptimizeQueryUseCase,
        query_repo=query_analysis_repository,
        optimization_repo=ai_optimization_repository,
        ai_clients=ai_clients,
        target_session_factory=target_db_session_factory,
    )

    get_optimizations_use_case = providers.Factory(
        GetOptimizationsUseCase,
        optimization_repo=ai_optimization_repository,
    )

    get_optimization_use_case = providers.Factory(
        GetOptimizationUseCase,
        optimization_repo=ai_optimization_repository,
    )

    # ─── AI 최적화 작업 관리 유스케이스 ───
    create_optimization_task_use_case = providers.Factory(
        CreateOptimizationTaskUseCase,
        repository=ai_optimization_repository,
    )

    get_optimization_task_use_case = providers.Factory(
        GetOptimizationTaskUseCase,
        repository=ai_optimization_repository,
    )

    process_optimization_task_use_case = providers.Factory(
        ProcessOptimizationTaskUseCase,
        task_repo=ai_optimization_repository,
        optimize_use_case=optimize_query_use_case,
    )
