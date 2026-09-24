from zotero_arxiv_daily.retriever.arxiv_retriever import ArxivRetriever
import zotero_arxiv_daily.retriever.arxiv_retriever as arxiv_retriever
import feedparser
import pickle
from types import SimpleNamespace
from urllib.error import ContentTooShortError

def test_arxiv_retriever(config, monkeypatch):

    parsed_result = feedparser.parse("tests/retriever/arxiv_rss_example.xml")
    raw_parser = feedparser.parse
    def mock_feedparser_parse(url):
        if url == f"https://rss.arxiv.org/atom/{'+'.join(config.source.arxiv.category)}":
            return parsed_result
        return raw_parser(url)
    monkeypatch.setattr(feedparser, "parse", mock_feedparser_parse)
    
    retriever = ArxivRetriever(config)
    papers = retriever.retrieve_papers()
    parsed_results = [i for i in parsed_result.entries if i.get("arxiv_announce_type","new") == 'new']
    assert len(papers) == len(parsed_results)
    paper_titles = [i.title for i in papers]
    parsed_titles = [i.title for i in parsed_results]
    assert set(paper_titles) == set(parsed_titles)


def test_extract_text_from_pdf_returns_none_when_download_fails(monkeypatch):
    def mock_urlretrieve(*args, **kwargs):
        raise ContentTooShortError("partial content", b"partial")

    monkeypatch.setattr(arxiv_retriever, "urlretrieve", mock_urlretrieve)

    paper = SimpleNamespace(title="test paper", pdf_url="https://example.com/paper.pdf")
    assert arxiv_retriever.extract_text_from_pdf(paper) is None