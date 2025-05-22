import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from loguru import logger
import time

@dataclass
class FaceLogEntry:
    id: int
    timestamp: float
    camera_id: int
    camera_name: str
    face_name: str
    age: Optional[int]
    gender: Optional[str]
    confidence: float
    screenshot_path: Optional[str]

    def __post_init__(self):
        # Convert timestamp to float if it comes as bytes
        if isinstance(self.timestamp, bytes):
            self.timestamp = float(self.timestamp.decode('utf-8'))
        elif isinstance(self.timestamp, str):
            self.timestamp = float(self.timestamp)

class FaceDatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database with required tables"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create face_logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS face_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        camera_id INTEGER NOT NULL,
                        camera_name TEXT NOT NULL,
                        face_name TEXT NOT NULL,
                        age INTEGER,
                        gender TEXT,
                        confidence REAL NOT NULL,
                        screenshot_path TEXT
                    )
                ''')
                
                # Create known_faces table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS known_faces (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        embedding BLOB NOT NULL,
                        image_path TEXT NOT NULL,
                        created_at REAL NOT NULL
                    )
                ''')
                
                conn.commit()
                logger.success("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def log_face_event(self, event) -> int:
        """Log a face recognition event to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO face_logs (
                        timestamp, camera_id, camera_name, face_name,
                        age, gender, confidence, screenshot_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    float(event.timestamp),
                    int(event.camera_id),
                    str(event.camera_name),
                    str(event.face_name),
                    int(event.age) if event.age else None,
                    str(event.gender) if event.gender else None,
                    float(event.confidence),
                    str(event.screenshot_path) if event.screenshot_path else None
                ))
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Error logging face event: {e}")
            raise

    def get_face_logs(self, limit: int = 100, 
                 camera_id: Optional[int] = None,
                 face_name: Optional[str] = None,
                 start_time: Optional[float] = None,
                 end_time: Optional[float] = None) -> List[FaceLogEntry]:
        """Retrieve face logs with optional filters"""
        try:
            query = '''
                SELECT id, timestamp, camera_id, camera_name, face_name, age, gender, confidence, screenshot_path
                FROM face_logs
            '''
            params = []
            conditions = []
            
            if camera_id is not None:
                conditions.append("camera_id = ?")
                params.append(camera_id)
                
            if face_name is not None:
                conditions.append("face_name = ?")
                params.append(face_name)
                
            if start_time is not None:
                conditions.append("timestamp >= ?")
                params.append(float(start_time))
                
            if end_time is not None:
                conditions.append("timestamp <= ?")
                params.append(float(end_time))
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                entries = []
                for row in cursor.fetchall():
                    try:
                        # Convert all values to proper types
                        entries.append(FaceLogEntry(
                            id=row['id'],
                            timestamp=float(row['timestamp']),
                            camera_id=row['camera_id'],
                            camera_name=row['camera_name'],
                            face_name=row['face_name'],
                            age=row['age'],
                            gender=row['gender'],
                            confidence=float(row['confidence']),
                            screenshot_path=row['screenshot_path']
                        ))
                    except Exception as e:
                        logger.error(f"Error converting row {dict(row)}: {e}")
                        continue
                        
                return entries
                
        except Exception as e:
            logger.error(f"Error retrieving face logs: {e}")
            return []

    def add_known_face(self, name: str, embedding: bytes, image_path: str) -> bool:
        """Add a known face to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO known_faces (name, embedding, image_path, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (name, embedding, image_path, time.time()))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Face with name '{name}' already exists")
            return False
        except Exception as e:
            logger.error(f"Error adding known face: {e}")
            return False

    def get_known_faces(self) -> List[dict]:
        """Retrieve all known faces from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, embedding, image_path FROM known_faces
                ''')
                return [{
                    'name': row[0],
                    'embedding': row[1],
                    'image_path': row[2]
                } for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error retrieving known faces: {e}")
            return []

    def delete_known_face(self, name: str) -> bool:
        """Delete a known face from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM known_faces WHERE name = ?
                ''', (name,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting known face: {e}")
            return False