import pandas as pd
from PyPDF2 import PdfReader
from pathlib import Path
from typing import Union
import uuid
from datetime import datetime

from ..models.schemas import Product


class DocumentProcessor:
    """Processes Excel and PDF files to extract product data."""

    SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv", ".pdf", ".txt"}

    def __init__(self):
        pass

    def process_file(self, file_path: Path) -> list[dict]:
        """Process a file and return list of product dictionaries."""
        extension = file_path.suffix.lower()

        if extension in {".xlsx", ".xls"}:
            return self._process_excel(file_path)
        elif extension == ".csv":
            return self._process_csv(file_path)
        elif extension == ".pdf":
            return self._process_pdf(file_path)
        elif extension == ".txt":
            return self._process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def _process_excel(self, file_path: Path) -> list[dict]:
        """Process Excel file with normalized format."""
        df = pd.read_excel(file_path)
        return self._dataframe_to_products(df)

    def _process_csv(self, file_path: Path) -> list[dict]:
        """Process CSV file."""
        df = pd.read_csv(file_path)
        return self._dataframe_to_products(df)

    def _clean_value(self, value) -> str:
        """Clean value - handle NaN and empty strings."""
        if pd.isna(value):
            return ""
        val_str = str(value).strip()
        if val_str.lower() == "nan":
            return ""
        return val_str

    def _dataframe_to_products(self, df: pd.DataFrame) -> list[dict]:
        """Convert DataFrame to list of product dictionaries."""
        products = []

        # Expected columns (case-insensitive matching)
        column_mapping = {
            "category": ["category", "main_category", "cat"],
            "sub_category": ["sub_category", "subcategory", "sub_cat"],
            "sub_sub_category": ["sub_sub_category", "subsubcategory", "sub_sub_cat"],
            "product_name": ["product_name", "productname", "name", "product", "item"],
            "variant": ["variant", "size", "option"],
            "size_weight": ["size_weight", "weight", "quantity"],
            "price_lkr": ["price_lkr", "price", "cost", "amount"],
            "description": ["description", "desc", "details"],
            "available": ["available", "in_stock", "stock"],
            "tags": ["tags", "keywords", "labels"],
        }

        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()

        # Map columns
        mapped_columns = {}
        for target, options in column_mapping.items():
            for option in options:
                if option in df.columns:
                    mapped_columns[target] = option
                    break

        # Process each row
        for _, row in df.iterrows():
            product = {
                "category": self._clean_value(row.get(mapped_columns.get("category", ""), "")),
                "sub_category": self._clean_value(row.get(mapped_columns.get("sub_category", ""), "")),
                "sub_sub_category": self._clean_value(row.get(mapped_columns.get("sub_sub_category", ""), "")),
                "product_name": self._clean_value(row.get(mapped_columns.get("product_name", ""), "")),
                "variant": self._clean_value(row.get(mapped_columns.get("variant", ""), "")),
                "size_weight": self._clean_value(row.get(mapped_columns.get("size_weight", ""), "")),
                "price_lkr": self._parse_price(row.get(mapped_columns.get("price_lkr", ""), 0)),
                "description": self._clean_value(row.get(mapped_columns.get("description", ""), "")),
                "available": self._clean_value(row.get(mapped_columns.get("available", ""), "Yes")) or "Yes",
                "tags": self._clean_value(row.get(mapped_columns.get("tags", ""), "")),
            }

            # Skip rows without product name
            if product["product_name"]:
                products.append(product)

        return products

    def _parse_price(self, price_value) -> float:
        """Parse price from various formats (RS.3000, 3000, etc.)."""
        if pd.isna(price_value):
            return 0.0

        price_str = str(price_value)
        # Remove currency symbols and text
        import re

        price_clean = re.sub(r"[^\d.]", "", price_str)
        try:
            return float(price_clean) if price_clean else 0.0
        except ValueError:
            return 0.0

    def _process_pdf(self, file_path: Path) -> list[dict]:
        """Process PDF file - extract text and create chunks."""
        reader = PdfReader(str(file_path))
        full_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        # For PDFs, we create text chunks as "products"
        chunks = self._chunk_text(full_text)

        products = []
        for i, chunk in enumerate(chunks):
            products.append(
                {
                    "category": "Document",
                    "sub_category": file_path.stem,
                    "sub_sub_category": "",
                    "product_name": f"Chunk {i + 1}",
                    "variant": "",
                    "size_weight": "",
                    "price_lkr": 0,
                    "description": chunk,
                    "available": "Yes",
                    "tags": "pdf,document",
                }
            )

        return products

    def _process_txt(self, file_path: Path) -> list[dict]:
        """Process text file."""
        with open(file_path, "r", encoding="utf-8") as f:
            full_text = f.read()

        # Attempt to parse Q&A format first
        products = self._parse_qa_from_text(full_text, file_path.stem)
        
        if products:
             return products

        # Fallback to chunking
        chunks = self._chunk_text(full_text)

        products = []
        for i, chunk in enumerate(chunks):
            products.append(
                {
                    "category": "Document",
                    "sub_category": file_path.stem,
                    "sub_sub_category": "",
                    "product_name": f"Chunk {i + 1}",
                    "variant": "",
                    "size_weight": "",
                    "price_lkr": 0,
                    "description": chunk,
                    "available": "Yes",
                    "tags": "text,document",
                }
            )

        return products

    def _parse_qa_from_text(self, text: str, source_name: str) -> list[dict]:
        """Parse Q&A format typical in FAQ files."""
        import re
        
        # Regex to find "Q1:", "Q:", followed by text, then "A:" followed by text
        # Groups: 1=Question Label (e.g. Q1), 2=Question Text, 3=Answer Text
        # We use dotall to capture multi-line text, but need to be careful not to eat the next Q
        qa_pattern = re.compile(r'(Q\d*|Q):?\s+(.*?)\s*\n?A:\s+(.*?)(?=\nQ\d*:|\nQ:|$)', re.DOTALL | re.IGNORECASE)
        
        matches = qa_pattern.findall(text)
        
        products = []
        for _, question, answer in matches:
            products.append({
                "category": "FAQ",
                "sub_category": source_name, # e.g. "data" or "Fly Killer"
                "sub_sub_category": "",
                "product_name": question.strip(),
                "variant": "",
                "size_weight": "",
                "price_lkr": 0,
                "description": answer.strip(),
                "available": "Yes",
                "tags": "faq, info",
            })
            
        return products

    def _chunk_text(
        self, text: str, chunk_size: int = 500, overlap: int = 50
    ) -> list[str]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return []

        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start = end - overlap

        return chunks

    def create_embedding_text(self, product: dict) -> str:
        """Create text representation for embedding."""
        parts = []

        if product.get("category"):
            parts.append(f"Category: {product['category']}")
        if product.get("sub_category"):
            parts.append(f"Sub-category: {product['sub_category']}")
        if product.get("sub_sub_category"):
            parts.append(f"Type: {product['sub_sub_category']}")
        if product.get("product_name"):
            parts.append(f"Product: {product['product_name']}")
        if product.get("variant"):
            parts.append(f"Variant: {product['variant']}")
        if product.get("size_weight"):
            parts.append(f"Size/Weight: {product['size_weight']}")
        # Exclude dynamic data (price, available) from embeddings to prevent hallucinations
        # if product.get("price_lkr"):
        #     parts.append(f"Price: RS.{product['price_lkr']}")
        if product.get("description"):
            parts.append(f"Description: {product['description']}")
        if product.get("tags"):
            parts.append(f"Tags: {product['tags']}")

        return " | ".join(parts)
