import sqlite3
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.config_loader import get_config


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        config = get_config()
        
        if db_path is None:
            db_path = config.storage.get('db_path', 'data/agent.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()

    def _init_db(self):
        conn = self._get_connection()
        self._create_tables(conn)
        conn.close()

    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self, conn):
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                dataset_version TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id INTEGER NOT NULL,
                class_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                bbox_x REAL NOT NULL,
                bbox_y REAL NOT NULL,
                bbox_w REAL NOT NULL,
                bbox_h REAL NOT NULL,
                decision_action TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sample_id) REFERENCES samples (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id INTEGER NOT NULL,
                reviewer TEXT,
                action TEXT NOT NULL,
                modified_bbox TEXT,
                reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (detection_id) REFERENCES detections (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_name TEXT UNIQUE NOT NULL,
                parent_version TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

    def insert_sample(self, image_path: str, dataset_version: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO samples (image_path, dataset_version)
            VALUES (?, ?)
        ''', (image_path, dataset_version))
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    def insert_detection(self, sample_id: int, detection: Dict[str, Any], decision_action: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections (sample_id, class_name, confidence, bbox_x, bbox_y, bbox_w, bbox_h, decision_action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sample_id,
            detection['cls'],
            detection['conf'],
            detection['bbox'][0],
            detection['bbox'][1],
            detection['bbox'][2],
            detection['bbox'][3],
            decision_action
        ))
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    def insert_review(self, detection_id: int, reviewer: str, action: str, modified_bbox: Optional[Dict] = None) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        modified_bbox_json = json.dumps(modified_bbox) if modified_bbox else None
        cursor.execute('''
            INSERT INTO reviews (detection_id, reviewer, action, modified_bbox)
            VALUES (?, ?, ?, ?)
        ''', (detection_id, reviewer, action, modified_bbox_json))
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    def insert_version(self, version_name: str, parent_version: Optional[str] = None, description: str = "") -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO versions (version_name, parent_version, description)
            VALUES (?, ?, ?)
        ''', (version_name, parent_version, description))
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    def get_review_queue(self, limit: int = 100) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, s.image_path, d.id, d.class_name, d.confidence, 
                   d.bbox_x, d.bbox_y, d.bbox_w, d.bbox_h, d.decision_action
            FROM samples s
            JOIN detections d ON s.id = d.sample_id
            WHERE d.decision_action = 'send_to_review'
            AND NOT EXISTS (
                SELECT 1 FROM reviews r WHERE r.detection_id = d.id
            )
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                'sample_id': row[0],
                'image_path': row[1],
                'detection_id': row[2],
                'class_name': row[3],
                'confidence': row[4],
                'bbox': [row[5], row[6], row[7], row[8]],
                'decision_action': row[9]
            })
        conn.close()
        return results

    def get_statistics(self) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM samples')
        total_samples = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM detections')
        total_detections = cursor.fetchone()[0]
        
        cursor.execute('SELECT decision_action, COUNT(*) FROM detections GROUP BY decision_action')
        decision_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute('SELECT action, COUNT(*) FROM reviews GROUP BY action')
        review_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_samples': total_samples,
            'total_detections': total_detections,
            'decision_stats': decision_stats,
            'review_stats': review_stats
        }


class StorageManager:
    def __init__(self):
        config = get_config()
        self.base_path = Path(config.storage.get('base_path', 'dataset'))
        self.current_version = config.storage.get('current_version', 'v1_auto')
        self.db = DatabaseManager()
        
        self._ensure_directories()

    def _ensure_directories(self):
        directories = [
            self.base_path / self.current_version / 'auto_accept' / 'images',
            self.base_path / self.current_version / 'auto_accept' / 'labels',
            self.base_path / self.current_version / 'human_fix' / 'images',
            self.base_path / self.current_version / 'human_fix' / 'labels',
            self.base_path / self.current_version / 'review_queue' / 'images',
            self.base_path / self.current_version / 'review_queue' / 'detections',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def save_detection_result(self, image_path: str, detection_result: Dict[str, Any], decision: Dict[str, Any]):
        image_name = Path(image_path).name
        sample_id = self.db.insert_sample(image_name, self.current_version)
        
        for detection, decision_info in zip(detection_result['detections'], decision['decisions']):
            detection_id = self.db.insert_detection(sample_id, detection, decision_info['action'])
            
            if decision_info['action'] == 'send_to_review':
                self._copy_to_review_queue(image_path, detection_result, detection_id)

    def _copy_to_review_queue(self, image_path: str, detection_result: Dict[str, Any], detection_id: int):
        review_images_dir = self.base_path / self.current_version / 'review_queue' / 'images'
        review_detections_dir = self.base_path / self.current_version / 'review_queue' / 'detections'
        
        image_name = Path(image_path).name
        dest_image_path = review_images_dir / image_name
        
        if Path(image_path).exists():
            shutil.copy2(image_path, dest_image_path)
        
        detection_json_name = f"{Path(image_name).stem}_det{detection_id}.json"
        detection_json_path = review_detections_dir / detection_json_name
        
        with open(detection_json_path, 'w', encoding='utf-8') as f:
            json.dump(detection_result, f, indent=2, ensure_ascii=False)

    def save_review_result(self, detection_id: int, reviewer: str, action: str, modified_bbox: Optional[Dict] = None):
        self.db.insert_review(detection_id, reviewer, action, modified_bbox)

    def get_review_queue(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.db.get_review_queue(limit)

    def move_to_final(self, image_path: str, action: str):
        image_name = Path(image_path).name
        review_image_path = self.base_path / self.current_version / 'review_queue' / 'images' / image_name
        
        if action == 'accepted':
            dest_dir = self.base_path / self.current_version / 'auto_accept' / 'images'
        elif action == 'modified':
            dest_dir = self.base_path / self.current_version / 'human_fix' / 'images'
        else:
            return
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / image_name
        
        if review_image_path.exists():
            shutil.move(str(review_image_path), str(dest_path))

    def get_statistics(self) -> Dict[str, Any]:
        return self.db.get_statistics()
