from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Example
from app.schemas import ExampleCreate, ExampleOut

router = APIRouter(prefix="/api/examples", tags=["examples"])


@router.get("/", response_model=list[ExampleOut])
def list_examples(db: Session = Depends(get_db)):
    return db.query(Example).all()


@router.post("/", response_model=ExampleOut)
def create_example(payload: ExampleCreate, db: Session = Depends(get_db)):
    item = Example(name=payload.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
