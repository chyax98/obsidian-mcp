# Obsidian Vault MCP

Obsidian 知识库的语义搜索和记忆服务。

## 功能

| 工具 | 说明 |
|------|------|
| `search` | 搜索笔记（bm25/semantic/hybrid） |
| `get_backlinks` | 获取反向链接 |
| `get_tags` | 获取标签或按标签查找 |
| `find_orphans` | 查找孤立笔记 |
| `recent_notes` | 最近修改的笔记 |
| `memory_set` | 存储记忆 |
| `memory_get` | 获取记忆 |
| `memory_list` | 列出记忆 |
| `memory_delete` | 删除记忆 |
| `stats` | 统计信息 |

## 安装

```bash
uv sync
```

## Vault 路径配置

优先级：命令行参数 > 环境变量 > 当前目录

```bash
# 方式 1：命令行参数
uv run obsidian-vault-mcp --vault /path/to/vault

# 方式 2：环境变量
export OBSIDIAN_VAULT_PATH=/path/to/vault
uv run obsidian-vault-mcp

# 方式 3：在 vault 目录下直接运行
cd /path/to/vault
uv run --directory /path/to/obsidian-mcp obsidian-vault-mcp
```

## 配置 MCP 客户端

**Claude Code（推荐，使用环境变量）：**

```bash
claude mcp add obsidian-vault \
  --transport stdio \
  -e OBSIDIAN_VAULT_PATH=/path/to/vault \
  -- uv run --directory /path/to/obsidian-mcp obsidian-vault-mcp
```

**项目 `.mcp.json`（在 vault 目录下）：**

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/obsidian-mcp", "obsidian-vault-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "${workspaceFolder}"
      }
    }
  }
}
```

> 注：`${workspaceFolder}` 会被替换为当前工作目录（vault 路径）

## 索引机制

- 启动时后台初始化（不阻塞）
- 每 5 分钟检查文件变动
- 增量更新（只处理变动文件）

## License

MIT
