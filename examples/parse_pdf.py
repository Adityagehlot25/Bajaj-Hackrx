#!/usr/bin/env python3
"""
Example script to parse a PDF document using the robust document parser.
"""

import sys
import os
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from robust_document_parser import parse_document

def parse_pdf_example():
    """Parse a PDF file and print the result."""
    # Get the PDF file path from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python parse_pdf.py <pdf_file_path>")
        return
    
    pdf_file = sys.argv[1]
    
    print(f"Parsing PDF file: {pdf_file}")
    
    try:
        # Parse the PDF file
        result = parse_document(pdf_file)
        
        # Print the results
        print("\nDocument parsing completed successfully!")
        print(f"Total chunks: {result['total_chunks']}")
        print(f"Total words: {result['total_words']}")
        print(f"Total characters: {result['total_characters']}")
        
        # Print the first 3 chunks
        print("\nFirst 3 chunks:")
        for i, chunk in enumerate(result['chunks'][:3]):
            print(f"\nChunk {i+1}:")
            print(f"  Words: {chunk['word_count']}")
            print(f"  First 100 characters: {chunk['text'][:100]}...")
            
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        
if __name__ == "__main__":
    parse_pdf_example()
