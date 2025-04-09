from fastapi import HTTPException, status
from typing import Dict, Optional, Any

class APIExceptions:
    """
    API异常类，集中定义各种API错误
    """
    # ================ 认证相关异常 (Authentication related exceptions) ================
    # 通用认证错误
    CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",  # 无法验证凭证
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Token相关错误
    TOKEN_EXPIRED_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",  # Token已过期
        headers={"WWW-Authenticate": "Bearer"},
    )

    TOKEN_INVALID_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",  # Token无效
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 用户状态错误
    INACTIVE_USER_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Inactive user",  # 用户未激活
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ================ 用户相关异常 (User related exceptions) ================
    # 用户注册相关错误
    USERNAME_EXISTS_EXCEPTION = HTTPException(
        status_code=471,  # 自定义状态码：471 - 用户名已存在
        detail="Username already exists",  # 用户名已存在
    )

    EMAIL_EXISTS_EXCEPTION = HTTPException(
        status_code=472,  # 自定义状态码：472 - 邮箱已被注册
        detail="Email already registered",  # 邮箱已被注册
    )
    
    INVALID_EMAIL_FORMAT_EXCEPTION = HTTPException(
        status_code=473,  # 自定义状态码：473 - 邮箱格式无效
        detail="Invalid email format",  # 邮箱格式无效
    )
    
    # 邀请码错误
    INVALID_INVITE_CODE_EXCEPTION = HTTPException(
        status_code=451,  # 自定义状态码：451 - 无效邀请码
        detail="Invalid invite code",  # 无效的邀请码
    )

    # 用户登录相关错误
    USER_NOT_FOUND_EXCEPTION = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",  # 用户不存在
    )
    
    INCORRECT_PASSWORD_EXCEPTION = HTTPException(
        status_code=461,  # 自定义状态码：461 - 密码错误
        detail="Incorrect password",  # 密码错误
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    INCORRECT_USERNAME_PASSWORD_EXCEPTION = HTTPException(
        status_code=460,  # 自定义状态码：460 - 用户名或密码错误
        detail="Incorrect username or password",  # 用户名或密码错误
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ================ 权限相关异常 (Permission related exceptions) ================
    PERMISSION_DENIED_EXCEPTION = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",  # 权限不足
    )

    # ================ 系统异常 (System exceptions) ================
    NETWORK_ERROR_EXCEPTION = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Network error or service unavailable, please try again later",  # 网络错误或服务不可用，请稍后再试
    )

    # ================ 聊天相关异常 (Chat related exceptions) ================
    CHAT_NOT_FOUND_EXCEPTION = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Chat not found",  # 聊天记录不存在
    )
    
    # 指定用户未找到指定对话
    USER_CHAT_NOT_FOUND_EXCEPTION = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Chat not found for this user",  # 未找到此用户的指定对话
    )

    CHAT_ID_EXISTS_EXCEPTION = HTTPException(
        status_code=status.HTTP_409_CONFLICT,  # 409 Conflict 状态码表示请求冲突
        detail="Chat ID already exists",  # 指定的 Chat ID 已存在
    )

    INVALID_ROLE_EXCEPTION = HTTPException(
        status_code=463,  # 自定义状态码：463 - 角色无效
        detail="Invalid role",  # 角色无效
    )

    # ================ 业务逻辑相关异常 (Business logic related exceptions) ================
    RATE_LIMIT_EXCEEDED_EXCEPTION = HTTPException(
        status_code=470,  # 自定义状态码：470 - 超过速率限制
        detail="Rate limit exceeded, please try again later",  # 请求频率超出限制，请稍后再试
    )

    QUOTA_EXCEEDED_EXCEPTION = HTTPException(
        status_code=471,  # 自定义状态码：471 - 额度已用完
        detail="Your quota has been exhausted",  # 您的使用额度已用完
    )

    @classmethod
    def create_not_found_exception(cls, resource_name: str) -> HTTPException:
        """创建资源不存在异常"""
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} not found"  # 资源不存在
        )

    @classmethod
    def create_already_exists_exception(cls, resource_name: str) -> HTTPException:
        """创建资源已存在异常"""
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{resource_name} already exists"  # 资源已存在
        )
        
    @classmethod
    def create_custom_exception(
        cls, 
        status_code: int, 
        detail: str, 
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPException:
        """创建自定义异常"""
        return HTTPException(
            status_code=status_code,
            detail=detail,
            headers=headers
        ) 