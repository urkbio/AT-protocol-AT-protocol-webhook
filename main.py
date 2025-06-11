import os
import json
from datetime import datetime, timezone
from typing import Dict, Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException

# 加载环境变量
load_dotenv()

# 初始化FastAPI应用
app = FastAPI(title="Memos to Bluesky Webhook")

# 从环境变量获取Bluesky账号信息
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

if not all([BLUESKY_HANDLE, BLUESKY_APP_PASSWORD]):
    raise ValueError("请设置BLUESKY_HANDLE和BLUESKY_APP_PASSWORD环境变量")

def get_bluesky_session() -> Dict[str, str]:
    """获取Bluesky会话token"""
    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD},
    )
    resp.raise_for_status()
    return resp.json()

def create_bluesky_post(text: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """发布内容到Bluesky"""
    # 获取UTC时间戳
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # 构建发布内容
    post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
        "langs": ["zh-CN"]  # 设置语言为中文
    }
    
    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {session['accessJwt']}"},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
    resp.raise_for_status()
    return resp.json()

@app.post("/webhook")
async def handle_webhook(request: Request):
    """处理来自Memos的webhook请求"""
    try:
        payload = await request.json()
        
        # 验证webhook payload格式
        activity_type = payload.get("activityType")
        if not activity_type:
            raise HTTPException(status_code=400, detail="无效的webhook payload")
            
        # 只处理新建笔记的事件
        if activity_type == "memos.memo.created":
            memo = payload.get("memo", {})
            if not memo:
                raise HTTPException(status_code=400, detail="无效的memo数据")
                
            # 获取笔记内容
            content = memo.get("content")
            if not content:
                raise HTTPException(status_code=400, detail="笔记内容为空")
                
            # 获取Bluesky会话并发布内容
            session = get_bluesky_session()
            result = create_bluesky_post(content, session)
            
            return {"status": "success", "message": "已同步到Bluesky", "result": result}
            
        return {"status": "ignored", "message": f"忽略的事件类型: {activity_type}"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON格式")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Bluesky API错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7361)