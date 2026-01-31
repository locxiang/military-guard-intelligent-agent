"""
API v1 路由模块
"""
from fastapi import APIRouter

from app.api.v1 import auth, archive, doc_generate, knowledge_graph, dashboard, statistics, ocr, classification, user, template, content_review

# 创建 API 路由器
api_router = APIRouter(prefix="/api/v1")

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(archive.router, prefix="/case-file", tags=["案卷管理"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR数字化"])
api_router.include_router(classification.router, prefix="/classification", tags=["智能分类"])
api_router.include_router(doc_generate.router, prefix="/doc-generate", tags=["文档生成"])
api_router.include_router(template.router, prefix="/template", tags=["模板管理"])
api_router.include_router(content_review.router, prefix="/content-review", tags=["内容审查"])
api_router.include_router(knowledge_graph.router, prefix="/knowledge-graph", tags=["知识图谱"])
api_router.include_router(user.router, prefix="/user", tags=["用户管理"])
api_router.include_router(dashboard.router, tags=["工作台"])
api_router.include_router(statistics.router, tags=["统计分析"])
