import requests
import json
import xml.etree.ElementTree as ET
from pathlib import Path


class GrobidProcessor:
    """Minimal GROBID processor for MVP"""

    def __init__(self, base_url="http://localhost:8070"):
        self.grobid_url = f"{base_url}/api/processFulltextDocument"

    def process_paper(self, pdf_path):
        """Extract structured sections from PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                files = {
                    'input': (Path(pdf_path).name, f, 'application/pdf')
                }
                response = requests.post(self.grobid_url, files=files, timeout=120)
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
            return None

        if response.status_code != 200:
            print(f"  Error: GROBID returned {response.status_code}")
            return None

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            print(f"  Error: Failed to parse XML - {e}")
            return None

        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

        paper = {
            'title': self._extract_text(root, './/tei:titleStmt/tei:title', ns),
            'abstract': self._extract_text(root, './/tei:abstract//tei:p', ns),
            'sections': [],
            'metadata': {
                'doi': self._extract_text(root, './/tei:idno[@type="DOI"]', ns),
                'year': self._extract_year(root, ns)
            }
        }

        for div in root.findall('.//tei:body//tei:div', ns):
            head = div.find('tei:head', ns)
            if head is None:
                continue

            section_title = ''.join(head.itertext()).strip()
            paragraphs = [''.join(p.itertext()).strip() for p in div.findall('.//tei:p', ns)]
            paragraphs = [p for p in paragraphs if p]

            if paragraphs:
                paper['sections'].append({
                    'title': section_title,
                    'type': self._classify_section(section_title),
                    'content': '\n\n'.join(paragraphs)
                })

        return paper

    def _extract_text(self, root, xpath, ns):
        """Extract text from XML element, including nested elements"""
        elem = root.find(xpath, ns)
        return ''.join(elem.itertext()).strip() if elem is not None else ''

    def _extract_year(self, root, ns):
        """Extract year from XML element"""
        date = root.find('.//tei:publicationStmt//tei:date', ns)
        if date is not None and 'when' in date.attrib:
            return date.attrib['when'][:4]
        return None

    def _classify_section(self, title):
        """Quick classification of section types"""
        title_lower = title.lower()
        if any(w in title_lower for w in ['method', 'approach', 'model']):
            return 'methodology'
        elif any(w in title_lower for w in ['result', 'finding']):
            return 'results'
        elif any(w in title_lower for w in ['discuss', 'conclusion']):
            return 'discussion'
        elif 'intro' in title_lower:
            return 'introduction'
        return 'other'


def process_all_papers(pdf_directory):
    """Process all papers in a directory using GROBID"""
    processor = GrobidProcessor()
    papers = []
    failed = []

    pdf_files = list(Path(pdf_directory).glob('*.pdf'))
    total = len(pdf_files)
    print(f"Processing {total} PDFs...")

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{total}] {pdf_path.name}", end=" ")
        paper = processor.process_paper(pdf_path)
        if paper:
            papers.append(paper)
            print(f"-> {len(paper['sections'])} sections")
        else:
            failed.append(pdf_path.name)
            print("-> FAILED")

    
    output_dir = Path(pdf_directory).parent / 'outputs' / 'grobid_processed_papers'
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'processed_papers.json', 'w') as f:
        json.dump(papers, f, indent=2)

    if failed:
        with open(output_dir / 'failed_papers.json', 'w') as f:
            json.dump(failed, f, indent=2)
    
    print(f"\nDone: {len(papers)} successful, {len(failed)} failed")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    process_all_papers(script_dir / 'pdf_pub')
