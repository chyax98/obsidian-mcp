# Obsidian Vault MCP

[![PyPI](https://img.shields.io/pypi/v/obsidian-vault-mcp)](https://pypi.org/project/obsidian-vault-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/obsidian-vault-mcp)](https://pypi.org/project/obsidian-vault-mcp/)
[![License](https://img.shields.io/github/license/chyax98/obsidian-mcp)](https://github.com/chyax98/obsidian-mcp/blob/main/LICENSE)

Obsidian 知识库的 MCP 服务，提供语义搜索和记忆存储能力。

## 特性

- **混合搜索**：BM25 关键词 + 向量语义搜索
- **后台索引**：启动不阻塞，增量更新
- **记忆存储**：SQLite 持久化
- **零配置**：开箱即用

## 安装

```bash
uv tool install obsidian-vault-mcp --python 3.12
```

## 工具列表

| 工具 | 说明 |
|------|------|
| `search` | 搜索笔记（mode: bm25/semantic/hybrid） |
| `get_backlinks` | 获取反向链接 |
| `get_tags` | 获取标签或按标签查找 |
| `find_orphans` | 查找孤立笔记 |
| `recent_notes` | 最近修改的笔记 |
| `memory_set` | 存储记忆 |
| `memory_get` | 获取记忆 |
| `memory_list` | 列出记忆 |
| `memory_delete` | 删除记忆 |
| `stats` | 统计信息 |

## 使用

### Vault 路径配置

优先级：`--vault` 参数 > `OBSIDIAN_VAULT_PATH` 环境变量 > 当前目录

```bash
# 命令行参数
obsidian-vault-mcp --vault /path/to/vault

# 环境变量
export OBSIDIAN_VAULT_PATH=/path/to/vault
obsidian-vault-mcp
```

### Claude Code 配置

**命令行添加：**

```bash
claude mcp add obsidian-vault \
  -e OBSIDIAN_VAULT_PATH=/path/to/vault \
  -- obsidian-vault-mcp
```

**项目 `.mcp.json`（放在 vault 目录下）：**

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "type": "stdio",
      "command": "obsidian-vault-mcp",
      "env": {
        "OBSIDIAN_VAULT_PATH": "${PWD}"
      }
    }
  }
}
```

## 索引机制

- 启动时后台初始化（不阻塞主线程）
- 每 5 分钟检查文件变动
- 增量更新（只处理变动文件）
- 缓存 mtime + size 判断变动

## 开发

```bash
git clone https://github.com/chyax98/obsidian-mcp.git
cd obsidian-mcp
uv sync
uv run obsidian-vault-mcp --vault /path/to/vault
```

## License

MIT
