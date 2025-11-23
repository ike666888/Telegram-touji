FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下所有文件到容器
COPY . .

# 设置时区为上海（可选，方便看日志时间）
ENV TZ=Asia/Shanghai

# 启动命令
CMD ["python", "telegram_bot.py"]