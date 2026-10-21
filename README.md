# East China R&D Opportunity Radar

面向 PingCode 企业软件销售的华东研发型企业机会雷达。M1 聚焦可运行、可测试的数据底座与基础驾驶舱，不包含自动互联网监测。

## M1 已实现

- 企业创建、修改、查询、别名、筛选、Excel 批量导入与导出
- 兼容 `华东研发企业Universe-Part1-v0.3.xlsx` 的多工作表和中文字段
- 企业事件创建、查询、证据原文、来源、核验状态与重复约束
- S0—S3 机会状态与每次评估历史；状态不等同于采购概率
- B/R/P 信号定义表、JSON 规则配置与版本字段
- AI 结构化输出的 Pydantic 校验契约；无证据的企业事实会被拒绝
- 中文 Web 驾驶舱：总览、企业列表、企业详情、事件时间线、机会排行、信号规则
- PostgreSQL、Alembic、Docker Compose、模拟种子数据、API 测试

## 快速启动

```bash
cp .env.example .env
docker compose up --build
```

打开：

- Web：<http://localhost:3000>
- API 文档：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/api/v1/health>

首次启动会自动执行 Alembic 迁移并写入明确标记的模拟数据。修改 `.env` 中的数据库密码后再用于共享环境。

## 本地开发

后端：

```bash
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run python -m app.seed
uv run uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 测试

```bash
cd backend && uv run pytest
cd frontend && npm run typecheck && npm run build
docker compose config
```

## Excel 导入

标准模板位于 `templates/company-import-template.xlsx`。API 也兼容以下 Universe 字段：

- `企业名称`
- `一级行业`
- `总部/华东研发地`
- `软件/嵌入式研发规模(估)`
- `销售优先级`

导入器会忽略 `口径说明`、`汇总`、`README` 和 `说明` 工作表；同名企业会跳过。研发规模如 `50-100/待核` 会取下限 `50` 用于筛选，原表中的“待核”不应被解释为已核验事实。

## 目录

```text
.
├── backend/                 FastAPI、SQLAlchemy、Alembic、测试
│   ├── alembic/versions/   初始数据库迁移
│   ├── app/                API、模型、服务、种子数据
│   └── tests/              单元与 API 集成测试
├── frontend/                Next.js、TypeScript、Tailwind、shadcn 风格组件
│   ├── app/                 六类中文驾驶舱页面
│   ├── components/          共享布局与 UI 组件
│   └── lib/                 类型、API 与降级演示数据
├── templates/               Excel 导入模板
├── compose.yaml
└── .env.example
```

## 数据准确性约束

- 模拟企业与事件始终带“模拟”标识。
- M1 没有配置真实数据源，也没有自动互联网监测。
- AI 只提供结构化辅助分析契约；真实 OpenAI API 调用、重试与审计将在 M2 实现。
- 机会状态表达证据成熟度，不存储 AI 主观“采购概率”。
- 公开信息仍需人工核验；原始来源与证据摘录应长期保留。

## M2 建议

1. 实现 `SourceAdapter` 抽象、RSS、手工 URL 与历史事件导入。
2. 增加增量游标、任务日志、指数退避重试和内容指纹去重。
3. 接入可配置 OpenAI 模型，增加 JSON Schema/Pydantic 双重校验、调用审计和证据不足拒答。
4. 完成信号规则 CRUD、规则回放、事件—信号关联与机会状态建议。
5. 加入销售反馈闭环、权限、操作审计和真实数据源的验收基线。

