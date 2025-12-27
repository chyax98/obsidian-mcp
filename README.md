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

**全局安装（推荐）：**

```bash
# 从本地安装
uv tool install /path/to/obsidian-mcp --python 3.12

# 或从 GitHub 安装
uv tool install git+https://github.com/yourname/obsidian-mcp --python 3.12
```

安装后可直接使用 `obsidian-vault-mcp` 命令。

**开发模式：**

```bash
cd /path/to/obsidian-mcp
uv sync
uv run obsidian-vault-mcp
```

## Vault 路径配置

优先级：命令行参数 > 环境变量 `OBSIDIAN_VAULT_PATH` > 当前目录

```bash
# 方式 1：命令行参数
obsidian-vault-mcp --vault /path/to/vault

# 方式 2：环境变量
export OBSIDIAN_VAULT_PATH=/path/to/vault
obsidian-vault-mcp
```

## Claude Code 配置

**方式 1：命令行添加**

```bash
claude mcp add obsidian-vault \
  -e OBSIDIAN_VAULT_PATH=/path/to/vault \
  -- obsidian-vault-mcp
```

**方式 2：项目 `.mcp.json`（放在 vault 目录下）**

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

- 启动时后台初始化（不阻塞）
- 每 5 分钟检查文件变动
- 增量更新（只处理变动文件）

## License

MIT
