import sys
from pathlib import Path
from fastapi import APIRouter

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.storage import StorageManager
from api.models import StatisticsResponse

router = APIRouter(prefix="/api/stats", tags=["statistics"])

storage_manager = StorageManager()


@router.get("", response_model=StatisticsResponse)
async def get_statistics():
    try:
        stats = storage_manager.get_statistics()
        
        return StatisticsResponse(
            success=True,
            data={
                "total_samples": stats.get('total_samples', 0),
                "total_detections": stats.get('total_detections', 0),
                "decision_stats": stats.get('decision_stats', {}),
                "review_stats": stats.get('review_stats', {})
            }
        )
        
    except Exception as e:
        return StatisticsResponse(
            success=False,
            message=f"获取统计信息失败: {str(e)}"
        )


@router.get("/decision", response_model=StatisticsResponse)
async def get_decision_stats():
    try:
        stats = storage_manager.get_statistics()
        
        return StatisticsResponse(
            success=True,
            data={
                "decision_stats": stats.get('decision_stats', {})
            }
        )
        
    except Exception as e:
        return StatisticsResponse(
            success=False,
            message=f"获取决策统计失败: {str(e)}"
        )


@router.get("/review", response_model=StatisticsResponse)
async def get_review_stats():
    try:
        stats = storage_manager.get_statistics()
        
        return StatisticsResponse(
            success=True,
            data={
                "review_stats": stats.get('review_stats', {})
            }
        )
        
    except Exception as e:
        return StatisticsResponse(
            success=False,
            message=f"获取审核统计失败: {str(e)}"
        )
