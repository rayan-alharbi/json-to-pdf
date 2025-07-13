#!/usr/bin/env python3
import json
import os
import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import hashlib
import random

# Third-party imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, blue, gray
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus import PageBreak, KeepTogether
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from tqdm import tqdm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: ReportLab not installed. Install with: pip install reportlab")


@dataclass
class ConversionStats:
    """Statistics tracking for the conversion process."""
    start_time: datetime
    total_items: int
    files_created: int
    errors: List[str]
    warnings: List[str]
    
    def __post_init__(self):
        self.end_time = None
        self.duration = None
    
    def finish(self):
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time


class JSONAnalyzer:
    """Intelligent JSON structure analyzer and content distributor."""
    
    def __init__(self, data: Union[Dict, List, Any]):
        self.data = data
        self.structure_type = self._determine_structure()
        self.total_items = self._count_items()
        self.complexity_score = self._calculate_complexity()
    
    def _determine_structure(self) -> str:
        """Determine the primary structure of the JSON data."""
        if isinstance(self.data, list):
            return "array"
        elif isinstance(self.data, dict):
            return "object"
        else:
            return "primitive"
    
    def _count_items(self) -> int:
        """Count total items for intelligent distribution."""
        if isinstance(self.data, list):
            return len(self.data)
        elif isinstance(self.data, dict):
            return len(self.data)
        else:
            return 1
    
    def _calculate_complexity(self) -> float:
        """Calculate complexity score for adaptive formatting."""
        def _recursive_complexity(obj, depth=0):
            if depth > 10:  # Prevent infinite recursion
                return 1
            
            if isinstance(obj, dict):
                return sum(_recursive_complexity(v, depth + 1) for v in obj.values()) + len(obj)
            elif isinstance(obj, list):
                return sum(_recursive_complexity(item, depth + 1) for item in obj) + len(obj)
            else:
                return 1
        
        return _recursive_complexity(self.data)
    
    def create_chunks(self, num_chunks: int = 40) -> List[Dict[str, Any]]:
        """Create intelligent chunks with metadata."""
        chunks = []
        
        if self.structure_type == "array":
            chunks = self._chunk_array(num_chunks)
        elif self.structure_type == "object":
            chunks = self._chunk_object(num_chunks)
        else:
            chunks = self._chunk_primitive(num_chunks)
        
        # Add metadata and ensure we have exactly num_chunks
        return self._normalize_chunks(chunks, num_chunks)
    
    def _chunk_array(self, num_chunks: int) -> List[Dict[str, Any]]:
        """Intelligently chunk array data."""
        array_data = self.data
        chunk_size = max(1, len(array_data) // num_chunks)
        chunks = []
        
        for i in range(0, len(array_data), chunk_size):
            chunk_data = array_data[i:i + chunk_size]
            chunks.append({
                'type': 'array_chunk',
                'data': chunk_data,
                'original_indices': list(range(i, min(i + chunk_size, len(array_data)))),
                'size': len(chunk_data)
            })
        
        return chunks
    
    def _chunk_object(self, num_chunks: int) -> List[Dict[str, Any]]:
        """Intelligently chunk object data."""
        obj_data = self.data
        items = list(obj_data.items())
        chunk_size = max(1, len(items) // num_chunks)
        chunks = []
        
        for i in range(0, len(items), chunk_size):
            chunk_items = items[i:i + chunk_size]
            chunks.append({
                'type': 'object_chunk',
                'data': dict(chunk_items),
                'keys': [k for k, v in chunk_items],
                'size': len(chunk_items)
            })
        
        return chunks
    
    def _chunk_primitive(self, num_chunks: int) -> List[Dict[str, Any]]:
        """Handle primitive data by replication with variations."""
        chunks = []
        for i in range(num_chunks):
            chunks.append({
                'type': 'primitive_chunk',
                'data': self.data,
                'variation': i + 1,
                'size': 1
            })
        return chunks
    
    def _normalize_chunks(self, chunks: List[Dict], target_count: int) -> List[Dict[str, Any]]:
        """Ensure exactly target_count chunks through intelligent distribution."""
        if len(chunks) == target_count:
            return chunks
        
        if len(chunks) < target_count:
            # Duplicate chunks creatively
            while len(chunks) < target_count:
                # Select chunk to duplicate based on size and complexity
                chunk_to_duplicate = min(chunks, key=lambda x: x['size'])
                new_chunk = chunk_to_duplicate.copy()
                new_chunk['is_duplicate'] = True
                new_chunk['duplicate_id'] = len(chunks)
                chunks.append(new_chunk)
        
        elif len(chunks) > target_count:
            # Merge chunks intelligently
            while len(chunks) > target_count:
                # Find two smallest chunks to merge
                chunks.sort(key=lambda x: x['size'])
                chunk1, chunk2 = chunks[:2]
                
                merged_chunk = {
                    'type': 'merged_chunk',
                    'data': [chunk1['data'], chunk2['data']],
                    'original_types': [chunk1['type'], chunk2['type']],
                    'size': chunk1['size'] + chunk2['size']
                }
                
                chunks = [merged_chunk] + chunks[2:]
        
        # Add final metadata
        for i, chunk in enumerate(chunks):
            chunk['chunk_id'] = i + 1
            chunk['total_chunks'] = target_count
            chunk['hash'] = hashlib.md5(str(chunk['data']).encode()).hexdigest()[:8]
        
        return chunks


class PDFGenerator:
    """Advanced PDF generator with creative formatting."""
    
    def __init__(self, output_dir: str = "output_pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.styles = self._create_custom_styles()
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation")
    
    def _create_custom_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles for beautiful PDFs."""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=HexColor('#2E4057'),
                alignment=TA_CENTER
            ),
            'ChunkHeader': ParagraphStyle(
                'ChunkHeader',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=20,
                textColor=HexColor('#048A81'),
                alignment=TA_LEFT
            ),
            'MetaData': ParagraphStyle(
                'MetaData',
                parent=styles['Normal'],
                fontSize=10,
                textColor=gray,
                alignment=TA_CENTER,
                spaceAfter=20
            ),
            'JSONContent': ParagraphStyle(
                'JSONContent',
                parent=styles['Code'],
                fontSize=9,
                leftIndent=20,
                fontName='Courier',
                textColor=HexColor('#2C3E50')
            ),
            'KeyStyle': ParagraphStyle(
                'KeyStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=HexColor('#E74C3C'),
                fontName='Helvetica-Bold'
            )
        }
        
        return custom_styles
    
    def generate_pdf(self, chunk_data: Dict[str, Any], filename: str) -> bool:
        """Generate a single PDF file with creative formatting."""
        try:
            filepath = self.output_dir / filename
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            # Title page
            story.extend(self._create_title_page(chunk_data))
            
            # Content pages
            story.extend(self._create_content_pages(chunk_data))
            
            # Footer with metadata
            story.extend(self._create_footer(chunk_data))
            
            doc.build(story)
            return True
            
        except Exception as e:
            logging.error(f"Error generating PDF {filename}: {str(e)}")
            return False
    
    def _create_title_page(self, chunk_data: Dict[str, Any]) -> List[Any]:
        """Create an attractive title page."""
        story = []
        
        # Main title
        title = f"JSON Data Chunk {chunk_data['chunk_id']}"
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Metadata table
        metadata = [
            ['Chunk ID', f"{chunk_data['chunk_id']}/{chunk_data['total_chunks']}"],
            ['Data Type', chunk_data['type'].replace('_', ' ').title()],
            ['Content Size', str(chunk_data['size'])],
            ['Hash ID', chunk_data['hash']],
            ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        if 'is_duplicate' in chunk_data:
            metadata.append(['Note', 'Duplicate chunk for equal distribution'])
        
        table = Table(metadata, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FFFFFF')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#E0E0E0'))
        ]))
        
        story.append(table)
        story.append(PageBreak())
        
        return story
    
    def _create_content_pages(self, chunk_data: Dict[str, Any]) -> List[Any]:
        """Create formatted content pages."""
        story = []
        
        story.append(Paragraph("Data Content", self.styles['ChunkHeader']))
        story.append(Spacer(1, 20))
        
        # Format JSON content based on type
        if chunk_data['type'] == 'array_chunk':
            story.extend(self._format_array_content(chunk_data))
        elif chunk_data['type'] == 'object_chunk':
            story.extend(self._format_object_content(chunk_data))
        elif chunk_data['type'] == 'merged_chunk':
            story.extend(self._format_merged_content(chunk_data))
        else:
            story.extend(self._format_generic_content(chunk_data))
        
        return story
    
    def _format_array_content(self, chunk_data: Dict[str, Any]) -> List[Any]:
        """Format array content with creative styling and size limits."""
        story = []
        data = chunk_data['data']
        
        # Limit items per PDF to prevent memory issues
        max_items_per_pdf = 100
        total_items = len(data)
        
        if total_items > max_items_per_pdf:
            story.append(Paragraph(f"Array Items (showing first {max_items_per_pdf} of {total_items} items)", self.styles['KeyStyle']))
            data = data[:max_items_per_pdf]
            story.append(Paragraph(f"⚠️ Large dataset truncated for PDF generation", self.styles['MetaData']))
        else:
            story.append(Paragraph(f"Array Items ({total_items} items)", self.styles['KeyStyle']))
        
        story.append(Spacer(1, 12))
        
        for i, item in enumerate(data):
            # Item header
            item_header = f"Item {i + 1}"
            story.append(Paragraph(item_header, self.styles['KeyStyle']))
            
            # Item content with size limits
            try:
                if isinstance(item, (dict, list)):
                    json_str = json.dumps(item, indent=2, ensure_ascii=False)
                    # Limit JSON string length to prevent huge PDFs
                    if len(json_str) > 2000:
                        json_str = json_str[:2000] + "\n... (truncated)"
                    
                    # Split long JSON into chunks for better formatting
                    lines = json_str.split('\n')
                    for line_chunk in self._chunk_lines(lines, 30):  # Reduced from 50 to 30
                        content = '\n'.join(line_chunk)
                        story.append(Paragraph(f"<pre>{self._escape_xml(content)}</pre>", self.styles['JSONContent']))
                else:
                    item_str = str(item)
                    if len(item_str) > 1000:
                        item_str = item_str[:1000] + "... (truncated)"
                    story.append(Paragraph(self._escape_xml(item_str), self.styles['JSONContent']))
            except Exception as e:
                story.append(Paragraph(f"Error formatting item: {str(e)}", self.styles['JSONContent']))
            
            story.append(Spacer(1, 8))  # Reduced spacing
            
            # Add page break every 20 items to prevent memory issues
            if (i + 1) % 20 == 0 and i < len(data) - 1:
                story.append(PageBreak())
        
        return story
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters for PDF content."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def _format_object_content(self, chunk_data: Dict[str, Any]) -> List[Any]:
        """Format object content with key-value styling and size limits."""
        story = []
        data = chunk_data['data']
        
        # Limit properties per PDF
        max_props_per_pdf = 50
        total_props = len(data)
        
        if total_props > max_props_per_pdf:
            story.append(Paragraph(f"Object Properties (showing first {max_props_per_pdf} of {total_props} keys)", self.styles['KeyStyle']))
            data = dict(list(data.items())[:max_props_per_pdf])
            story.append(Paragraph(f"⚠️ Large object truncated for PDF generation", self.styles['MetaData']))
        else:
            story.append(Paragraph(f"Object Properties ({total_props} keys)", self.styles['KeyStyle']))
        
        story.append(Spacer(1, 12))
        
        for i, (key, value) in enumerate(data.items()):
            # Key header
            key_str = str(key)[:100]  # Limit key length
            story.append(Paragraph(f"Key: {self._escape_xml(key_str)}", self.styles['KeyStyle']))
            
            # Value content with size limits
            try:
                if isinstance(value, (dict, list)):
                    json_str = json.dumps(value, indent=2, ensure_ascii=False)
                    # Limit JSON string length
                    if len(json_str) > 2000:
                        json_str = json_str[:2000] + "\n... (truncated)"
                    
                    lines = json_str.split('\n')
                    for line_chunk in self._chunk_lines(lines, 30):
                        content = '\n'.join(line_chunk)
                        story.append(Paragraph(f"<pre>{self._escape_xml(content)}</pre>", self.styles['JSONContent']))
                else:
                    value_str = str(value)
                    if len(value_str) > 1000:
                        value_str = value_str[:1000] + "... (truncated)"
                    story.append(Paragraph(self._escape_xml(value_str), self.styles['JSONContent']))
            except Exception as e:
                story.append(Paragraph(f"Error formatting value: {str(e)}", self.styles['JSONContent']))
            
            story.append(Spacer(1, 8))
            
            # Add page break every 15 properties
            if (i + 1) % 15 == 0 and i < len(data) - 1:
                story.append(PageBreak())
        
        return story
    
    def _format_merged_content(self, chunk_data: Dict[str, Any]) -> List[Any]:
        """Format merged content with clear separation."""
        story = []
        
        story.append(Paragraph("Merged Content", self.styles['KeyStyle']))
        story.append(Spacer(1, 12))
        
        for i, data_part in enumerate(chunk_data['data']):
            story.append(Paragraph(f"Part {i + 1}", self.styles['KeyStyle']))
            json_str = json.dumps(data_part, indent=2, ensure_ascii=False)
            lines = json_str.split('\n')
            for line_chunk in self._chunk_lines(lines, 50):
                content = '\n'.join(line_chunk)
                story.append(Paragraph(f"<pre>{content}</pre>", self.styles['JSONContent']))
            story.append(Spacer(1, 20))
        
        return story
    
    def _format_generic_content(self, chunk_data: Dict[str, Any]) -> List[Any]:
        """Format generic content."""
        story = []
        
        json_str = json.dumps(chunk_data['data'], indent=2, ensure_ascii=False)
        lines = json_str.split('\n')
        for line_chunk in self._chunk_lines(lines, 50):
            content = '\n'.join(line_chunk)
            story.append(Paragraph(f"<pre>{content}</pre>", self.styles['JSONContent']))
        
        return story
    
    def _chunk_lines(self, lines: List[str], chunk_size: int) -> List[List[str]]:
        """Split lines into chunks for better PDF formatting."""
        return [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
    
    def _create_footer(self, chunk_data: Dict[str, Any]) -> List[Any]:
        """Create footer with generation info."""
        story = []
        
        story.append(Spacer(1, 30))
        footer_text = f"Generated by Advanced JSON to PDF Splitter | Chunk {chunk_data['chunk_id']}/{chunk_data['total_chunks']}"
        story.append(Paragraph(footer_text, self.styles['MetaData']))
        
        return story


class JSONToPDFConverter:
    """Main converter class orchestrating the entire process."""
    
    def __init__(self, input_file: str = "test.json", output_dir: str = "output_pdfs", num_files: int = 40):
        self.input_file = Path(input_file)
        self.output_dir = output_dir
        self.num_files = num_files
        self.stats = None
        self.force_sequential = False
        self.timeout = 300
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"json_pdf_conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def convert(self) -> bool:
        """Main conversion process with comprehensive error handling."""
        try:
            self.logger.info("Starting JSON to PDF conversion process")
            self.stats = ConversionStats(
                start_time=datetime.now(),
                total_items=0,
                files_created=0,
                errors=[],
                warnings=[]
            )
            
            # Step 1: Load and analyze JSON
            self.logger.info(f"Loading JSON file: {self.input_file}")
            json_data = self._load_json()
            
            # Step 2: Analyze and create chunks
            self.logger.info("Analyzing JSON structure and creating chunks")
            analyzer = JSONAnalyzer(json_data)
            chunks = analyzer.create_chunks(self.num_files)
            
            self.stats.total_items = len(chunks)
            self.logger.info(f"Created {len(chunks)} chunks from {analyzer.structure_type} data")
            
            # Step 3: Generate PDFs
            self.logger.info("Starting PDF generation")
            self._generate_pdfs(chunks)
            
            # Step 4: Generate summary
            self.stats.finish()
            self._generate_summary()
            
            self.logger.info("Conversion completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _load_json(self) -> Union[Dict, List, Any]:
        """Load and validate JSON file with comprehensive error handling."""
        try:
            if not self.input_file.exists():
                raise FileNotFoundError(f"Input file {self.input_file} does not exist")
            
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                raise ValueError("JSON file is empty")
            
            # Try to parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON format: {str(e)}")
                # Try to fix common JSON issues
                data = self._attempt_json_repair(content)
            
            self.logger.info(f"Successfully loaded JSON with {self._count_json_items(data)} items")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON: {str(e)}")
            raise
    
    def _attempt_json_repair(self, content: str) -> Union[Dict, List, Any]:
        """Attempt to repair common JSON issues."""
        self.logger.warning("Attempting to repair malformed JSON")
        
        # Common fixes
        fixes = [
            lambda x: x.replace("'", '"'),  # Single quotes to double quotes
            lambda x: x.replace('True', 'true'),  # Python True to JSON true
            lambda x: x.replace('False', 'false'),  # Python False to JSON false
            lambda x: x.replace('None', 'null'),  # Python None to JSON null
        ]
        
        for fix in fixes:
            try:
                fixed_content = fix(content)
                return json.loads(fixed_content)
            except json.JSONDecodeError:
                continue
        
        raise ValueError("Unable to repair JSON format")
    
    def _count_json_items(self, data: Union[Dict, List, Any]) -> int:
        """Count items in JSON data."""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return len(data)
        else:
            return 1
    
    def _generate_pdfs(self, chunks: List[Dict[str, Any]]):
        """Generate PDFs with improved progress tracking and error handling."""
        pdf_generator = PDFGenerator(self.output_dir)
        
        # Create file tasks
        tasks = []
        for i, chunk in enumerate(chunks):
            filename = f"output_{i+1:02d}.pdf"
            tasks.append((chunk, filename))
        
        self.logger.info(f"Starting PDF generation for {len(tasks)} files...")
        
        # Process with detailed progress tracking
        with tqdm(total=len(tasks), desc="Generating PDFs", unit="file", ncols=100) as pbar:
            
            # Option 1: Try parallel processing first (unless forced sequential)
            if len(tasks) > 1 and not self.force_sequential:
                try:
                    self._generate_pdfs_parallel(pdf_generator, tasks, pbar)
                except Exception as e:
                    self.logger.warning(f"Parallel processing failed: {str(e)}")
                    self.logger.info("Falling back to sequential processing...")
                    pbar.reset()  # Reset progress bar
                    self._generate_pdfs_sequential(pdf_generator, tasks, pbar)
            else:
                self._generate_pdfs_sequential(pdf_generator, tasks, pbar)
    
    def _generate_pdfs_parallel(self, pdf_generator, tasks, pbar):
        """Generate PDFs using parallel processing."""
        # Reduce max workers for large datasets
        max_workers = min(2, len(tasks))  # Reduced from 4 to 2 for stability
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(pdf_generator.generate_pdf, chunk, filename): (chunk, filename)
                for chunk, filename in tasks
            }
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                chunk, filename = future_to_task[future]
                try:
                    success = future.result(timeout=self.timeout)  # Use configurable timeout
                    if success:
                        self.stats.files_created += 1
                        self.logger.info(f"✅ Generated {filename}")
                    else:
                        self.stats.errors.append(f"Failed to generate {filename}")
                        self.logger.error(f"❌ Failed to generate {filename}")
                except Exception as e:
                    error_msg = f"Error generating {filename}: {str(e)}"
                    self.stats.errors.append(error_msg)
                    self.logger.error(f"❌ {error_msg}")
                
                pbar.update(1)
                pbar.set_postfix({"Created": self.stats.files_created, "Errors": len(self.stats.errors)})
    
    def _generate_pdfs_sequential(self, pdf_generator, tasks, pbar):
        """Generate PDFs sequentially (fallback method)."""
        for i, (chunk, filename) in enumerate(tasks):
            try:
                self.logger.info(f"Processing file {i+1}/{len(tasks)}: {filename}")
                success = pdf_generator.generate_pdf(chunk, filename)
                
                if success:
                    self.stats.files_created += 1
                    self.logger.info(f"✅ Generated {filename}")
                else:
                    self.stats.errors.append(f"Failed to generate {filename}")
                    self.logger.error(f"❌ Failed to generate {filename}")
                    
            except Exception as e:
                error_msg = f"Error generating {filename}: {str(e)}"
                self.stats.errors.append(error_msg)
                self.logger.error(f"❌ {error_msg}")
            
            pbar.update(1)
            pbar.set_postfix({"Created": self.stats.files_created, "Errors": len(self.stats.errors)})
            
            # Add small delay to prevent overwhelming the system
            import time
            time.sleep(0.1)
    
    def _generate_summary(self):
        """Generate comprehensive summary report."""
        summary_file = Path(self.output_dir) / "conversion_summary.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("JSON to PDF Conversion Summary\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Conversion Date: {self.stats.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {self.stats.duration}\n")
            f.write(f"Input File: {self.input_file}\n")
            f.write(f"Output Directory: {self.output_dir}\n\n")
            
            f.write("Results:\n")
            f.write(f"  Total Chunks: {self.stats.total_items}\n")
            f.write(f"  Files Created: {self.stats.files_created}\n")
            f.write(f"  Success Rate: {(self.stats.files_created / self.stats.total_items) * 100:.1f}%\n\n")
            
            if self.stats.errors:
                f.write("Errors:\n")
                for error in self.stats.errors:
                    f.write(f"  - {error}\n")
                f.write("\n")
            
            if self.stats.warnings:
                f.write("Warnings:\n")
                for warning in self.stats.warnings:
                    f.write(f"  - {warning}\n")
                f.write("\n")
            
            f.write("Generated Files:\n")
            output_path = Path(self.output_dir)
            for pdf_file in sorted(output_path.glob("output_*.pdf")):
                f.write(f"  - {pdf_file.name}\n")
        
        self.logger.info(f"Summary report generated: {summary_file}")
        
        # Console summary
        print("\n" + "=" * 60)
        print("CONVERSION SUMMARY")
        print("=" * 60)
        print(f"📄 Files Created: {self.stats.files_created}/{self.stats.total_items}")
        print(f"⏱️  Duration: {self.stats.duration}")
        print(f"📁 Output Directory: {self.output_dir}")
        if self.stats.errors:
            print(f"❌ Errors: {len(self.stats.errors)}")
        print("=" * 60)


def main():
    """Main entry point with argument handling."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced JSON to PDF Splitter")
    parser.add_argument("--input", "-i", default="test.json", help="Input JSON file")
    parser.add_argument("--output", "-o", default="output_pdfs", help="Output directory")
    parser.add_argument("--files", "-f", type=int, default=40, help="Number of output files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--sequential", "-s", action="store_true", help="Use sequential processing (for large datasets)")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Timeout per PDF file (seconds)")
    
    args = parser.parse_args()
    
    # Check dependencies
    if not REPORTLAB_AVAILABLE:
        print("❌ ReportLab is required but not installed.")
        print("Install with: pip install reportlab")
        sys.exit(1)
    
    # Additional dependencies check
    try:
        import tqdm
    except ImportError:
        print("❌ tqdm is required but not installed.")
        print("Install with: pip install tqdm")
        sys.exit(1)
    
    # Display startup info
    print("🚀 Advanced JSON to PDF Splitter")
    print("=" * 50)
    print(f"📁 Input: {args.input}")
    print(f"📁 Output: {args.output}")
    print(f"📄 Files: {args.files}")
    print(f"⚡ Mode: {'Sequential' if args.sequential else 'Parallel'}")
    print(f"⏱️  Timeout: {args.timeout}s per file")
    print("=" * 50)
    
    # Create converter and run
    converter = JSONToPDFConverter(
        input_file=args.input,
        output_dir=args.output,
        num_files=args.files
    )
    
    # Set processing mode
    if args.sequential:
        converter.force_sequential = True
    converter.timeout = args.timeout
    
    success = converter.convert()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()