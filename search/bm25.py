"""BM25 关键词搜索"""

import re
from dataclasses import dataclass
from rank_bm25 import BM25Okapi
import jieba


@dataclass
class SearchResult:
    """搜索结果"""
    path: str
    score: float
    snippet: str


class BM25Search:
    """BM25 搜索引擎"""

    def __init__(self):
        self.documents: dict[str, str] = {}  # path -> content
        self.paths: list[str] = []
        self.bm25: BM25Okapi | None = None

    def _tokenize(self, text: str) -> list[str]:
        """中文分词"""
        # 简单清理
        text = re.sub(r'[#\[\](){}]', ' ', text)
        return list(jieba.cut(text))

    def _get_snippet(self, content: str, query: str, max_len: int = 150) -> str:
        """提取包含查询词的片段"""
        query_terms = set(self._tokenize(query.lower()))
        lines = content.split('\n')

        for line in lines:
            line_lower = line.lower()
            if any(term in line_lower for term in query_terms if len(term) > 1):
                if len(line) > max_len:
                    return line[:max_len] + "..."
                return line

        # 没找到就返回开头
        return content[:max_len] + "..." if len(content) > max_len else content

    def index(self, documents: dict[str, str]):
        """建立索引"""
        self.documents = documents
        self.paths = list(documents.keys())

        if not self.paths:
            self.bm25 = None
            return

        tokenized = [self._tokenize(documents[p]) for p in self.paths]
        self.bm25 = BM25Okapi(tokenized)

    def add(self, path: str, content: str):
        """添加单个文档"""
        self.documents[path] = content
        # 重建索引（BM25 不支持增量）
        self.index(self.documents)

    def remove(self, path: str):
        """移除文档"""
        if path in self.documents:
            del self.documents[path]
            self.index(self.documents)

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """搜索"""
        if not self.bm25 or not self.paths:
            return []

        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)

        # 排序并取 top-k
        ranked = sorted(zip(self.paths, scores), key=lambda x: x[1], reverse=True)

        results = []
        for path, score in ranked[:limit]:
            if score > 0:
                content = self.documents.get(path, "")
                results.append(SearchResult(
                    path=path,
                    score=float(score),
                    snippet=self._get_snippet(content, query),
                ))

        return results
