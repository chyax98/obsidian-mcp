# Vault Retriever

[![PyPI](https://img.shields.io/pypi/v/vault-retriever)](https://pypi.org/project/vault-retriever/)
[![Python](https://img.shields.io/pypi/pyversions/vault-retriever)](https://pypi.org/project/vault-retriever/)
[![License](https://img.shields.io/github/license/chyax98/vault-retriever)](https://github.com/chyax98/vault-retriever/blob/main/LICENSE)

Obsidian 知识库智能检索服务，为 AI 提供语义搜索和知识图谱分析能力。

## 特性

- **混合检索**：BM25 关键词 + 向量语义 + RRF 融合 + PageRank 加权
- **轻量高效**：mmap 索引加载，内存占用 ~300MB
- **后台索引**：启动不阻塞，增量更新
- **零配置**：开箱即用

## 安装

```bash
uv tool install vault-retriever --python 3.12
```

## 工具列表

| 工具 | 说明 |
|------|------|
| `vault_search` | 智能搜索笔记，融合关键词+语义+PageRank |
| `vault_read` | 读取笔记完整内容 |
| `vault_list` | 列出笔记，支持目录过滤和最近修改筛选 |
| `vault_links` | 获取笔记的反向链接和出链关系 |
| `vault_tags` | 获取标签统计或按标签查找笔记 |
| `vault_related` | 查找语义相似的相关笔记 |

## 使用

### Vault 路径配置

优先级：`--vault` 参数 > `OBSIDIAN_VAULT_PATH` 环境变量 > 当前目录

```bash
# 命令行参数
vault-retriever --vault /path/to/vault

# 环境变量
export OBSIDIAN_VAULT_PATH=/path/to/vault
vault-retriever
```

### Claude Code 配置

**命令行添加：**

```bash
claude mcp add vault-retriever \
  -e OBSIDIAN_VAULT_PATH=/path/to/vault \
  -- vault-retriever
```

**项目 `.mcp.json`（放在 vault 目录下）：**

```json
{
  "mcpServers": {
    "vault-retriever": {
      "type": "stdio",
      "command": "vault-retriever",
      "env": {
        "OBSIDIAN_VAULT_PATH": "${PWD}"
      }
    }
  }
}
```

## 索引机制

- 启动时后台初始化（不阻塞主线程）
- BM25 索引使用 mmap 加载，内存高效
- 向量索引使用 LanceDB 持久化
- PageRank 图谱缓存到磁盘
- 每 10 分钟检查文件变动，增量更新

## 配置

在 vault 目录下创建 `.obsidian/vault-retriever.json`：

```json
{
  "embedding_model": "BAAI/bge-small-zh-v1.5",
  "index_interval": 600
}
```

- `embedding_model`: 向量模型（默认 bge-small-zh-v1.5）
- `index_interval`: 索引更新间隔秒数（默认 600）

## 开发

```bash
git clone https://github.com/chyax98/vault-retriever.git
cd vault-retriever
uv sync
uv run vault-retriever --vault /path/to/vault
```

## License

MIT
