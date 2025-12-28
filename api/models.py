from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DecisionAction(str, Enum):
    auto_accept = "auto_accept"
    send_to_review = "send_to_review"
    discard = "discard"


class ReviewAction(str, Enum):
    accepted = "accepted"
    rejected = "rejected"
    modified = "modified"


class BBox(BaseModel):
    x: float
    y: float
    w: float
    h: float


class Detection(BaseModel):
    cls: str = Field(..., description="类别名称")
    conf: float = Field(..., ge=0.0, le=1.0, description="置信度")
    bbox: List[float] = Field(..., min_length=4, max_length=4, description="边界框 [x, y, w, h]")


class DecisionInfo(BaseModel):
    action: DecisionAction = Field(..., description="决策动作")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")


class InferenceRequest(BaseModel):
    image_path: Optional[str] = Field(None, description="图片路径（用于测试）")


class InferenceResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class ReviewQueueItem(BaseModel):
    sample_id: int
    image_path: str
    detection_id: int
    class_name: str
    confidence: float
    bbox: List[float]
    decision_action: str


class ReviewQueueResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class ReviewRequest(BaseModel):
    reviewer: str = Field(..., description="审核人员")
    action: ReviewAction = Field(..., description="审核动作")
    modified_bbox: Optional[BBox] = Field(None, description="修改后的边界框")


class ReviewResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class StatisticsResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
