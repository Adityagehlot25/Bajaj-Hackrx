#!/usr/bin/env python3
"""Final verification test for the improved chunking system."""

from robust_document_parser import parse_document
import os

def test_original_issue():
    """Test that the original massive chunk issue is resolved."""
    
    print("FINAL TEST: Verifying Original Issue Resolution")
    print("=" * 60)
    
    # Test with bajaj.pdf - the file that was creating 47,810 token chunks
    pdf_path = 'bajaj.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ Test file {pdf_path} not found")
        return False
    
    print(f"📄 Testing {pdf_path} (the problematic file)...")
    print(f"   File size: {os.path.getsize(pdf_path)/1024:.1f} KB")
    
    # Parse with improved system
    result = parse_document(pdf_path, min_chunk_tokens=100, max_chunk_tokens=2000, target_chunk_tokens=1000)
    
    # Check results
    chunks = result.get('chunks', [])
    token_stats = result.get('token_statistics', {})
    
    print(f"\n📊 RESULTS:")
    print(f"   ✅ Total chunks created: {len(chunks)}")
    print(f"   ✅ Total tokens: {token_stats.get('total_tokens', 0):,}")
    print(f"   ✅ Average tokens per chunk: {token_stats.get('avg_tokens_per_chunk', 0):.1f}")
    print(f"   ✅ Largest chunk: {token_stats.get('max_tokens_per_chunk', 0)} tokens")
    print(f"   ✅ Chunks over 2000 tokens: {sum(1 for c in chunks if c.get('token_count', 0) > 2000)}")
    
    # Verify the fix
    max_tokens = token_stats.get('max_tokens_per_chunk', 0)
    over_limit = sum(1 for c in chunks if c.get('token_count', 0) > 2000)
    
    print(f"\n🎯 ISSUE RESOLUTION CHECK:")
    
    if over_limit == 0 and max_tokens <= 2000:
        print(f"   ✅ SUCCESS: No chunks exceed 2000 tokens!")
        print(f"   ✅ BEFORE: Single chunk with ~47,810 tokens")
        print(f"   ✅ AFTER: {len(chunks)} chunks, max {max_tokens} tokens")
        print(f"   ✅ The chunking issue has been COMPLETELY RESOLVED! 🎉")
        return True
    else:
        print(f"   ❌ ISSUE REMAINS: {over_limit} chunks still exceed 2000 tokens")
        return False

def test_embedding_compatibility():
    """Test that chunks are now compatible with embedding models."""
    
    print(f"\n🔧 EMBEDDING MODEL COMPATIBILITY:")
    
    # Common embedding model limits
    model_limits = {
        'text-embedding-ada-002': 8192,  # OpenAI
        'text-embedding-3-small': 8192,  # OpenAI  
        'gemini-pro': 2048,              # Google (conservative)
        'sentence-transformers': 512,     # Typical limit
    }
    
    result = parse_document('bajaj.pdf', max_chunk_tokens=2000)
    chunks = result.get('chunks', [])
    token_stats = result.get('token_statistics', {})
    max_tokens = token_stats.get('max_tokens_per_chunk', 0)
    
    for model, limit in model_limits.items():
        compatible = max_tokens <= limit
        status = "✅ COMPATIBLE" if compatible else "❌ TOO LARGE"
        print(f"   {model}: {status} (max chunk: {max_tokens}/{limit} tokens)")

if __name__ == "__main__":
    success = test_original_issue()
    if success:
        test_embedding_compatibility()
    
    print(f"\n{'='*60}")
    print("🚀 SYSTEM READY FOR DEPLOYMENT!" if success else "⚠️  ADDITIONAL WORK NEEDED")
    print(f"{'='*60}")
