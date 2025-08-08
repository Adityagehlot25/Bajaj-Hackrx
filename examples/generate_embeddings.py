#!/usr/bin/env python3
"""
Example script to generate embeddings for a list of text chunks.
"""

import sys
import os
import asyncio

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from gemini_vector_embedder import generate_embeddings
from dotenv import load_dotenv

async def generate_embeddings_example():
    """Generate embeddings for a list of text chunks."""
    # Load environment variables
    load_dotenv()
    
    # Sample text chunks
    text_chunks = [
        "Bajaj Auto Limited is one of the leading motorcycle manufacturers in India.",
        "The company produces a wide range of motorcycles, three-wheelers, and quadricycles.",
        "Bajaj Auto has a strong presence in both domestic and international markets."
    ]
    
    print("Generating embeddings for sample text chunks...")
    
    try:
        # Generate embeddings
        result = await generate_embeddings(text_chunks)
        
        # Print results
        if result.get('success'):
            print("\nEmbedding generation successful!")
            print(f"Number of embeddings: {len(result['embeddings'])}")
            print(f"Dimensions per embedding: {result['dimensions']}")
            print(f"Total tokens processed: {result['total_tokens']}")
            
            # Print a sample of the first embedding
            first_emb = result['embeddings'][0]
            print(f"\nSample of first embedding (first 5 values):")
            print(first_emb[:5])
        else:
            print(f"Error generating embeddings: {result.get('error')}")
            
    except Exception as e:
        print(f"Exception during embedding generation: {e}")
        
async def main():
    await generate_embeddings_example()
        
if __name__ == "__main__":
    asyncio.run(main())
