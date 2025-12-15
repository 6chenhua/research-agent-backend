"""
论文相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class PaperUploadResponse(BaseModel):
    """论文上传响应（只上传，不解析）"""
    paper_id: str = Field(..., description="论文ID")
    filename: str = Field(..., description="原始文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    status: str = Field(..., description="处理状态（uploaded）")
    message: Optional[str] = Field(None, description="提示信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "paper_id": "paper_abc123def456",
                "filename": "attention_is_all_you_need.pdf",
                "file_size": 1234567,
                "status": "uploaded",
                "message": "Paper uploaded successfully. It will be parsed when used in chat."
            }
        }