from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from requests.exceptions import RequestException
import re
import uuid

from app.core import security
from app.core.config import Config
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.api.exceptions import APIExceptions

router = APIRouter()  # 创建一个名为 "router" 的 API 路由器
# 定义 JWT 认证的 token 端点（/token），客户端通过此端点获取 token。
"""
JWT 是在用户登录时（例如通过 /token 端点）动态生成的，而不是为每个用户预先分配一个固定的 JWT。
每次用户成功认证（提供正确的用户名和密码），服务器会生成一个新的 JWT，包含该用户的身份信息（例如 sub 字段）和过期时间（exp）
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token") 

"""
Depends 是 FastAPI 提供的一个依赖注入工具，允许函数在调用时自动解析和提供参数，而无需手动传入。
"""
async def get_current_user(
    db: Session = Depends(get_db),  # 声明并注入依赖项
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    通过解析 JWT token 获取当前登录用户，验证其身份。
    如果 token 无效或用户不存在，将抛出 HTTP 401 Unauthorized 异常。
    
    在 FastAPI 中，raise 抛出的 HTTPException 会被框架捕获并转换为 HTTP 响应，
    不会中断整个程序（服务器继续运行）。
    """
    
    # 解码 JWT token，并验证其有效性。如果 token 无效或用户不存在，将抛出异常。
    try:
        # jwt.decode: 解码 JWT 令牌。
        # token: 从请求中提取的令牌。
        # Config.SECRET_KEY: 用于签名验证的密钥。
        # algorithms=[Config.ALGORITHM]: 使用的加密算法（如 "HS256"）。
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        
        # 从解码后的 payload 中提取 sub 字段（通常表示用户名或用户 ID）
        username: str = payload.get("sub")
        # 如果 payload 中没有 sub 字段，则抛出异常
        if username is None:
            raise APIExceptions.TOKEN_INVALID_EXCEPTION
    except JWTError:
        # 如果令牌无效（例如签名错误、过期等），捕获异常并抛出异常。
        raise APIExceptions.TOKEN_INVALID_EXCEPTION
    
    # 查询用户，如果用户不存在，抛出异常。
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise APIExceptions.USER_NOT_FOUND_EXCEPTION
    
    # 用户处于非活动状态
    if not user.is_active:
        raise APIExceptions.INACTIVE_USER_EXCEPTION
    
    # 返回经过验证的 User 对象，供后续接口使用。
    return user

# 验证邮箱格式的函数
def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式是否有效
    简单的正则表达式验证：包含@符号和点号，并且@在点号之前
    """
    if not email or email.strip() == "":
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

# 用户注册接口
@router.post("/register", response_model=UserResponse, operation_id="register_user")
async def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    用户注册接口
    - username: 必填，用户名
    - password: 必填，密码
    - email: 可选，邮箱
    - nickname: 可选，昵称
    - invite_code: 必填，邀请码
    """
    try:
        # 验证邀请码
        invite_codes = Config.get_invite_codes
        # 只有当邀请码列表不为空时才验证邀请码
        if invite_codes and user_in.invite_code not in invite_codes:
            raise APIExceptions.INVALID_INVITE_CODE_EXCEPTION
        
        # 检查用户名是否存在
        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise APIExceptions.USERNAME_EXISTS_EXCEPTION
        
        # 处理邮箱
        email = user_in.email
        if email and email.strip():  # 如果提供了非空邮箱
            # 验证邮箱格式
            if not is_valid_email(email):
                raise APIExceptions.INVALID_EMAIL_FORMAT_EXCEPTION
                
            # 检查邮箱是否已存在
            user = db.query(User).filter(User.email == email).first()
            if user:
                raise APIExceptions.EMAIL_EXISTS_EXCEPTION
        else:
            # 如果没有提供邮箱，将其设置为None，避免空字符串导致的唯一性约束问题
            email = None
        
        # 如果未提供nickname或为空字符串，生成一个随机的nickname
        nickname = user_in.nickname
        if not nickname or nickname.strip() == "":
            nickname = f"user_{uuid.uuid4().hex[:8]}"
        
        # 创建新用户
        user = User(
            username=user_in.username,
            email=email,  # 使用处理后的email
            nickname=nickname,
            hashed_password=security.get_password_hash(user_in.password),
            is_active=True,  # 默认设置为激活状态
            is_superuser=False,  # 默认设置为非超级用户
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except RequestException as e:
        # 处理网络或服务器错误
        raise APIExceptions.NETWORK_ERROR_EXCEPTION from e

# 获取 JWT 访问令牌
@router.post("/token", response_model=Token, operation_id="get_access_token")
async def login_access_token(
    db: Session = Depends(get_db),  # 注入数据库会话，通过 get_db 获取。
    form_data: OAuth2PasswordRequestForm = Depends()  # 注入表单数据，使用 FastAPI 的 OAuth2PasswordRequestForm，从请求中提取用户名和密码。
) -> Any:
    """
    用户登录接口，获取 JWT 访问令牌
    """
    # 验证用户凭证
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 检查用户是否存在
    if not user:
        raise APIExceptions.USER_NOT_FOUND_EXCEPTION
    
    # 验证密码
    if not security.verify_password(form_data.password, user.hashed_password):
        raise APIExceptions.INCORRECT_PASSWORD_EXCEPTION
    
    # 验证用户状态    
    if not user.is_active:
        raise APIExceptions.INACTIVE_USER_EXCEPTION
    
    # 生成访问 token - 使用 timedelta 创建过期时间间隔
    # Config.ACCESS_TOKEN_EXPIRE_MINUTES: 从配置中读取令牌有效期（例如 30 分钟）
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = security.create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/test_token", response_model=UserResponse, operation_id="test_access_token")
async def test_token(current_user: User = Depends(get_current_user)):
    """
    测试访问 token 是否有效
    """
    return current_user