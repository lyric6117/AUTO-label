from typing import Dict, Any, List
from enum import Enum
from utils.config_loader import get_config


class DecisionAction(Enum):
    AUTO_ACCEPT = "auto_accept"
    SEND_TO_REVIEW = "send_to_review"
    DISCARD = "discard"


class DecisionAgent:
    def __init__(self):
        config = get_config()
        
        self.auto_accept_threshold = config.decision.get('auto_accept_threshold', 0.85)
        self.review_min_threshold = config.decision.get('review_min_threshold', 0.4)
        self.discard_threshold = config.decision.get('discard_threshold', 0.4)
        
        self.classes = config.model.get('classes', [])
        
        self.statistics = {
            DecisionAction.AUTO_ACCEPT: 0,
            DecisionAction.SEND_TO_REVIEW: 0,
            DecisionAction.DISCARD: 0,
            "by_class": {cls: {
                DecisionAction.AUTO_ACCEPT: 0,
                DecisionAction.SEND_TO_REVIEW: 0,
                DecisionAction.DISCARD: 0
            } for cls in self.classes}
        }

    def decide_single(self, detection: Dict[str, Any]) -> DecisionAction:
        conf = detection.get('conf', 0.0)
        cls = detection.get('cls', 'unknown')
        
        threshold = self._get_class_threshold(cls)
        
        if conf >= threshold:
            action = DecisionAction.AUTO_ACCEPT
        elif self.review_min_threshold <= conf < threshold:
            action = DecisionAction.SEND_TO_REVIEW
        else:
            action = DecisionAction.DISCARD
        
        self._update_statistics(action, cls)
        
        return action

    def decide_batch(self, detections: List[Dict[str, Any]]) -> List[DecisionAction]:
        actions = []
        
        for detection in detections:
            action = self.decide_single(detection)
            actions.append(action)
        
        return actions

    def decide(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        detections = detection_result.get('detections', [])
        
        decisions = []
        for detection in detections:
            action = self.decide_single(detection)
            decisions.append({
                'action': action.value,
                'confidence': detection.get('conf', 0.0)
            })
        
        overall_action = self._determine_overall_action(decisions)
        
        return {
            'decisions': decisions,
            'overall_action': overall_action
        }

    def _determine_overall_action(self, decisions: List[Dict[str, Any]]) -> str:
        if not decisions:
            return 'discard'
        
        actions = [d['action'] for d in decisions]
        
        if 'send_to_review' in actions:
            return 'send_to_review'
        elif 'auto_accept' in actions:
            return 'auto_accept'
        else:
            return 'discard'

    def decide_image(self, image_result: Dict[str, Any]) -> Dict[str, Any]:
        image_name = image_result.get('image', 'unknown')
        detections = image_result.get('detections', [])
        
        decisions = []
        for detection in detections:
            action = self.decide_single(detection)
            decisions.append({
                'detection': detection,
                'action': action.value
            })
        
        image_decision = {
            'image': image_name,
            'decisions': decisions,
            'summary': self._get_image_summary(decisions)
        }
        
        return image_decision

    def decide_images_batch(self, image_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.decide_image(result) for result in image_results]

    def _get_class_threshold(self, cls: str) -> float:
        class_thresholds = {
            'part1_normal': 0.85,
            'part1_fault': 0.85,
            'part2_normal': 0.85,
            'part2_fault': 0.85
        }
        
        return class_thresholds.get(cls, self.auto_accept_threshold)

    def _apply_custom_rules(self, detection: Dict[str, Any]) -> DecisionAction:
        conf = detection.get('conf', 0.0)
        cls = detection.get('cls', 'unknown')
        
        if cls == 'part1_fault' and conf >= 0.80:
            return DecisionAction.AUTO_ACCEPT
        
        return None

    def _update_statistics(self, action: DecisionAction, cls: str):
        self.statistics[action] += 1
        
        if cls in self.statistics['by_class']:
            self.statistics['by_class'][cls][action] += 1

    def _get_image_summary(self, decisions: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {
            DecisionAction.AUTO_ACCEPT.value: 0,
            DecisionAction.SEND_TO_REVIEW.value: 0,
            DecisionAction.DISCARD.value: 0
        }
        
        for decision in decisions:
            action = decision['action']
            summary[action] += 1
        
        return summary

    def get_statistics(self) -> Dict[str, Any]:
        total = sum(self.statistics[action] for action in DecisionAction)
        
        by_class_serializable = {}
        for cls, stats in self.statistics['by_class'].items():
            by_class_serializable[cls] = {
                'auto_accept': stats[DecisionAction.AUTO_ACCEPT],
                'send_to_review': stats[DecisionAction.SEND_TO_REVIEW],
                'discard': stats[DecisionAction.DISCARD]
            }
        
        return {
            'total_detections': total,
            'auto_accept_count': self.statistics[DecisionAction.AUTO_ACCEPT],
            'review_count': self.statistics[DecisionAction.SEND_TO_REVIEW],
            'discard_count': self.statistics[DecisionAction.DISCARD],
            'auto_accept_rate': self.statistics[DecisionAction.AUTO_ACCEPT] / total if total > 0 else 0,
            'review_rate': self.statistics[DecisionAction.SEND_TO_REVIEW] / total if total > 0 else 0,
            'discard_rate': self.statistics[DecisionAction.DISCARD] / total if total > 0 else 0,
            'by_class': by_class_serializable
        }

    def reset_statistics(self):
        self.statistics = {
            DecisionAction.AUTO_ACCEPT: 0,
            DecisionAction.SEND_TO_REVIEW: 0,
            DecisionAction.DISCARD: 0,
            "by_class": {cls: {
                DecisionAction.AUTO_ACCEPT: 0,
                DecisionAction.SEND_TO_REVIEW: 0,
                DecisionAction.DISCARD: 0
            } for cls in self.classes}
        }
