#!/usr/bin/env python3
"""
Example script to run the full Q&A pipeline: Parse a document, generate embeddings, and answer questions.
"""

import sys
import os
import asyncio

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from robust_document_parser import parse_document
from gemini_vector_embedder import generate_embeddings
from gemini_answer import generate_answer
from dotenv import load_dotenv

async def qa_pipeline_example():
    """Run the full Q&A pipeline."""
    # Load environment variables
    load_dotenv()
    
    # Get the PDF file path and question from command line arguments
    if len(sys.argv) < 3:
        print("Usage: python qa_pipeline.py <pdf_file_path> <question>")
        return
    
    pdf_file = sys.argv[1]
    question = sys.argv[2]
    
    print(f"Processing PDF file: {pdf_file}")
    print(f"Question: {question}")
    
    try:
        # Step 1: Parse the PDF document
        print("\n--- Step 1: Parsing document ---")
        parse_result = parse_document(pdf_file)
        print(f"Document parsed into {parse_result['total_chunks']} chunks")
        
        # Extract text chunks
        text_chunks = [chunk['text'] for chunk in parse_result['chunks'] if chunk['is_valid']]
        print(f"Valid chunks: {len(text_chunks)}")
        
        # Step 2: Generate embeddings for the chunks
        print("\n--- Step 2: Generating embeddings ---")
        embed_result = await generate_embeddings(text_chunks)
        
        if not embed_result.get('success'):
            print(f"Error generating embeddings: {embed_result.get('error')}")
            return
        
        print(f"Generated {len(embed_result['embeddings'])} embeddings with {embed_result['dimensions']} dimensions each")
        
        # Step 3: Generate answer for the question
        print("\n--- Step 3: Generating answer ---")
        answer_result = await generate_answer(
            question=question,
            context_chunks=text_chunks,
            embeddings=embed_result['embeddings']
        )
        
        if answer_result.get('success'):
            print("\n=== Answer ===")
            print(answer_result['answer'])
            print("\n=== Sources ===")
            for i, source in enumerate(answer_result.get('sources', [])[:3]):
                print(f"Source {i+1}: {source[:100]}...")
        else:
            print(f"Error generating answer: {answer_result.get('error')}")
            
    except Exception as e:
        print(f"Error in QA pipeline: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await qa_pipeline_example()
        
if __name__ == "__main__":
    asyncio.run(main())
