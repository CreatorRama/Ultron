from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session as DBSession

from database import engine, Base, get_db
from models import Session
from Schema import ClientRequest


Base.metadata.create_all(bind=engine)

app = FastAPI()

api_router = APIRouter(prefix="/api/v1")


@api_router.post("/sessions")
def create_session(
    data: ClientRequest,
    db: DBSession = Depends(get_db)
):

    new_session = Session(
        client_version=data.client_version,
        browser=data.browser,
        status="active",
        expires_in=1800,
        policy=data.privacy_policy.model_dump(),  
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "session_id": new_session.session_id,
        "status": new_session.status,
        "expires_in": new_session.expires_in,
        "policy": new_session.policy,
        "createdAt": new_session.createdAt,
        "updatedAt": new_session.updatedAt
    }


app.include_router(api_router)
