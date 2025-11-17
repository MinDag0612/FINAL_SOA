import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pwdlib import PasswordHash


class jwt_services:
    SECRET_KEY = "your-super-secret-key" 
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 120

    # Password Hashing
    pwd_context = PasswordHash.recommended()

    # OAuth2 Scheme
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    
    def get_hash(self, password: str):
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)