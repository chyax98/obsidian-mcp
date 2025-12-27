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

## 使用

```bash
uv run obsidian-vault-mcp --vault /path/to/vault
```

## 配置 MCP 客户端

**Claude Code：**

```bash
claude mcp add obsidian-vault --transport stdio -- uv run --directory /path/to/obsidian-mcp obsidian-vault-mcp --vault /path/to/vault
```

**`.mcp.json`：**

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/obsidian-mcp", "obsidian-vault-mcp", "--vault", "/path/to/vault"]
    }
  }
}
```

## 索引更新

- 启动时自动加载缓存
- 后台每 5 分钟检查文件变动
- 增量更新（只处理变动文件）

## License

MIT
