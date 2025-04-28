from .arxiv_fetcher import ArxivFetcher
from .venturebeat_fetcher import VenturebeatFetcher

__all__ = ['ArxivFetcher', 'VenturebeatFetcher', 'create_fetcher']


def create_fetcher(source_config):
    """创建适合特定源的抓取器"""
    parser_type = source_config.get("parser", "").lower()
    
    if parser_type == "arxiv":
        return ArxivFetcher(source_config)
    elif parser_type == "venturebeat":
        return VenturebeatFetcher(source_config)
    else:
        raise ValueError(f"不支持的解析器类型: {parser_type}") 