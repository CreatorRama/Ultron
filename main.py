from fastapi import FastAPI, Depends, APIRouter, HTTPException
from Schema import ClientRequest, ObservationRequest
from models import Session, Observation, Context
from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session as DBSession

from database import engine, Base, get_db
from models import Session
from Schema import ClientRequest, ObservationRequest


Base.metadata.create_all(bind=engine)

app = FastAPI()

api_router = APIRouter(prefix="/api/v1")


@api_router.post("/sessions", status_code=201)
def create_session(
    data: ClientRequest,
    db: DBSession = Depends(get_db)
):
    print("ABC")
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
    }


Base.metadata.create_all(bind=engine)

app = FastAPI()

api_router = APIRouter(prefix="/api/v1")


# -----------------------------------------
# CREATE SESSION
# -----------------------------------------

@api_router.post("/sessions", status_code=201)
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
    }


# -----------------------------------------
# CREATE OBSERVATION + CONTEXT
# -----------------------------------------

@api_router.post("/sessions/{session_id}/observe",status_code=201)
def create_observation(
    session_id: str,
    data: ObservationRequest,
    db: DBSession = Depends(get_db)
):

    # -------------------------------------
    # 1. Check session exists
    # -------------------------------------
    print("ram");
    
    session = (
        db.query(Session)
        .filter(Session.session_id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # -------------------------------------
    # 2. Mandatory server validation
    # -------------------------------------

    if data.privacy.redaction_applied is not True:
        raise HTTPException(
            status_code=400,
            detail="privacy.redaction_applied must be true"
        )

    if data.privacy.raw_context_discarded is not True:
        raise HTTPException(
            status_code=400,
            detail="privacy.raw_context_discarded must be true"
        )

    if data.image is not None:

        if data.image.sanitized is not True:
            raise HTTPException(
                status_code=400,
                detail="image.sanitized must be true"
            )

    # -------------------------------------
    # 3. Create Observation
    # -------------------------------------

    new_observation = Observation(
        observation_id=data.observation_id,

        session_id=session.session_id,

        url=data.url.model_dump(),

        page=data.page.model_dump(),

        dom_elements=[
            element.model_dump()
            for element in data.dom.elements
        ],

        ocr_text_blocks=[
            block.model_dump()
            for block in data.ocr.text_blocks
        ],

        screenshot=(
            data.image.data
            if data.image is not None
            else None
        ),

        detected_redaction_types=[
            detected_type.value
            for detected_type in data.privacy.detected_types
        ]
    )

    # -------------------------------------
    # 4. Add Observation to transaction
    # -------------------------------------

    db.add(new_observation)

    # Flush sends INSERT to PostgreSQL
    # without committing the transaction.
    db.flush()

    # -------------------------------------
    # 5. Create Context
    # -------------------------------------

    new_context = Context(
        observation_id=new_observation.observation_id,

        allowed_actions=None,

        require_confirmation_for=None
    )

    # -------------------------------------
    # 6. Add Context
    # -------------------------------------

    db.add(new_context)

    # -------------------------------------
    # 7. Commit BOTH together
    # -------------------------------------

    try:

        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create observation and context"
        )

    # -------------------------------------
    # 8. Refresh context
    # -------------------------------------

    db.refresh(new_context)

    # -------------------------------------
    # 9. Response
    # -------------------------------------

    return {
        "observation_id": new_observation.observation_id,
        "accepted": True,
        "context_id": new_context.context_id,
        "privacy": {
            "sanitized": True,
            "raw_pii_received": False
        }
    }



app.include_router(api_router)
