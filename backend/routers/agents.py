from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import get_db
from auth import oauth2_scheme
from jose import JWTError, jwt
from auth import SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix="/agents",
    tags=["agents"]
)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/", response_model=schemas.Agent)
def create_agent(
    agent: schemas.AgentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    return crud.create_agent(db=db, agent=agent, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Agent])
def read_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    agents = crud.get_agents(db, user_id=current_user.id, skip=skip, limit=limit)
    return agents

@router.get("/{agent_id}", response_model=schemas.Agent)
def read_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.put("/{agent_id}", response_model=schemas.Agent)
def update_agent(
    agent_id: int,
    agent: schemas.AgentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_agent = crud.update_agent(db, agent_id=agent_id, agent=agent, user_id=current_user.id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    success = crud.delete_agent(db, agent_id=agent_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"detail": "Agent deleted"}