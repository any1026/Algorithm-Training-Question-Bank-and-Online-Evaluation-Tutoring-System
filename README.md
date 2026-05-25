# Algorithm Training Question Bank and Online Evaluation Tutoring System

一个面向算法训练的题库、提交评测和学习辅导后端项目。当前阶段已经完成后端 MVP：题目管理、测试用例管理、代码提交、Redis 判题队列、Python/C++ 判题 Worker、提交统计、Docker Compose 一键启动和自动化测试。

> 说明：当前判题模块用于本地学习和项目展示，已经具备基本隔离和超时控制，但还不是面向公网不可信代码的生产级沙箱。后续如果要公开部署，需要继续加入容器级/系统级资源隔离、权限收敛和审计。

## 技术栈

- Backend: FastAPI, Pydantic, SQLAlchemy
- Database: MySQL 8.0
- Queue/Cache: Redis
- Judge Worker: Python subprocess, C++17/g++
- DevOps: Docker, Docker Compose
- Test/Quality: pytest, ruff

## 已实现功能

- 健康检查接口：`GET /health`
- 题目 CRUD：创建、列表查询、详情、更新、删除
- 题目筛选：按关键词、难度、标签查询
- 测试用例管理：为题目添加/删除测试用例
- 提交记录：创建提交、查询提交、提交列表、统计信息
- 异步评测：提交代码后进入 Redis 队列，由 Worker 消费并判题
- 判题结果：`PENDING`, `RUNNING`, `AC`, `WA`, `CE`, `RE`, `TLE`
- 支持语言：`python`, `cpp`
- 种子数据：内置 A + B Problem 示例题

## 目录结构

```text
.
├── backend/
│   ├── Dockerfile
│   └── app/
│       ├── api/          # FastAPI routes
│       ├── core/         # config, database, redis
│       ├── models/       # SQLAlchemy models
│       ├── schemas/      # Pydantic schemas
│       ├── services/     # business logic and judge service
│       ├── worker/       # Redis judge worker
│       ├── main.py
│       └── seed.py
├── scripts/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── requirements-dev.txt
```

## 本地启动

确保本机已经安装并启动 Docker Desktop，然后在项目根目录执行：

```powershell
docker compose up -d --build
```

服务启动后：

- API: `http://localhost:8000`
- Swagger 文档: `http://localhost:8000/docs`
- MySQL: `localhost:3307`
- Redis: `localhost:6380`

检查服务：

```powershell
Invoke-RestMethod http://localhost:8000/health
docker compose ps
```

初始化示例题：

```powershell
docker compose exec -T api python -m app.seed
```

## 接口示例

创建题目：

```powershell
$body = @{
  title = "A + B Problem"
  difficulty = "easy"
  description = "Read two integers and output their sum."
  input_description = "Two integers a and b."
  output_description = "One integer, the sum of a and b."
  constraints = "-10^9 <= a, b <= 10^9"
  sample_input = "1 2`n"
  sample_output = "3`n"
  tags = @("basic", "math")
  test_cases = @(
    @{ input_data = "1 2`n"; expected_output = "3`n"; is_sample = $true; sort_order = 1 },
    @{ input_data = "-5 8`n"; expected_output = "3`n"; is_sample = $false; sort_order = 2 }
  )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/problems" -ContentType "application/json" -Body $body
```

提交 Python 代码：

```powershell
$body = @{
  problem_id = 1
  language = "python"
  code = "a,b=map(int,input().split())`nprint(a+b)`n"
} | ConvertTo-Json

$sub = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/submissions" -ContentType "application/json" -Body $body
Invoke-RestMethod "http://localhost:8000/api/v1/submissions/$($sub.id)"
```

提交 C++ 代码：

```powershell
$code = @"
#include <bits/stdc++.h>
using namespace std;
int main() {
    long long a, b;
    cin >> a >> b;
    cout << a + b << '\n';
    return 0;
}
"@

$body = @{
  problem_id = 1
  language = "cpp"
  code = $code
} | ConvertTo-Json

$sub = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/submissions" -ContentType "application/json" -Body $body
Invoke-RestMethod "http://localhost:8000/api/v1/submissions/$($sub.id)"
```

## 本地开发

创建虚拟环境并安装依赖：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

运行测试和代码检查：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check backend tests
```

如果想直接用本机 Python 运行 API，需要先启动 MySQL 和 Redis，并准备 `.env`：

```powershell
Copy-Item .env.example .env
docker compose up -d mysql redis
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

## 常见命令

```powershell
docker compose up -d
docker compose logs api --tail=80
docker compose logs worker --tail=80
docker compose exec -T api python -m app.seed
docker compose down
```

如需清空本地 Docker 数据卷并重新初始化：

```powershell
docker compose down -v
docker compose up -d --build
docker compose exec -T api python -m app.seed
```
