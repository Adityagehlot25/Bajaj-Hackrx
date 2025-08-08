"""
Simple example demonstrating the document parsing functionality.
"""

# Example of how to use the document parser
from document_parser import DocumentParser

def example_usage():
    """Show basic usage of the document parser."""
    
    # Create a parser instance
    parser = DocumentParser(min_chunk_words=500, max_chunk_words=1000)
    
    # Example text to demonstrate chunking
    sample_text = """
    This is a comprehensive example of how the document parser works with different types of content.
    The parser is designed to handle PDF, DOCX, and EML files efficiently.
    
    When processing a PDF file, the parser extracts text from each page and combines it into a single text stream.
    It then applies intelligent chunking algorithms to split the content into manageable pieces.
    
    For DOCX files, the parser reads through all paragraphs and table content, preserving the document structure
    while extracting plain text. This ensures that all textual content is captured regardless of formatting.
    
    Email files (EML format) are handled specially, as they contain both header information (sender, recipient,
    subject, date) and body content. The parser extracts both components and includes metadata about the email.
    
    The chunking algorithm is particularly sophisticated. It aims to create chunks between 500-1000 words
    (these limits are configurable) while trying to break at natural sentence boundaries. This approach
    maintains readability and context within each chunk.
    
    Each chunk contains metadata including its position in the document, word count, and source file information.
    This metadata is valuable for applications that need to track the origin of text segments or implement
    search functionality with precise source attribution.
    
    Error handling is robust throughout the system. If a file cannot be parsed due to corruption, unsupported
    format, or missing dependencies, the system provides clear error messages and continues processing other files
    when dealing with batch operations.
    
    The system is designed to be extensible, allowing for easy addition of new file format parsers while
    maintaining a consistent interface and chunking behavior across all supported formats.
    """
    
    # Demonstrate text chunking
    chunks = parser._split_into_chunks(sample_text, "example.txt")
    
    print("=== Document Parser Example ===\n")
    print(f"Original text length: {len(sample_text)} characters")
    print(f"Total words: {len(sample_text.split())}")
    print(f"Number of chunks created: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Word count: {chunk.word_count}")
        print(f"Text preview: {chunk.text[:150]}...")
    
    return chunks

if __name__ == "__main__":
    try:
        chunks = example_usage()
        print(f"\n✅ Successfully created {len(chunks)} text chunks")
        print("\nTo test with actual files, use:")
        print("1. python test_parser.py - for comprehensive testing")
        print("2. Start FastAPI server: uvicorn main:app --reload")
        print("3. Visit http://localhost:8000/docs for API documentation")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
