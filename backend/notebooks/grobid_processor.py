import requests
import xml.etree.ElementTree as ET
from pathlib import Path

class GrobidProcessor:
    """
    Minimal GROBID processor for MVP
    Following Aytar et al.'s approach
    """

    def __init__(self, base_url="http://localhost:8070"):
        self.grobid_url = f"{base_url}/api/processFulltextDocument"

    def process_paper(self, pdf_path):
        """
        Extract structured sections from PDF
        """
        with open(pdf_path, 'rb') as f:
            response = requests.post(
                self.grobid_url, 
                files={'input': f},
                timeout=120
            )

        if response.status_code != 200:
            return None

        # Parse XML
        root = ET.fromstring(response.content)
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

        # Extract key components
        paper = {
            'title': self._extract_text(root, './/tei:titleStmt/tei:title', ns),
            'abstract': self._extract_text(root, './/tei:abstract/tei:div/tei:p', ns),
            'sections': [],
            'metadata': {
                'doi': self._extract_text(root, './/tei:idno[@type="DOI"]', ns),
                'year': self._extract_year(root, ns)
            }
        }

        # Extract sections
        for div in root.findall('.//tei:body//tei:div', ns):
            head = div.find('tei:head', ns)
            if head is None:
                continue
            
            section_title = head.text or ''
            paragraphs = [p.text for p in div.findall('.//tei:p', ns) if p.text]
            
            if paragraphs:
                paper['sections'].append({
                    'title': section_title,
                    'type': self._classify_section(section_title),
                    'content': '\n\n'.join(paragraphs)
                })

        return paper
        
    def _extract_text(self, root, xpath, ns):
        """Extract text from XML element"""
        elem = root.find(xpath, ns)
        return elem.text if elem is not None and elem.text else ''
    
    def _extract_year(self, root, ns):
        """Extract year from XML element"""
        date = root.find('.//tei:publicationStmt//tei:date', ns)
        if date is not None and 'when' in date.attrib:
            return date.attrib['when'][:4]  # Get year
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
        else:
            return 'other'

# Process all papers
def process_all_papers(pdf_directory):
    processor = GrobidProcessor()
    papers = []
    
    pdf_files = list(Path(pdf_directory).glob('*.pdf'))
    print(f"Processing {len(pdf_files)} papers...")
    
    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name}...")
        paper = processor.process_paper(pdf_path)
        if paper:
            papers.append(paper)
    
    print(f"Successfully processed {len(papers)} papers")
    return papers

# Run it
processed_papers = process_all_papers('./pdf_pub')