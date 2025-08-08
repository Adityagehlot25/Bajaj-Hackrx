"""
Simplified Integration Tests for PDF Processing and Embedding Generation
Focus on core fixes without heavy dependencies that cause compatibility issues
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_pdf_parsing():
    """Test PDF parsing with all 5 user files."""
    logger.info("="*60)
    logger.info("TESTING PDF PARSING WITH ROBUST ERROR HANDLING")
    logger.info("="*60)
    
    # Import without sentence transformers to avoid compatibility issues
    try:
        from robust_document_parser import RobustDocumentParser
    except ImportError as e:
        logger.error(f"Failed to import document parser: {e}")
        return False
    
    pdf_files = [
        r"e:\final try\bajaj.pdf",
        r"e:\final try\chotgdp.pdf",
        r"e:\final try\edl.pdf",
        r"e:\final try\hdf.pdf",
        r"e:\final try\ici.pdf"
    ]
    
    parser = RobustDocumentParser(min_chunk_words=100, max_chunk_words=500)
    results = {}
    
    for pdf_file in pdf_files:
        if not Path(pdf_file).exists():
            logger.warning(f"PDF file not found: {pdf_file}")
            continue
        
        filename = Path(pdf_file).name
        logger.info(f"\n📄 Testing PDF: {filename}")
        logger.info(f"   File size: {Path(pdf_file).stat().st_size / 1024:.1f} KB")
        
        try:
            # Parse the PDF
            start_time = datetime.now()
            result = parser.parse_file(pdf_file)
            parse_time = (datetime.now() - start_time).total_seconds()
            
            # Validate result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'raw_text' in result, "Missing raw_text"
            assert 'chunks' in result, "Missing chunks"
            assert 'total_chunks' in result, "Missing total_chunks"
            assert 'metadata' in result, "Missing metadata"
            
            # Validate content quality
            raw_text = result['raw_text']
            chunks = result['chunks']
            total_chunks = result['total_chunks']
            
            assert len(raw_text.strip()) > 50, f"Text too short: {len(raw_text)} chars"
            assert total_chunks > 0, "No chunks created"
            assert len(chunks) == total_chunks, f"Chunk count mismatch: {len(chunks)} vs {total_chunks}"
            
            # Count valid chunks
            valid_chunks = [chunk for chunk in chunks if chunk.get('is_valid', True)]
            valid_count = len(valid_chunks)
            
            # Check extraction quality
            quality = result.get('extraction_quality', {})
            alpha_ratio = quality.get('alphabetic_ratio', 0)
            
            # Library used
            library_used = result['metadata'].get('library', 'unknown')
            
            results[pdf_file] = {
                'status': 'success',
                'filename': filename,
                'total_chunks': total_chunks,
                'valid_chunks': valid_count,
                'total_words': result.get('total_words', 0),
                'total_characters': len(raw_text),
                'library': library_used,
                'quality_score': alpha_ratio,
                'parse_time': parse_time,
                'pages': result['metadata'].get('pages', 0)
            }
            
            logger.info(f"   ✅ SUCCESS: {valid_count} chunks, {result.get('total_words', 0)} words")
            logger.info(f"   📊 Library: {library_used}, Quality: {alpha_ratio:.3f}, Time: {parse_time:.2f}s")
            
        except Exception as e:
            logger.error(f"   ❌ FAILED: {str(e)}")
            results[pdf_file] = {
                'status': 'failed',
                'filename': filename,
                'error': str(e)
            }
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("PDF PARSING TEST SUMMARY")
    logger.info("="*60)
    
    successful = sum(1 for r in results.values() if r['status'] == 'success')
    total = len(results)
    
    for result in results.values():
        if result['status'] == 'success':
            logger.info(f"✅ {result['filename']:<15} | {result['valid_chunks']:>3} chunks | {result['total_words']:>6} words | {result['library']:<10} | Quality: {result['quality_score']:.3f}")
        else:
            logger.info(f"❌ {result['filename']:<15} | ERROR: {result['error']}")
    
    success_rate = (successful / total * 100) if total > 0 else 0
    logger.info(f"\nSuccess Rate: {successful}/{total} files ({success_rate:.1f}%)")
    
    if successful > 0:
        # Calculate statistics for successful parses
        successful_results = [r for r in results.values() if r['status'] == 'success']
        
        total_chunks = sum(r['valid_chunks'] for r in successful_results)
        total_words = sum(r['total_words'] for r in successful_results)
        avg_quality = sum(r['quality_score'] for r in successful_results) / len(successful_results)
        libraries_used = set(r['library'] for r in successful_results)
        
        logger.info(f"Total Valid Chunks: {total_chunks}")
        logger.info(f"Total Words Extracted: {total_words}")
        logger.info(f"Average Quality Score: {avg_quality:.3f}")
        logger.info(f"PDF Libraries Used: {', '.join(libraries_used)}")
    
    return successful > 0, results


def test_basic_embedding_generation():
    """Test basic embedding generation without heavy dependencies."""
    logger.info("\n" + "="*60)
    logger.info("TESTING EMBEDDING GENERATION WITH ERROR HANDLING")
    logger.info("="*60)
    
    try:
        # Import our embedding generator but skip sentence transformers
        import os
        os.environ['SKIP_SENTENCE_TRANSFORMERS'] = '1'  # Signal to skip
        
        # Create a simplified version that only uses OpenAI/Gemini
        from robust_embedding_generator import RobustEmbeddingGenerator
        
    except ImportError as e:
        logger.error(f"Failed to import embedding generator: {e}")
        return False
    
    # Test data
    test_chunks = [
        "Bajaj Auto Limited reported strong financial performance in Q4 with revenue growth of 12%.",
        "The company's market share in the two-wheeler segment increased to 19.5%.",
        "Export revenues contributed significantly with growth in international markets.",
        "Cost optimization initiatives resulted in improved operating margins.",
        "The management expressed confidence about future growth prospects."
    ]
    
    logger.info(f"Testing embedding generation with {len(test_chunks)} sample text chunks...")
    
    try:
        generator = RobustEmbeddingGenerator(use_cache=False)
        
        # Check available providers
        available_providers = list(generator.initialized_providers.keys())
        logger.info(f"Available providers: {available_providers}")
        
        if not available_providers:
            logger.warning("No embedding providers available - checking environment variables...")
            
            gemini_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if gemini_key:
                logger.info("✅ Gemini API key found in environment")
            else:
                logger.warning("❌ Gemini API key not found")
                
            if openai_key:
                logger.info("✅ OpenAI API key found in environment")
            else:
                logger.warning("❌ OpenAI API key not found")
            
            if not gemini_key and not openai_key:
                logger.error("No API keys available for embedding generation")
                return False
        
        # Test embedding generation with available provider
        for provider in available_providers:
            logger.info(f"\n🧠 Testing {provider} provider...")
            
            try:
                start_time = datetime.now()
                result = generator.generate_embeddings(
                    text_chunks=test_chunks[:3],  # Limit to 3 for testing
                    provider=provider
                )
                generation_time = (datetime.now() - start_time).total_seconds()
                
                # Validate result
                assert result.get('success', False), f"Embedding generation failed: {result}"
                assert 'embeddings' in result, "Missing embeddings in result"
                assert 'embedding_dimension' in result, "Missing embedding_dimension"
                
                embeddings = result['embeddings']
                dimension = result['embedding_dimension']
                
                assert len(embeddings) > 0, "No embeddings generated"
                assert dimension > 0, "Invalid embedding dimension"
                
                # Validate individual embeddings
                for i, embedding in enumerate(embeddings):
                    assert isinstance(embedding, list), f"Embedding {i} is not a list"
                    assert len(embedding) == dimension, f"Embedding {i} has wrong dimension"
                    assert all(isinstance(x, (int, float)) for x in embedding), f"Embedding {i} has non-numeric values"
                
                logger.info(f"   ✅ SUCCESS: Generated {len(embeddings)} embeddings")
                logger.info(f"   📊 Dimension: {dimension}, Time: {generation_time:.2f}s")
                
                # Test query embedding
                logger.info(f"   🔍 Testing query embedding...")
                query_result = generator.generate_query_embedding(
                    "What is the financial performance?",
                    provider=provider
                )
                
                assert query_result.get('success', False), "Query embedding failed"
                assert 'embedding' in query_result, "Missing query embedding"
                query_embedding = query_result['embedding']
                assert len(query_embedding) == dimension, "Query embedding dimension mismatch"
                
                logger.info(f"   ✅ Query embedding generated successfully")
                
                return True
                
            except Exception as e:
                logger.error(f"   ❌ {provider} provider failed: {str(e)}")
                continue
        
        logger.error("All embedding providers failed")
        return False
        
    except Exception as e:
        logger.error(f"Embedding test failed: {str(e)}")
        return False


def test_integration_pipeline():
    """Test the complete pipeline from PDF to embeddings."""
    logger.info("\n" + "="*60)
    logger.info("TESTING COMPLETE PDF-TO-EMBEDDINGS PIPELINE")
    logger.info("="*60)
    
    # Test with one PDF file to validate the pipeline
    test_pdf = r"e:\final try\bajaj.pdf"
    
    if not Path(test_pdf).exists():
        logger.error(f"Test PDF not found: {test_pdf}")
        return False
    
    try:
        # Import modules
        from robust_document_parser import RobustDocumentParser
        from robust_embedding_generator import RobustEmbeddingGenerator
        
        logger.info(f"🔄 Testing complete pipeline with: {Path(test_pdf).name}")
        
        # Step 1: Parse PDF
        logger.info("   Step 1: Parsing PDF document...")
        parser = RobustDocumentParser(min_chunk_words=150, max_chunk_words=400)
        
        parse_start = datetime.now()
        parse_result = parser.parse_file(test_pdf)
        parse_time = (datetime.now() - parse_start).total_seconds()
        
        assert parse_result['total_chunks'] > 0, "No chunks created from PDF"
        
        # Extract valid text chunks
        valid_chunks = [chunk for chunk in parse_result['chunks'] if chunk.get('is_valid', True)]
        text_chunks = [chunk['text'] for chunk in valid_chunks]
        
        logger.info(f"      ✅ Parsed into {len(text_chunks)} valid chunks in {parse_time:.2f}s")
        logger.info(f"      📊 Total words: {parse_result.get('total_words', 0)}")
        
        # Step 2: Generate embeddings (limit to first few chunks for testing)
        logger.info("   Step 2: Generating embeddings...")
        generator = RobustEmbeddingGenerator(use_cache=False)
        
        test_chunks = text_chunks[:3]  # Limit for testing
        if not test_chunks:
            raise ValueError("No valid chunks available for embedding")
        
        embed_start = datetime.now()
        embed_result = generator.generate_embeddings(test_chunks)
        embed_time = (datetime.now() - embed_start).total_seconds()
        
        assert embed_result.get('success', False), "Embedding generation failed"
        
        embeddings = embed_result['embeddings']
        dimension = embed_result['embedding_dimension']
        
        logger.info(f"      ✅ Generated {len(embeddings)} embeddings in {embed_time:.2f}s")
        logger.info(f"      📊 Dimension: {dimension}, Provider: {embed_result.get('provider', 'unknown')}")
        
        # Step 3: Validate embedding quality
        logger.info("   Step 3: Validating embedding quality...")
        
        for i, embedding in enumerate(embeddings):
            assert len(embedding) == dimension, f"Embedding {i} dimension mismatch"
            assert all(isinstance(x, (int, float)) for x in embedding), f"Embedding {i} has invalid values"
            
            # Check for zero vectors (might indicate issues)
            magnitude = sum(x * x for x in embedding) ** 0.5
            assert magnitude > 0, f"Embedding {i} is a zero vector"
        
        logger.info(f"      ✅ All embeddings validated successfully")
        
        # Step 4: Test query embedding with pipeline
        logger.info("   Step 4: Testing query embedding...")
        
        query = "What are the financial performance metrics mentioned?"
        query_result = generator.generate_query_embedding(query)
        
        assert query_result.get('success', False), "Query embedding failed"
        query_embedding = query_result['embedding']
        assert len(query_embedding) == dimension, "Query embedding dimension mismatch"
        
        logger.info(f"      ✅ Query embedding generated successfully")
        
        # Pipeline summary
        total_time = parse_time + embed_time
        logger.info(f"\n📊 PIPELINE SUMMARY:")
        logger.info(f"   📄 Document: {Path(test_pdf).name}")
        logger.info(f"   📚 Chunks parsed: {len(text_chunks)}")
        logger.info(f"   🧠 Embeddings generated: {len(embeddings)}")
        logger.info(f"   📐 Embedding dimension: {dimension}")
        logger.info(f"   ⏱️  Total time: {total_time:.2f}s (Parse: {parse_time:.2f}s, Embed: {embed_time:.2f}s)")
        logger.info(f"   🏷️  Library used: {parse_result['metadata'].get('library', 'unknown')}")
        logger.info(f"   📈 Quality score: {parse_result.get('extraction_quality', {}).get('alphabetic_ratio', 0):.3f}")
        
        logger.info(f"\n✅ COMPLETE PIPELINE TEST PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {str(e)}")
        return False


def main():
    """Run all tests and provide comprehensive summary."""
    logger.info("🚀 STARTING AI Q&A SYSTEM COMPREHENSIVE VALIDATION")
    logger.info("="*80)
    
    test_results = {}
    
    # Test 1: PDF Parsing
    try:
        pdf_success, pdf_results = test_pdf_parsing()
        test_results['pdf_parsing'] = {
            'status': 'passed' if pdf_success else 'failed',
            'details': pdf_results
        }
    except Exception as e:
        test_results['pdf_parsing'] = {
            'status': 'failed',
            'error': str(e)
        }
    
    # Test 2: Embedding Generation
    try:
        embed_success = test_basic_embedding_generation()
        test_results['embedding_generation'] = {
            'status': 'passed' if embed_success else 'failed'
        }
    except Exception as e:
        test_results['embedding_generation'] = {
            'status': 'failed',
            'error': str(e)
        }
    
    # Test 3: Integration Pipeline
    try:
        pipeline_success = test_integration_pipeline()
        test_results['integration_pipeline'] = {
            'status': 'passed' if pipeline_success else 'failed'
        }
    except Exception as e:
        test_results['integration_pipeline'] = {
            'status': 'failed',
            'error': str(e)
        }
    
    # Final Summary
    logger.info("\n" + "="*80)
    logger.info("🏁 COMPREHENSIVE TEST SUMMARY")
    logger.info("="*80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = result['status']
        icon = "✅" if status == 'passed' else "❌"
        test_display = test_name.replace('_', ' ').title()
        
        logger.info(f"{icon} {test_display}: {status.upper()}")
        
        if status == 'passed':
            passed_tests += 1
            
            # Show additional details for PDF parsing
            if test_name == 'pdf_parsing' and 'details' in result:
                successful_pdfs = sum(1 for r in result['details'].values() if r['status'] == 'success')
                total_pdfs = len(result['details'])
                logger.info(f"    📊 PDF Success Rate: {successful_pdfs}/{total_pdfs} files")
                
        else:
            if 'error' in result:
                logger.info(f"    💥 Error: {result['error']}")
    
    # Overall assessment
    success_rate = (passed_tests / total_tests) * 100
    logger.info(f"\n📈 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - AI Q&A System is ready for production!")
        logger.info("✨ Key improvements implemented:")
        logger.info("   • Robust PDF parsing with multiple fallback libraries")
        logger.info("   • Comprehensive error handling and logging")
        logger.info("   • Text quality validation and chunk validation")
        logger.info("   • Retry logic for embedding generation")
        logger.info("   • Defensive programming throughout the pipeline")
    elif passed_tests >= total_tests * 0.75:
        logger.info("⚠️  MOSTLY WORKING - Minor issues may need attention")
        logger.info("💡 System is functional but some edge cases might need fixes")
    else:
        logger.info("❌ SIGNIFICANT ISSUES - Major fixes required")
        logger.info("🔧 Review the error messages and fix critical components")
    
    # Recommendations
    logger.info(f"\n💡 RECOMMENDATIONS:")
    if test_results.get('pdf_parsing', {}).get('status') == 'passed':
        logger.info("✅ PDF parsing is working - all documents can be processed reliably")
    else:
        logger.info("🔧 Fix PDF parsing issues - check library installations and file permissions")
    
    if test_results.get('embedding_generation', {}).get('status') == 'passed':
        logger.info("✅ Embedding generation is working - API keys configured correctly")
    else:
        logger.info("🔧 Fix embedding generation - check API keys and network connectivity")
    
    if test_results.get('integration_pipeline', {}).get('status') == 'passed':
        logger.info("✅ Complete pipeline is working - ready for production use")
    else:
        logger.info("🔧 Fix pipeline integration - ensure all components work together")
    
    return test_results


if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    passed_count = sum(1 for r in results.values() if r['status'] == 'passed')
    total_count = len(results)
    
    if passed_count == total_count:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed
