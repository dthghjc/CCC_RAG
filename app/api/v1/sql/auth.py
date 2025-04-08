from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from requests.exceptions import RequestException

from app.core import security
from app.core.config import Config
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

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
    通过解析 JWT token 获取当前登录用户，验证其身份。如果 token 无效或用户不存在，将抛出 HTTP 401 Unauthorized 异常。
    """
    # 异常定义
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,  # HTTP 状态码 401，表示未授权。
        detail="Could not validate credentials",  # 错误信息，提示无法验证凭证。
        headers={"WWW-Authenticate": "Bearer"},  # 返回 WWW-Authenticate: Bearer，符合 OAuth2 规范，提示客户端需要提供有效的 Bearer Token。
    )
    # 解码 JWT token，并验证其有效性。如果 token 无效或用户不存在，将抛出 credentials_exception 异常。
    try:
        """
        jwt.decode: 解码 JWT 令牌。
        token: 从请求中提取的令牌。
        settings.SECRET_KEY: 用于签名验证的密钥（通常在配置文件中定义）。
        algorithms=[settings.ALGORITHM]: 使用的加密算法（如 "HS256"）。
        """
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        # 从解码后的 payload 中提取 sub 字段（通常表示用户名或用户 ID）
        username: str = payload.get("sub")
        if username is None:
            # 如果 payload 中没有 sub 字段，则抛出 credentials_exception 异常
            """
            如果 raise 抛出的异常没有被任何 try-except 捕获，程序会被中断并退出。
            如果使用了 try-except 捕获异常，程序不会中断，可以继续执行后续代码。
            异常会沿着调用栈传播，直到被捕获或程序终止。
            在 FastAPI 中，raise 抛出的 HTTPException 会被框架捕获并转换为 HTTP 响应，不会中断整个程序（服务器继续运行）。
            """
            raise credentials_exception
    except JWTError:
        # 如果令牌无效（例如签名错误、过期等），捕获异常并抛出 401 异常。
        raise credentials_exception
    # 查询用户，如果用户不存在，抛出 credentials_exception 异常。
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    # 用户处于非活动状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 返回经过验证的 User 对象，供后续接口使用。
    return user

# 用户注册接口
@router.post("/register", response_model=UserResponse, operation_id="register_user")
async def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    用户注册接口
    - username: 必填，用户名
    - password: 必填，密码
    - email: 可选，邮箱
    - nickname: 可选，昵称
    
    注：id、is_active、is_superuser 由系统自动生成
    """
    try:
        # 检查用户名是否存在
        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="用户名已存在",
            )
        
        # 如果提供了邮箱，检查邮箱是否存在
        if user_in.email:
            user = db.query(User).filter(User.email == user_in.email).first()
            if user:
                raise HTTPException(
                    status_code=400,
                    detail="邮箱已被注册",
                )
        
        # 创建新用户
        user = User(
            username=user_in.username,
            email=user_in.email,
            nickname=user_in.nickname,
            hashed_password=security.get_password_hash(user_in.password),
            is_active=True,  # 默认设置为激活状态
            is_superuser=False,  # 默认设置为非超级用户
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except RequestException as e:
        raise HTTPException(
            status_code=503,
            detail="网络错误或服务器无法访问，请稍后重试",
        ) from e

# 获取 JWT 访问令牌
@router.post("/token", response_model=Token, operation_id="get_access_token")
async def login_access_token(
    db: Session = Depends(get_db),  # 注入数据库会话，通过 get_db 获取。
    form_data: OAuth2PasswordRequestForm = Depends()  # 注入表单数据，使用 FastAPI 的 OAuth2PasswordRequestForm，从请求中提取用户名和密码。
) -> Any:
    """
    用户登录接口。
    grant_type="password": 表示使用密码进行授权。
    scope：权限范围，可选，默认为空字符串 ""。
    client_id：客户端 ID，可选，默认为 None。
    client_secret：客户端密钥，可选，默认为 None。
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):  # not security.verify_password(...): 密码验证失败。
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 检查用户状态
    elif not user.is_active:  # not user.is_active: 检查用户是否被禁用。
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 生成访问 token
    """
    使用 timedelta 创建过期时间间隔。
    settings.ACCESS_TOKEN_EXPIRE_MINUTES: 从配置中读取令牌有效期（例如 30 分钟）。
    """
    # token 过期时间
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    # token
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/test_token", response_model=UserResponse, operation_id="test_access_token")
async def test_token(current_user: User = Depends(get_current_user)):
    """
    测试访问 token 是否有效。
    """
    return current_user