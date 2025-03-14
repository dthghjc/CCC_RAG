from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    access_token: str: 访问令牌（JWT 字符串），必填字段，类型为字符串。
    例如："eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."。
    token_type: str: 令牌类型，必填字段，通常是 "bearer"。
    表示使用 OAuth2 的 Bearer Token 认证方式
    """
    access_token: str
    token_type: str
    
class TokenPayload(BaseModel):
    """
    sub: Optional[int] = None: 表示令牌的“主体”（subject），通常是用户标识（如用户 ID）。
    Optional[int]: 类型为整数，但可选，默认值为 None。
    在 JWT 中，sub 是标准字段，用于标识令牌所属的用户。
    """
    sub: Optional[str] = None