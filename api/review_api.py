import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.storage import StorageManager
from api.models import (
    ReviewRequest,
    ReviewResponse,
    ReviewQueueResponse,
    ReviewQueueItem
)

router = APIRouter(prefix="/api/review", tags=["review"])

storage_manager = StorageManager()


@router.get("/image/{sample_id}")
async def get_review_image(sample_id: int):
    try:
        queue_items = storage_manager.get_review_queue()
        target_item = None
        for item in queue_items:
            if item['sample_id'] == sample_id:
                target_item = item
                break
        
        if not target_item:
            raise HTTPException(status_code=404, detail=f"未找到样本ID {sample_id}")
        
        config = storage_manager.db._get_connection()
        cursor = config.cursor()
        cursor.execute('SELECT image_path FROM samples WHERE id = ?', (sample_id,))
        result = cursor.fetchone()
        config.close()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到样本ID {sample_id}")
        
        image_name = result[0]
        review_images_dir = storage_manager.base_path / storage_manager.current_version / 'review_queue' / 'images'
        image_path = review_images_dir / image_name
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"图片文件不存在: {image_name}")
        
        return FileResponse(str(image_path))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片失败: {str(e)}")


@router.get("/queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    limit: int = Query(100, ge=1, le=1000, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    try:
        queue_items = storage_manager.get_review_queue(limit)
        
        total = len(queue_items)
        items = queue_items[offset:offset + limit]
        
        formatted_items = [
            ReviewQueueItem(
                sample_id=item['sample_id'],
                image_path=item['image_path'],
                detection_id=item['detection_id'],
                class_name=item['class_name'],
                confidence=item['confidence'],
                bbox=item['bbox'],
                decision_action=item['decision_action']
            )
            for item in items
        ]
        
        return ReviewQueueResponse(
            success=True,
            data={
                "total": total,
                "offset": offset,
                "limit": limit,
                "items": [item.dict() for item in formatted_items]
            }
        )
        
    except Exception as e:
        return ReviewQueueResponse(
            success=False,
            message=f"获取审核队列失败: {str(e)}"
        )


@router.post("/sample/{sample_id}", response_model=ReviewResponse)
async def submit_review_by_sample(sample_id: int, request: ReviewRequest):
    try:
        queue_items = storage_manager.get_review_queue()
        target_items = [item for item in queue_items if item['sample_id'] == sample_id]
        
        if not target_items:
            return ReviewResponse(
                success=False,
                message=f"未找到样本ID {sample_id} 的待审核项目"
            )
        
        for item in target_items:
            storage_manager.save_review_result(
                detection_id=item['detection_id'],
                reviewer=request.reviewer,
                action=request.action.value,
                modified_bbox=None
            )
        
        if request.action.value in ['accepted', 'modified']:
            storage_manager.move_to_final(
                target_items[0]['image_path'],
                request.action.value
            )
        
        return ReviewResponse(
            success=True,
            data={
                "sample_id": sample_id,
                "action": request.action.value,
                "reviewed_count": len(target_items)
            }
        )
        
    except Exception as e:
        return ReviewResponse(
            success=False,
            message=f"提交审核结果失败: {str(e)}"
        )


@router.post("/{detection_id}", response_model=ReviewResponse)
async def submit_review(detection_id: int, request: ReviewRequest):
    try:
        modified_bbox = None
        if request.modified_bbox:
            modified_bbox = {
                'x': request.modified_bbox.x,
                'y': request.modified_bbox.y,
                'w': request.modified_bbox.w,
                'h': request.modified_bbox.h
            }
        
        review_id = storage_manager.save_review_result(
            detection_id=detection_id,
            reviewer=request.reviewer,
            action=request.action.value,
            modified_bbox=modified_bbox
        )
        
        if request.action.value in ['accepted', 'modified']:
            queue_items = storage_manager.get_review_queue()
            target_item = None
            for item in queue_items:
                if item['detection_id'] == detection_id:
                    target_item = item
                    break
            
            if target_item:
                storage_manager.move_to_final(
                    target_item['image_path'],
                    request.action.value
                )
        
        return ReviewResponse(
            success=True,
            data={
                "review_id": review_id,
                "detection_id": detection_id,
                "action": request.action.value
            }
        )
        
    except Exception as e:
        return ReviewResponse(
            success=False,
            message=f"提交审核结果失败: {str(e)}"
        )


@router.get("/stats", response_model=ReviewResponse)
async def get_review_stats():
    try:
        stats = storage_manager.get_statistics()
        
        return ReviewResponse(
            success=True,
            data={
                "review_stats": stats.get('review_stats', {}),
                "pending_review": stats.get('decision_stats', {}).get('send_to_review', 0)
            }
        )
        
    except Exception as e:
        return ReviewResponse(
            success=False,
            message=f"获取审核统计失败: {str(e)}"
        )
