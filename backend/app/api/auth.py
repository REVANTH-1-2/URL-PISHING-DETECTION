from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from app.database.connection import db
from app.core.security import get_password_hash, verify_password, create_access_token, oauth2_scheme, decode_access_token
from app.schemas.user import UserRegister, UserLogin, UserOut, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister):
    if db.db is not None:
        existing = await db.db.users.find_one({"email": user_in.email.lower()})
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        user_doc = {
            "name": user_in.name,
            "email": user_in.email.lower(),
            "password_hash": get_password_hash(user_in.password),
            "role": "user",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        res = await db.db.users.insert_one(user_doc)
        user_id = str(res.inserted_id)
    else:
        user_id = "standalone_mock_id"
    
    user_out = UserOut(
        id=user_id,
        name=user_in.name,
        email=user_in.email.lower(),
        role="user",
        created_at=datetime.utcnow()
    )
    
    token = create_access_token(subject=user_id)
    return Token(access_token=token, token_type="bearer", user=user_out)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    if db.db is not None:
        user = await db.db.users.find_one({"email": credentials.email.lower()})
        if not user or not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user_id = str(user["_id"])
        user_out = UserOut(
            id=user_id,
            name=user["name"],
            email=user["email"],
            role=user.get("role", "user"),
            created_at=user.get("created_at", datetime.utcnow())
        )
    else:
        user_id = "standalone_mock_id"
        user_out = UserOut(
            id=user_id,
            name="Demo User",
            email=credentials.email.lower(),
            role="user",
            created_at=datetime.utcnow()
        )
    
    token = create_access_token(subject=user_id)
    return Token(access_token=token, token_type="bearer", user=user_out)

@router.get("/me", response_model=UserOut)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        # Standalone default fallback
        return UserOut(
            id="standalone_user_id",
            name="Security Admin",
            email="admin@deepshield.ai",
            role="admin",
            created_at=datetime.utcnow()
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token or token expired")
    
    user_id = payload.get("sub")
    if db.db is not None and ObjectId.is_valid(user_id):
        user = await db.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return UserOut(
                id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                role=user.get("role", "user"),
                created_at=user.get("created_at", datetime.utcnow())
            )
            
    return UserOut(
        id=user_id or "user_id",
        name="Security Analyst",
        email="analyst@deepshield.ai",
        role="user",
        created_at=datetime.utcnow()
    )
