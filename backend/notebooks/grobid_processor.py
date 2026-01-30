import requests
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GrobidProcessor:
    """
    Minimal GROBID processor for MVP
    Following Aytar et al.'s approach
    """

    def __init__(self, base_url="http://localhost:8070"):
        self.grobid_url = f"{base_url}/api/processFulltextDocument"
        logger.debug(f"Initialized GrobidProcessor with URL: {self.grobid_url}")

    def process_paper(self, pdf_path):
        """
        Extract structured sections from PDF
        """
        logger.debug(f"Starting to process PDF: {pdf_path}")

        try:
            with open(pdf_path, 'rb') as f:
                logger.debug(f"Sending request to GROBID at {self.grobid_url}")
                files = {
                    'input': (
                        Path(pdf_path).name,
                        f,
                        'application/pdf'
                    )
                }
                response = requests.post(
                    self.grobid_url,
                    files=files,
                    timeout=120
                )
                logger.debug(f"GROBID response status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to GROBID failed: {e}")
            return None

        if response.status_code != 200:
            logger.error(f"GROBID returned non-200 status: {response.status_code}")
            logger.debug(f"Response content: {response.content[:500]}")
            return None

        # Parse XML
        logger.debug("Parsing XML response from GROBID")
        try:
            root = ET.fromstring(response.content)
            logger.debug("XML parsed successfully")
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML: {e}")
            logger.debug(f"Raw response content: {response.content[:1000]}")
            return None

        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

        # Extract key components
        title = self._extract_text(root, './/tei:titleStmt/tei:title', ns)
        abstract = self._extract_text(root, './/tei:abstract//tei:p', ns)
        doi = self._extract_text(root, './/tei:idno[@type="DOI"]', ns)
        year = self._extract_year(root, ns)

        logger.debug(f"Extracted title: {title[:100] if title else 'None'}...")
        logger.debug(f"Extracted abstract length: {len(abstract) if abstract else 0} chars")
        logger.debug(f"Extracted DOI: {doi}")
        logger.debug(f"Extracted year: {year}")

        paper = {
            'title': title,
            'abstract': abstract,
            'sections': [],
            'metadata': {
                'doi': doi,
                'year': year
            }
        }

        # Extract sections
        divs = root.findall('.//tei:body//tei:div', ns)
        logger.debug(f"Found {len(divs)} div elements in body")

        for div in divs:
            head = div.find('tei:head', ns)
            if head is None:
                logger.debug("Skipping div without head element")
                continue

            section_title = ''.join(head.itertext()).strip() or ''
            paragraphs = [''.join(p.itertext()).strip() for p in div.findall('.//tei:p', ns)]
            paragraphs = [p for p in paragraphs if p]

            logger.debug(f"Section '{section_title}': {len(paragraphs)} paragraphs")

            if paragraphs:
                section_type = self._classify_section(section_title)
                logger.debug(f"Classified section '{section_title}' as '{section_type}'")
                paper['sections'].append({
                    'title': section_title,
                    'type': section_type,
                    'content': '\n\n'.join(paragraphs)
                })

        logger.info(f"Successfully processed {pdf_path}: {len(paper['sections'])} sections extracted")
        return paper
        
    def _extract_text(self, root, xpath, ns):
        """Extract text from XML element, including nested elements"""
        elem = root.find(xpath, ns)
        result = ''.join(elem.itertext()).strip() if elem is not None else ''
        logger.debug(f"_extract_text({xpath}): found={'yes' if elem is not None else 'no'}, len={len(result)}")
        return result
    
    def _extract_year(self, root, ns):
        """Extract year from XML element"""
        date = root.find('.//tei:publicationStmt//tei:date', ns)
        logger.debug(f"_extract_year: date element found={'yes' if date is not None else 'no'}")
        if date is not None:
            logger.debug(f"_extract_year: date attribs={date.attrib}")
            if 'when' in date.attrib:
                year = date.attrib['when'][:4]
                logger.debug(f"_extract_year: extracted year={year}")
                return year
        logger.debug("_extract_year: no year found")
        return None
    
    def _classify_section(self, title):
        """Quick classification of section types"""
        title_lower = title.lower()
        logger.debug(f"_classify_section: classifying '{title}'")

        if any(w in title_lower for w in ['method', 'approach', 'model']):
            logger.debug(f"_classify_section: matched methodology keywords")
            return 'methodology'
        elif any(w in title_lower for w in ['result', 'finding']):
            logger.debug(f"_classify_section: matched results keywords")
            return 'results'
        elif any(w in title_lower for w in ['discuss', 'conclusion']):
            logger.debug(f"_classify_section: matched discussion keywords")
            return 'discussion'
        elif 'intro' in title_lower:
            logger.debug(f"_classify_section: matched introduction keyword")
            return 'introduction'
        else:
            logger.debug(f"_classify_section: no match, returning 'other'")
            return 'other'

# Process all papers
def process_all_papers(pdf_directory):
    logger.info(f"Starting batch processing from directory: {pdf_directory}")
    processor = GrobidProcessor()
    papers = []
    failed = []

    pdf_files = list(Path(pdf_directory).glob('*.pdf'))
    logger.info(f"Found {len(pdf_files)} PDF files to process")

    for i, pdf_path in enumerate(pdf_files, 1):
        logger.info(f"Processing [{i}/{len(pdf_files)}]: {pdf_path.name}")
        paper = processor.process_paper(pdf_path)
        if paper:
            papers.append(paper)
            logger.debug(f"Successfully added paper: {paper.get('title', 'Unknown')[:50]}...")
        else:
            failed.append(pdf_path.name)
            logger.warning(f"Failed to process: {pdf_path.name}")

    logger.info(f"Batch processing complete: {len(papers)} successful, {len(failed)} failed")
    if failed:
        logger.warning(f"Failed files: {failed}")
    return papers

# Run it
if __name__ == "__main__":
    processed_papers = process_all_papers('./pdf_pub')
    with open('processed_papers.json', 'w') as f:
        json.dump(processed_papers, f, indent=2)
    logger.info(f"Final result: {len(processed_papers)} papers processed")