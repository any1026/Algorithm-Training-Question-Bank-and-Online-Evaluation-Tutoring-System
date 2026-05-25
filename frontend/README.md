# Algorithm Lab Frontend

本地算法题库与在线评测工作台前端，使用 React、TypeScript、Vite、Monaco Editor 和 lucide-react 构建。

## 功能

- 题库列表、关键词搜索、难度和标签筛选
- 题目详情、标签、样例输入输出展示
- Python/C++ 代码编辑器
- 提交代码到本地 FastAPI 后端
- 轮询判题结果并展示 AC/WA/CE/RE/TLE 状态
- 桌面端三栏工作台布局，移动端纵向自适应布局

## 启动

```powershell
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

默认连接后端：

```text
http://localhost:8000
```

如需修改后端地址，复制 `.env.example` 为 `.env.local` 后调整：

```text
VITE_API_BASE_URL=http://localhost:8000
```

## 检查

```powershell
npm run lint
npm run build
```
