"""Obsidian Vault MCP Server"""

import logging
import threading
from pathlib import Path
from dataclasses import asdict
from typing import Annotated, Literal

from fastmcp import FastMCP
from pydantic import Field

from config import Config, load_config
from vault import VaultReader
from search import BM25Search, VectorSearch, Indexer
from memory import MemoryStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IndexState:
    """索引状态管理"""
    def __init__(self):
        self.ready = False
        self.doc_contents: dict[str, str] = {}
        self._lock = threading.Lock()

    def set_ready(self, contents: dict[str, str]):
        with self._lock:
            self.doc_contents = contents
            self.ready = True

    def is_ready(self) -> bool:
        with self._lock:
            return self.ready

    def get_contents(self) -> dict[str, str]:
        with self._lock:
            return self.doc_contents.copy()


def create_server(vault_path: Path, config: Config | None = None) -> FastMCP:
    """创建 MCP 服务器"""

    config = config or load_config(vault_path)
    storage = config.storage_path

    # 初始化组件
    vault = VaultReader(vault_path)
    bm25 = BM25Search()
    vector = VectorSearch(storage, model_name=config.embedding_model)
    memory = MemoryStore(storage)
    indexer = Indexer(storage, bm25, vector, interval=config.index_interval)
    state = IndexState()

    # 后台初始化索引（不阻塞主线程）
    def init_index():
        logger.info("后台初始化索引...")
        docs = vault.load_all_documents()
        doc_contents = {d.path: d.content for d in docs}
        file_stats = {d.path: (d.mtime, len(d.content)) for d in docs}

        # 尝试增量更新
        result = indexer.index_incremental(doc_contents, file_stats)
        if result["status"] == "unchanged":
            # 缓存有效但 BM25 需要重建（内存索引）
            bm25.index(doc_contents)
            logger.info("从缓存恢复索引")
        elif result["status"] != "updated":
            indexer.index_full(doc_contents, file_stats)
            logger.info(f"全量索引完成: {len(docs)} 文档")
        else:
            logger.info(f"增量更新: {result}")

        state.set_ready(doc_contents)
        logger.info("索引就绪")

    # 启动后台索引线程
    threading.Thread(target=init_index, daemon=True).start()

    # 启动定时更新
    def get_docs():
        docs = vault.load_all_documents()
        contents = {d.path: d.content for d in docs}
        stats = {d.path: (d.mtime, len(d.content)) for d in docs}
        # 更新状态
        state.set_ready(contents)
        return contents, stats

    indexer.start_background(get_docs)

    # 创建 MCP 服务器
    mcp = FastMCP(
        name="obsidian-vault-mcp",
        instructions="""Obsidian Vault 搜索和记忆服务。

功能：
- search: 搜索笔记（支持关键词/语义/混合模式）
- get_backlinks: 获取反向链接
- get_tags: 获取标签
- find_orphans: 查找孤立笔记
- memory_*: 存储和获取记忆""",
    )

    # ========== 搜索（核心） ==========

    @mcp.tool(name="search", description="搜索笔记")
    def search(
        query: Annotated[str, Field(description="搜索内容")],
        mode: Annotated[
            Literal["bm25", "semantic", "hybrid"],
            Field(default="hybrid", description="搜索模式")
        ] = "hybrid",
        limit: Annotated[int, Field(default=10, ge=1, le=50)] = 10,
    ) -> dict:
        # 检查索引是否就绪
        if not state.is_ready():
            return {"error": "索引正在初始化，请稍后再试", "results": [], "count": 0}

        doc_contents = state.get_contents()

        if mode == "bm25":
            results = bm25.search(query, limit)
        elif mode == "semantic":
            if not vector.is_indexed():
                vector.index(doc_contents)
            results = vector.search(query, limit)
        else:  # hybrid
            if not vector.is_indexed():
                vector.index(doc_contents)

            bm25_results = bm25.search(query, limit * 2)
            vector_results = vector.search(query, limit * 2)

            # 融合分数
            scores: dict[str, float] = {}
            info: dict[str, dict] = {}

            # 归一化 BM25
            if bm25_results:
                max_s = max(r.score for r in bm25_results)
                min_s = min(r.score for r in bm25_results)
                range_s = max_s - min_s if max_s != min_s else 1.0
                for r in bm25_results:
                    norm = (r.score - min_s) / range_s if range_s else 0.5
                    scores[r.path] = norm * 0.5
                    info[r.path] = {"path": r.path, "snippet": r.snippet}

            for r in vector_results:
                scores[r.path] = scores.get(r.path, 0) + r.score * 0.5
                if r.path not in info:
                    info[r.path] = {"path": r.path, "snippet": r.snippet}

            sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            results = [
                {"path": p, "score": s, "snippet": info[p]["snippet"]}
                for p, s in sorted_results[:limit]
            ]
            return {"results": results, "count": len(results)}

        return {
            "results": [asdict(r) for r in results],
            "count": len(results)
        }

    # ========== 链接分析 ==========

    @mcp.tool(name="get_backlinks", description="获取笔记的反向链接")
    def get_backlinks(
        path: Annotated[str, Field(description="笔记路径")]
    ) -> dict:
        links = vault.get_links(path)
        return {
            "path": path,
            "backlinks": links.backlinks,
            "outgoing": links.outgoing,
        }

    # ========== 标签 ==========

    @mcp.tool(name="get_tags", description="获取标签或按标签查找")
    def get_tags(
        tag: Annotated[str | None, Field(default=None, description="指定标签则返回该标签的笔记")] = None,
    ) -> dict:
        if tag:
            notes = vault.find_by_tag(tag)
            return {"tag": tag, "notes": notes, "count": len(notes)}
        else:
            tags = vault.get_all_tags()
            return {"tags": tags, "count": len(tags)}

    # ========== Vault 分析 ==========

    @mcp.tool(name="find_orphans", description="查找孤立笔记")
    def find_orphans() -> dict:
        orphans = vault.find_orphans()
        return {"orphans": orphans, "count": len(orphans)}

    @mcp.tool(name="recent_notes", description="最近修改的笔记")
    def recent_notes(
        days: Annotated[int, Field(default=7, ge=1)] = 7,
        limit: Annotated[int, Field(default=20, ge=1, le=100)] = 20,
    ) -> dict:
        notes = vault.get_recent_notes(days, limit)
        return {"notes": notes, "count": len(notes)}

    # ========== Memory ==========

    @mcp.tool(name="memory_set", description="存储记忆")
    def memory_set(
        key: Annotated[str, Field(description="键")],
        value: Annotated[str, Field(description="值")],
        category: Annotated[str, Field(default="general")] = "general",
    ) -> dict:
        mem = memory.set(key, value, category)
        return asdict(mem)

    @mcp.tool(name="memory_get", description="获取记忆")
    def memory_get(key: Annotated[str, Field(description="键")]) -> dict:
        mem = memory.get(key)
        if mem:
            return asdict(mem)
        return {"error": "not found", "key": key}

    @mcp.tool(name="memory_list", description="列出记忆")
    def memory_list(
        category: Annotated[str, Field(default="general")] = "general",
    ) -> dict:
        memories = memory.list_by_category(category)
        return {"memories": [asdict(m) for m in memories], "count": len(memories)}

    @mcp.tool(name="memory_delete", description="删除记忆")
    def memory_delete(key: Annotated[str, Field(description="键")]) -> dict:
        deleted = memory.delete(key)
        return {"deleted": deleted, "key": key}

    # ========== 统计 ==========

    @mcp.tool(name="stats", description="统计信息")
    def stats() -> dict:
        return {
            "vault": {"notes": len(vault.list_notes())},
            "search": {
                "ready": state.is_ready(),
                "bm25": len(bm25.documents),
                "vector": vector.get_stats(),
            },
            "memory": memory.get_stats(),
        }

    return mcp


def main():
    """入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Obsidian Vault MCP Server")
    parser.add_argument("--vault", type=str, default=".", help="Vault 路径")
    args = parser.parse_args()

    vault_path = Path(args.vault).resolve()
    if not vault_path.exists():
        print(f"错误: 路径不存在 {vault_path}")
        exit(1)

    logger.info(f"启动服务: {vault_path}")
    mcp = create_server(vault_path)
    mcp.run()


if __name__ == "__main__":
    main()
