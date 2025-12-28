import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.inference import InferenceCollector
from agent.decision import DecisionAgent
from agent.storage import StorageManager
from api.models import (
    InferenceRequest,
    InferenceResponse,
    Detection,
    DecisionInfo
)

router = APIRouter(prefix="/inference", tags=["inference"])

inference_collector = InferenceCollector()
decision_agent = DecisionAgent()
storage_manager = StorageManager()


@router.post("", response_model=InferenceResponse)
async def run_inference(
    file: Optional[UploadFile] = File(None),
    image_path: Optional[str] = Form(None)
):
    try:
        if file is None and image_path is None:
            raise HTTPException(status_code=400, detail="必须提供文件或图片路径")
        
        if file is not None:
            temp_dir = Path("data/temp")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_file_path = temp_dir / file.filename
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            image_path_to_use = str(temp_file_path)
        else:
            image_path_to_use = image_path
        
        detection_result = inference_collector.predict_single(image_path_to_use)
        
        if not detection_result or not detection_result.get('detections'):
            return InferenceResponse(
                success=False,
                message="未检测到任何目标"
            )
        
        decision = decision_agent.decide(detection_result)
        
        storage_manager.save_detection_result(image_path_to_use, detection_result, decision)
        
        detections = [
            Detection(
                cls=d['cls'],
                conf=d['conf'],
                bbox=d['bbox']
            )
            for d in detection_result['detections']
        ]
        
        decisions = [
            DecisionInfo(
                action=d['action'],
                confidence=d['confidence']
            )
            for d in decision['decisions']
        ]
        
        return InferenceResponse(
            success=True,
            data={
                "image_path": image_path_to_use,
                "detections": [d.dict() for d in detections],
                "decisions": [d.dict() for d in decisions]
            }
        )
        
    except Exception as e:
        return InferenceResponse(
            success=False,
            message=f"推理失败: {str(e)}"
        )


@router.post("/batch", response_model=InferenceResponse)
async def run_batch_inference(files: List[UploadFile] = File(...)):
    try:
        results = []
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            temp_file_path = temp_dir / file.filename
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            try:
                detection_result = inference_collector.predict_single(str(temp_file_path))
                
                if detection_result and detection_result.get('detections'):
                    decision = decision_agent.decide(detection_result)
                    storage_manager.save_detection_result(str(temp_file_path), detection_result, decision)
                    
                    detections = [
                        Detection(
                            cls=d['cls'],
                            conf=d['conf'],
                            bbox=d['bbox']
                        )
                        for d in detection_result['detections']
                    ]
                    
                    decisions = [
                        DecisionInfo(
                            action=d['action'],
                            confidence=d['confidence']
                        )
                        for d in decision['decisions']
                    ]
                    
                    results.append({
                        "image_path": file.filename,
                        "success": True,
                        "detections": [d.dict() for d in detections],
                        "decisions": [d.dict() for d in decisions]
                    })
                else:
                    results.append({
                        "image_path": file.filename,
                        "success": False,
                        "message": "未检测到任何目标"
                    })
                    
            except Exception as e:
                results.append({
                    "image_path": file.filename,
                    "success": False,
                    "message": str(e)
                })
        
        return InferenceResponse(
            success=True,
            data={
                "results": results,
                "total": len(results),
                "successful": sum(1 for r in results if r.get('success'))
            }
        )
        
    except Exception as e:
        return InferenceResponse(
            success=False,
            message=f"批量推理失败: {str(e)}"
        )
