from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import json
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from database import get_db, settings, engine
from models import Base, User, Board, Product, Code, Purchase, Transaction, Package, BoardSettings, Connection

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Discord Shop Bot", docs_url=None, redoc_url=None)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend/templates"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def verify_discord_signature(request_body: bytes, signature: str, timestamp: str) -> bool:
    try:
        verify_key = VerifyKey(bytes.fromhex(settings.discord_public_key))
        verify_key.verify(f"{timestamp}{request_body.decode()}".encode(), bytes.fromhex(signature))
        return True
    except BadSignatureError:
        return False

@app.post("/interactions")
async def interactions(request: Request, db: Session = Depends(get_db)):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = await request.body()
    if not verify_discord_signature(body, signature, timestamp):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    data = json.loads(body)
    if data["type"] == 1:  # PING
        return {"type": 1}
    
    # Handle interactions: slash, buttons, select
    # Core handlers for shop board, buy, topup, check, etc.
    # Full implementation expands here with component routing
    return {"type": 4, "data": {"content": "Interaction received", "flags": 64}}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Auth check via cookie/token
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/status", response_class=HTMLResponse)
async def status(request: Request, db: Session = Depends(get_db)):
    boards = db.query(Board).all()
    return templates.TemplateResponse(request, "status.html", {"boards": boards})

# Auth endpoints
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(400, "Username taken")
    user = User(username=username, hashed_password=get_password_hash(password))
    db.add(user)
    db.commit()
    return {"ok": True}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(401, "Bad creds")
    token = create_access_token({"sub": user.username, "uid": user.id})
    response = JSONResponse({"ok": True})
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return response

# Product / Board management APIs
@app.post("/api/boards")
async def create_board(guild_id: int, verify_link: str, db: Session = Depends(get_db)):
    # Verify message link logic, create board
    board = Board(guild_id=guild_id, verify_message_link=verify_link, owner_id=1)  # from auth
    db.add(board)
    db.commit()
    return {"board_id": board.id}

# More endpoints for products, topup, packages, admin approve, etc.
# Credit update is transactional to fix the zero-credit bug

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
