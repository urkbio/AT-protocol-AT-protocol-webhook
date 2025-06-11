# Memos to Bluesky Webhook

这是一个用于将 Memos 笔记自动同步到 Bluesky 的 Webhook 服务。当你在 Memos 中创建新笔记时，该服务会自动将内容同步发布到你的 Bluesky 账号。

## 功能特点

- 监听 Memos webhook 事件
- 自动将新建的笔记同步到 Bluesky
- 支持环境变量配置
- 错误处理和日志记录

## 安装要求

- Python 3.7+
- pip

## 安装步骤

1. 克隆仓库：
```bash
git clone [你的仓库URL]
cd AT-protocol-webhook
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
```
然后编辑 `.env` 文件，填入你的 Bluesky 账号信息：
- `BLUESKY_HANDLE`: 你的 Bluesky 用户名（例如：user.bsky.social）
- `BLUESKY_APP_PASSWORD`: 你的 Bluesky 应用密码

## 运行服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## 配置 Memos Webhook

1. 在 Memos 设置中找到 Webhook 配置部分
2. 添加新的 Webhook
3. 输入你的服务URL：`http://你的服务器地址:8000/webhook`

## API 端点

- POST `/webhook`: 接收来自 Memos 的 webhook 请求

## 注意事项

- 确保你的服务器能够被 Memos 服务器访问
- 请妥善保管你的 Bluesky 账号信息
- 建议在生产环境中使用反向代理和 HTTPS

## 许可证

MIT