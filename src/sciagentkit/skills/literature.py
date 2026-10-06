from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd

from sciagentkit.core.http import SciAgentHttpError, request_json, request_text
from sciagentkit.core.manifest import write_manifest

EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def search_europe_pmc(query: str, page_size: int = 20) -> pd.DataFrame:
    data = request_json(EUROPE_PMC_URL, params={"query": query, "format": "json", "pageSize": page_size, "resultType": "core"})
    rows = []
    for item in data.get("resultList", {}).get("result", []):
        rows.append({
            "source": "EuropePMC", "title": item.get("title"), "authors": item.get("authorString"),
            "journal": item.get("journalTitle"), "year": item.get("pubYear"), "doi": item.get("doi"),
            "pmid": item.get("pmid"), "pmcid": item.get("pmcid"), "abstract": item.get("abstractText"),
        })
    return pd.DataFrame(rows)


def search_pubmed(query: str, retmax: int = 20) -> pd.DataFrame:
    search_xml = request_text(PUBMED_ESEARCH_URL, params={"db": "pubmed", "term": query, "retmax": retmax, "retmode": "xml"})
    root = ET.fromstring(search_xml)
    ids = [node.text for node in root.findall(".//Id") if node.text]
    if not ids:
        return pd.DataFrame(columns=["source", "pmid", "title", "journal", "year", "abstract"])
    fetch_xml = request_text(PUBMED_EFETCH_URL, params={"db": "pubmed", "id": ",".join(ids), "retmode": "xml"})
    root = ET.fromstring(fetch_xml)
    rows = []
    for article in root.findall(".//PubmedArticle"):
        abstract_parts = [node.text or "" for node in article.findall(".//AbstractText")]
        rows.append({
            "source": "PubMed", "pmid": article.findtext(".//PMID"),
            "title": article.findtext(".//ArticleTitle") or "", "journal": article.findtext(".//Journal/Title"),
            "year": article.findtext(".//PubDate/Year") or article.findtext(".//PubDate/MedlineDate"),
            "abstract": " ".join(abstract_parts),
        })
    return pd.DataFrame(rows)


def literature_search(query: str, out_dir: str | Path, max_results: int = 20, source: str = "europepmc") -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        if source.lower() == "pubmed":
            df = search_pubmed(query, retmax=max_results)
        elif source.lower() in {"europepmc", "europe_pmc"}:
            df = search_europe_pmc(query, page_size=max_results)
        else:
            df = pd.concat([search_europe_pmc(query, page_size=max_results), search_pubmed(query, retmax=max_results)], ignore_index=True)
    except SciAgentHttpError as exc:
        df = pd.DataFrame([{"source": source, "query": query, "error": str(exc)}])
    df.to_csv(out / "literature_results.csv", index=False)
    write_manifest(out, [], command=f"sciagent literature-search '{query}' --out {out}", parameters={"query": query, "source": source, "max_results": max_results}, workflow_name="literature_search")
    return {"output_dir": str(out), "summary": {"query": query, "results": len(df), "source": source}, "generated_files": ["literature_results.csv", "run_manifest.json"]}
