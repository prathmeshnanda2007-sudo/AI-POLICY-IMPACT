import os
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

# Read the connection URL from environment or default to local SQLite
# To switch to PostgreSQL, simply set DATABASE_URL=postgresql://user:password@localhost/policy_simulator
DB_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'data', 'policy_simulator.db')}")

# Create SQLAlchemy engine
# connect_args={'check_same_thread': False} is only needed for SQLite
connect_args = {'check_same_thread': False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    scenarios = relationship("Scenario", back_populates="owner")
    simulations = relationship("SimulationHistory", back_populates="user")


class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    inputs = Column(Text, nullable=False)  # Stored as JSON string
    results = Column(Text, nullable=False) # Stored as JSON string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="scenarios")


class SimulationHistory(Base):
    __tablename__ = "simulation_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inputs = Column(Text, nullable=False)
    results = Column(Text, nullable=False)
    model_type = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="simulations")


class ModelTrainingLog(Base):
    __tablename__ = "model_training_log"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_type = Column(String, nullable=False)
    rmse = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)
    training_samples = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create tables if they don't exist."""
    # This will create tables in both SQLite and PostgreSQL automatically.
    Base.metadata.create_all(bind=engine)
    print(f"[OK] Database initialized at {DB_URL}")


# --- DB Session Dependency ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Scenarios CRUD ---

def save_scenario(name: str, inputs: dict, results: dict) -> dict:
    db = SessionLocal()
    scenario = Scenario(
        name=name,
        inputs=json.dumps(inputs),
        results=json.dumps(results)
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    result = {'id': scenario.id, 'name': scenario.name, 'inputs': inputs, 'results': results}
    db.close()
    return result


def get_all_scenarios() -> list:
    db = SessionLocal()
    try:
        rows = db.query(Scenario).order_by(Scenario.created_at.desc()).all()
        return [
            {
                'id': row.id,
                'name': row.name,
                'inputs': json.loads(row.inputs),
                'results': json.loads(row.results),
                'created_at': row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]
    finally:
        db.close()


def delete_scenario(scenario_id: int) -> bool:
    db = SessionLocal()
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario:
        db.delete(scenario)
        db.commit()
        db.close()
        return True
    db.close()
    return False


# --- Simulation History ---

def save_simulation(inputs: dict, results: dict, model_type: str = None, confidence: float = None):
    db = SessionLocal()
    sim = SimulationHistory(
        inputs=json.dumps(inputs),
        results=json.dumps(results),
        model_type=model_type,
        confidence=confidence
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)
    db.close()
    return sim.id


def get_history(limit: int = 50) -> list:
    db = SessionLocal()
    try:
        rows = db.query(SimulationHistory).order_by(SimulationHistory.created_at.desc()).limit(limit).all()
        return [
            {
                'id': row.id,
                'inputs': json.loads(row.inputs),
                'results': json.loads(row.results),
                'model_type': row.model_type,
                'confidence': row.confidence,
                'timestamp': row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]
    finally:
        db.close()


# --- Training Log ---

def log_training(model_type: str, rmse: float, r2: float, samples: int):
    db = SessionLocal()
    log = ModelTrainingLog(
        model_type=model_type,
        rmse=rmse,
        r2_score=r2,
        training_samples=samples
    )
    db.add(log)
    db.commit()
    db.close()


# --- User Management ---

import re

def create_user(email: str, password_hash: str, name: str) -> dict:
    """Create a new user. Returns user dict or raises on duplicate."""
    email = email.lower().strip()
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        raise ValueError('Invalid email format')
    if len(name.strip()) < 2:
        raise ValueError('Name must be at least 2 characters')

    db = SessionLocal()
    user = User(
        email=email,
        password_hash=password_hash,
        name=name.strip()
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        user_dict = {'id': user.id, 'email': user.email, 'name': user.name}
    except IntegrityError:
        db.rollback()
        raise ValueError('Email already registered')
    finally:
        db.close()
    return user_dict


def get_user_by_email(email: str) -> Optional[dict]:
    """Find a user by email. Returns dict with password_hash or None."""
    db = SessionLocal()
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    db.close()
    if user:
        return {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'password_hash': user.password_hash
        }
    return None

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Find a user by id."""
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if user:
        return {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
    return None

def update_last_login(user_id: int):
    """Update user last login timestamp."""
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
    db.close()
