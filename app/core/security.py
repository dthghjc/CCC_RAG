from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt  # 用于编码和解码 JWT 令牌，处理令牌相关错误。
from passlib.context import CryptContext  # 来自 passlib，用于密码哈希和验证（这里用 bcrypt）。
from app.core.config import Config
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader  # FastAPI 提供的安全工具，分别处理 OAuth2 令牌和 API Key。
from sqlalchemy.orm import Session
import pytz

from app.db.session import get_db
from app.models.user import User
# from app.services.api_key import APIKeyService

Beijing_tz = pytz.timezone('Asia/Shanghai')

# 创建一个用于密码哈希和验证的 CryptContext 实例。
"""
CryptContext: passlib 的核心类，用于管理密码哈希和验证。
schemes=["bcrypt"]: 指定使用 bcrypt 算法进行密码哈希。
bcrypt 是一种安全的哈希算法，广泛用于密码存储，具有抗暴力破解的特性。
deprecated="auto": 自动处理已废弃的哈希方案（例如旧版本的 bcrypt），确保向后兼容。
"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth2 令牌验证
"""
OAuth2PasswordBearer: FastAPI 提供的 OAuth2 密码流实现。
tokenUrl="/api/v1/auth/login/access-token": 指定获取令牌的端点（登录接口）。
从请求的 Authorization 头中提取 Bearer Token（格式：Authorization: Bearer <token>）。
用于依赖注入，验证用户身份（例如 Depends(oauth2_scheme)）。
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/access-token")
# API Key 验证
"""
APIKeyHeader: FastAPI 提供的工具，用于从请求头提取 API Key。
name="X-API-Key": 指定从名为 X-API-Key 的头中读取值。
auto_error=False: 如果头中缺少 API Key，不自动抛出异常，而是返回 None，让开发者手动处理。
"""
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    plain_password: str: 用户输入的明文密码。
    hashed_password: str: 数据库中存储的哈希密码。
    pwd_context.verify:
    使用 bcrypt 验证明文密码与哈希密码是否一致。
    内部会重新计算哈希并比较，确保安全性。
    """
    return pwd_context.verify(plain_password, hashed_password)

# 生成哈希密码
def get_password_hash(password: str) -> str:
    """
    password: str: 用户输入的明文密码。
    返回值: str，生成的哈希密码。
    pwd_context.hash:
    使用 bcrypt 对明文密码进行哈希，生成安全的密码存储格式。
    """
    return pwd_context.hash(password)
# 创建访问token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    data: dict: 一个字典，包含 JWT 的 payload（有效载荷）数据。
    expires_delta: Optional[timedelta] = None: 可选参数，表示令牌的过期时间间隔。
    """
    to_encode = data.copy()
    # 检查是否提供了自定义的过期时间间隔。
    if expires_delta:
        expire = datetime.now(Beijing_tz) + expires_delta
    else:
        expire = datetime.now(Beijing_tz) + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 更新 payload
    to_encode.update({"exp": expire})
    # 使用 pyjwt 库将 payload 编码为 JWT 字符串。
    """
    to_encode: 要编码的 payload 字典。
    settings.SECRET_KEY: 密钥，用于签名令牌（从配置中读取，例如 "my-secret-key"）。
        确保安全性，通常是一个长随机字符串。
    algorithm=settings.ALGORITHM: 加密算法（从配置中读取，例如 "HS256"）。
        HS256 是常用的 HMAC SHA-256 算法。
    """
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt 

# def get_current_user(
#     db: Session = Depends(get_db),
#     token: str = Depends(oauth2_scheme)
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
    
#     user = db.query(User).filter(User.username == username).first()
#     if user is None:
#         raise credentials_exception
#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Inactive user",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user 

# def get_api_key_user(
#     db: Session = Depends(get_db),
#     api_key: str = Security(api_key_header),
# ) -> User:
#     if not api_key:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="API key header missing",
#         )
    
#     api_key_obj = APIKeyService.get_api_key_by_key(db=db, key=api_key)
#     if not api_key_obj:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid API key",
#         )
    
#     if not api_key_obj.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Inactive API key",
#         )
    
#     APIKeyService.update_last_used(db=db, api_key=api_key_obj)
#     return api_key_obj.user 