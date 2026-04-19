from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.services.cv_parser import extract_text_from_pdf
from app.services.generator import generate_cv_improvements
from app.database import Base, engine, SessionLocal, CVAnalysis, User
from app.auth import hash_password, verify_password
import json

app = FastAPI(title="CVBoost AI")

# -------------------------
# INIT DATABASE
# -------------------------
Base.metadata.create_all(bind=engine)


# -------------------------
# HOME
# -------------------------
@app.get("/")
def home():
    return {"status": "CVBoost AI is running 🚀"}


# =========================
# AUTH ROUTES
# =========================

@app.post("/register")
def register(email: str = Form(...), password: str = Form(...)):

    db = SessionLocal()

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=email,
        password=hash_password(password)
    )

    db.add(new_user)
    db.commit()
    db.close()

    return {"message": "User created successfully"}


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):

    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()

    db.close()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "user_id": user.id,
        "email": user.email
    }


# =========================
# AI CV OPTIMIZER
# =========================

@app.post("/optimize-cv")
async def optimize_cv(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    user_id: int = Form(...)
):

    try:
        # 1. Extract CV text
        cv_text = extract_text_from_pdf(file)

        # 2. AI analysis
        ai_result = generate_cv_improvements(cv_text, job_description)

        # 3. Convert to dict safely
        parsed = json.loads(ai_result)

        # 4. Save in DB (linked to user)
        db = SessionLocal()

        record = CVAnalysis(
            filename=file.filename,
            match_score=int(parsed.get("match_score", 0)),
            missing_skills=str(parsed.get("missing_skills", [])),
            summary=parsed.get("summary_rewrite", ""),
            cover_letter=parsed.get("cover_letter", ""),
            user_id=user_id
        )

        db.add(record)
        db.commit()
        db.close()

        return {"result": parsed}

    except Exception as e:
        return {"error": str(e)}


# =========================
# USER HISTORY
# =========================

@app.get("/history/{user_id}")
def get_history(user_id: int):

    db = SessionLocal()

    records = db.query(CVAnalysis).filter(CVAnalysis.user_id == user_id).all()

    db.close()

    return {
        "history": [
            {
                "id": r.id,
                "filename": r.filename,
                "match_score": r.match_score,
                "missing_skills": r.missing_skills,
                "summary": r.summary,
                "cover_letter": r.cover_letter,
                "created_at": r.created_at
            }
            for r in records
        ]
    }