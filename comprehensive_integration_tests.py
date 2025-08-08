"""
Comprehensive Integration Tests for AI Q&A System
Tests document parsing, embedding generation, and vector search pipeline
"""

import os
import sys
import pytest
import logging
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules
from robust_document_parser import RobustDocumentParser, parse_document
from robust_embedding_generator import RobustEmbeddingGenerator, generate_embeddings

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestDocumentParser:
    """Test the robust document parser."""
    
    @pytest.fixture
    def parser(self):
        """Create a document parser instance."""
        return RobustDocumentParser(min_chunk_words=50, max_chunk_words=200)
    
    def test_pdf_parsing_all_files(self, parser):
        """Test PDF parsing with all 5 user files."""
        pdf_files = [
            r"e:\final try\bajaj.pdf",
            r"e:\final try\chotgdp.pdf",
            r"e:\final try\edl.pdf",
            r"e:\final try\hdf.pdf",
            r"e:\final try\ici.pdf"
        ]
        
        results = {}
        
        for pdf_file in pdf_files:
            if not Path(pdf_file).exists():
                logger.warning(f"PDF file not found: {pdf_file}")
                continue
            
            logger.info(f"Testing PDF parsing for: {pdf_file}")
            
            try:
                result = parser.parse_file(pdf_file)
                
                # Validate result structure
                assert isinstance(result, dict)
                assert 'success' not in result or result['success']  # If success field exists, it should be True
                assert 'raw_text' in result
                assert 'chunks' in result
                assert 'total_chunks' in result
                assert 'metadata' in result
                
                # Validate content quality
                assert len(result['raw_text'].strip()) > 100, f"Text too short: {len(result['raw_text'])}"
                assert result['total_chunks'] > 0, "No chunks created"
                assert len(result['chunks']) == result['total_chunks'], "Chunk count mismatch"
                
                # Validate chunks
                valid_chunks = [chunk for chunk in result['chunks'] if chunk.get('is_valid', True)]
                assert len(valid_chunks) > 0, "No valid chunks"
                
                # Check extraction quality
                quality = result.get('extraction_quality', {})
                if quality:
                    assert quality.get('alphabetic_ratio', 0) > 0.5, f"Poor text quality: {quality.get('alphabetic_ratio')}"
                
                results[pdf_file] = {
                    'status': 'success',
                    'chunks': len(valid_chunks),
                    'words': result.get('total_words', 0),
                    'characters': result.get('total_characters', 0),
                    'library': result['metadata'].get('library', 'unknown'),
                    'quality': quality.get('alphabetic_ratio', 0)
                }
                
                logger.info(f"✅ Successfully parsed {Path(pdf_file).name}: {len(valid_chunks)} chunks, {result.get('total_words', 0)} words")
                
            except Exception as e:
                logger.error(f"❌ Failed to parse {pdf_file}: {e}")
                results[pdf_file] = {
                    'status': 'failed',
                    'error': str(e)
                }
                # Don't fail the test immediately, collect all results
                continue
        
        # Print summary
        logger.info("PDF Parsing Test Summary:")
        successful = sum(1 for r in results.values() if r['status'] == 'success')
        total = len(results)
        
        for pdf_file, result in results.items():
            filename = Path(pdf_file).name
            if result['status'] == 'success':
                logger.info(f"  ✅ {filename}: {result['chunks']} chunks, {result['words']} words, quality={result['quality']:.2f}")
            else:
                logger.error(f"  ❌ {filename}: {result['error']}")
        
        logger.info(f"Success rate: {successful}/{total} files")
        
        # At least one file should parse successfully
        assert successful > 0, f"All PDF parsing failed. Results: {results}"
        
        return results
    
    def test_chunk_validation(self, parser):
        """Test chunk validation and quality checks."""
        # Create a simple test PDF or text file
        test_content = """
        This is a test document with multiple paragraphs.
        
        The first paragraph contains some business information about financial performance.
        We need to ensure that this content is properly chunked and validated.
        
        The second paragraph discusses market trends and analysis.
        This should create meaningful chunks that can be embedded and searched.
        
        The third paragraph covers operational efficiency and strategic planning.
        All chunks should pass validation checks for quality and length.
        """
        
        chunks = parser._split_into_chunks(test_content, "test_file.txt")
        
        assert len(chunks) > 0, "No chunks created"
        
        for chunk in chunks:
            # Test chunk validation
            assert chunk.is_valid, f"Invalid chunk: {chunk.text[:100]}"
            assert chunk.word_count >= 5, f"Chunk too short: {chunk.word_count} words"
            assert len(chunk.text.strip()) >= 10, "Chunk text too short"
            
            # Test chunk structure
            assert hasattr(chunk, 'chunk_id')
            assert hasattr(chunk, 'source_file')
            assert hasattr(chunk, 'word_count')
            assert hasattr(chunk, 'char_count')


class TestEmbeddingGenerator:
    """Test the robust embedding generator."""
    
    @pytest.fixture
    def generator(self):
        """Create an embedding generator instance."""
        return RobustEmbeddingGenerator(use_cache=False)  # Disable cache for tests
    
    def test_embedding_providers_initialization(self, generator):
        """Test that at least one embedding provider is available."""
        assert len(generator.initialized_providers) > 0, "No embedding providers initialized"
        logger.info(f"Available providers: {list(generator.initialized_providers.keys())}")
    
    def test_embedding_generation_basic(self, generator):
        """Test basic embedding generation."""
        test_chunks = [
            "This is a test document about financial performance.",
            "The company shows strong revenue growth in Q4.",
            "Market analysis indicates positive trends."
        ]
        
        try:
            result = generator.generate_embeddings(test_chunks)
            
            # Validate result structure
            assert isinstance(result, dict)
            assert result.get('success', False), f"Embedding generation failed: {result}"
            assert 'embeddings' in result
            assert 'embedding_dimension' in result
            assert 'total_embeddings' in result
            
            # Validate embeddings
            embeddings = result['embeddings']
            assert len(embeddings) == len(test_chunks), "Embedding count mismatch"
            assert result['total_embeddings'] == len(test_chunks)
            assert result['embedding_dimension'] > 0
            
            # Validate individual embeddings
            for i, embedding in enumerate(embeddings):
                assert isinstance(embedding, list), f"Embedding {i} is not a list"
                assert len(embedding) == result['embedding_dimension'], f"Embedding {i} dimension mismatch"
                assert all(isinstance(x, (int, float)) for x in embedding), f"Embedding {i} contains non-numeric values"
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings with dimension {result['embedding_dimension']}")
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise
    
    def test_query_embedding_generation(self, generator):
        """Test query embedding generation."""
        query = "What are the financial performance metrics?"
        
        try:
            result = generator.generate_query_embedding(query)
            
            # Validate result
            assert result.get('success', False), "Query embedding generation failed"
            assert 'embedding' in result
            assert 'embedding_dimension' in result
            
            embedding = result['embedding']
            assert isinstance(embedding, list), "Query embedding is not a list"
            assert len(embedding) == result['embedding_dimension'], "Query embedding dimension mismatch"
            assert all(isinstance(x, (int, float)) for x in embedding), "Query embedding contains non-numeric values"
            
            logger.info(f"✅ Generated query embedding with dimension {result['embedding_dimension']}")
            
        except Exception as e:
            logger.error(f"❌ Query embedding generation failed: {e}")
            raise
    
    def test_embedding_with_empty_input(self, generator):
        """Test error handling with empty input."""
        with pytest.raises(ValueError, match="text_chunks cannot be empty"):
            generator.generate_embeddings([])
        
        with pytest.raises(ValueError, match="text_chunks must be a list"):
            generator.generate_embeddings("not a list")
        
        with pytest.raises(ValueError, match="Query text cannot be empty"):
            generator.generate_query_embedding("")
    
    def test_embedding_text_cleaning(self, generator):
        """Test text cleaning and validation."""
        # Test with problematic text
        problematic_chunks = [
            "   ",  # Only whitespace
            "abc",  # Too short
            "This is a valid chunk with sufficient content for embedding generation.",
            "\x00\x01Invalid characters\x02",  # Control characters
            "A" * 10000,  # Very long text
        ]
        
        try:
            result = generator.generate_embeddings(problematic_chunks)
            
            # Should only process valid chunks
            embeddings = result['embeddings']
            assert len(embeddings) <= len(problematic_chunks), "More embeddings than valid chunks"
            assert len(embeddings) > 0, "No embeddings generated from valid chunks"
            
            logger.info(f"✅ Processed {len(embeddings)} valid chunks from {len(problematic_chunks)} input chunks")
            
        except Exception as e:
            logger.error(f"❌ Text cleaning test failed: {e}")
            raise


class TestIntegrationPipeline:
    """Test the complete document processing pipeline."""
    
    def test_pdf_to_embeddings_pipeline(self):
        """Test the complete pipeline from PDF to embeddings."""
        pdf_files = [
            r"e:\final try\bajaj.pdf",
            r"e:\final try\hdf.pdf"  # Test with 2 files for speed
        ]
        
        parser = RobustDocumentParser(min_chunk_words=100, max_chunk_words=300)
        generator = RobustEmbeddingGenerator(use_cache=False)
        
        pipeline_results = {}
        
        for pdf_file in pdf_files:
            if not Path(pdf_file).exists():
                logger.warning(f"PDF file not found: {pdf_file}")
                continue
            
            logger.info(f"Testing complete pipeline for: {Path(pdf_file).name}")
            
            try:
                # Step 1: Parse document
                logger.info("  Step 1: Parsing document...")
                parse_result = parser.parse_file(pdf_file)
                
                assert parse_result['total_chunks'] > 0, "No chunks created"
                
                # Extract text chunks
                text_chunks = [chunk['text'] for chunk in parse_result['chunks'] if chunk.get('is_valid', True)]
                assert len(text_chunks) > 0, "No valid text chunks"
                
                logger.info(f"    ✅ Parsed into {len(text_chunks)} valid chunks")
                
                # Step 2: Generate embeddings
                logger.info("  Step 2: Generating embeddings...")
                embed_result = generator.generate_embeddings(text_chunks[:5])  # Limit to 5 chunks for testing
                
                assert embed_result.get('success', False), "Embedding generation failed"
                assert len(embed_result['embeddings']) > 0, "No embeddings generated"
                
                logger.info(f"    ✅ Generated {len(embed_result['embeddings'])} embeddings")
                
                # Step 3: Validate embedding quality
                logger.info("  Step 3: Validating embeddings...")
                embeddings = embed_result['embeddings']
                embedding_dim = embed_result['embedding_dimension']
                
                for i, embedding in enumerate(embeddings):
                    assert len(embedding) == embedding_dim, f"Embedding {i} dimension mismatch"
                    assert all(isinstance(x, (int, float)) for x in embedding), f"Embedding {i} contains non-numeric values"
                    
                    # Check for zero vectors (might indicate issues)
                    if all(x == 0 for x in embedding):
                        logger.warning(f"Embedding {i} is a zero vector")
                
                logger.info(f"    ✅ All embeddings validated (dimension: {embedding_dim})")
                
                pipeline_results[pdf_file] = {
                    'status': 'success',
                    'parse_chunks': len(text_chunks),
                    'embeddings_generated': len(embeddings),
                    'embedding_dimension': embedding_dim,
                    'parse_time': parse_result.get('parse_duration_seconds', 0),
                    'embed_time': embed_result.get('processing_time_seconds', 0)
                }
                
                logger.info(f"  ✅ Pipeline complete for {Path(pdf_file).name}")
                
            except Exception as e:
                logger.error(f"  ❌ Pipeline failed for {pdf_file}: {e}")
                pipeline_results[pdf_file] = {
                    'status': 'failed',
                    'error': str(e)
                }
                continue
        
        # Summary
        logger.info("Integration Pipeline Test Summary:")
        successful = sum(1 for r in pipeline_results.values() if r['status'] == 'success')
        total = len(pipeline_results)
        
        for pdf_file, result in pipeline_results.items():
            filename = Path(pdf_file).name
            if result['status'] == 'success':
                logger.info(f"  ✅ {filename}: {result['parse_chunks']} chunks → {result['embeddings_generated']} embeddings")
            else:
                logger.error(f"  ❌ {filename}: {result['error']}")
        
        assert successful > 0, f"All pipeline tests failed. Results: {pipeline_results}"
        
        return pipeline_results
    
    def test_query_embedding_similarity(self):
        """Test that similar queries produce similar embeddings."""
        generator = RobustEmbeddingGenerator(use_cache=False)
        
        # Test with similar queries
        queries = [
            "What is the financial performance?",
            "How is the company performing financially?",
            "What are the revenue numbers?",
            "What are the company's sales figures?",
            "What is the weather today?"  # Dissimilar query
        ]
        
        try:
            embeddings = []
            for query in queries:
                result = generator.generate_query_embedding(query)
                embeddings.append(result['embedding'])
            
            # Calculate basic similarity (dot product)
            def cosine_similarity(a, b):
                dot_product = sum(x * y for x, y in zip(a, b))
                norm_a = sum(x * x for x in a) ** 0.5
                norm_b = sum(x * x for x in b) ** 0.5
                return dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
            
            # Similar financial queries should be more similar to each other
            fin_sim = cosine_similarity(embeddings[0], embeddings[1])  # Financial queries
            revenue_sim = cosine_similarity(embeddings[2], embeddings[3])  # Revenue queries
            dissimilar_sim = cosine_similarity(embeddings[0], embeddings[4])  # Financial vs Weather
            
            logger.info(f"Financial query similarity: {fin_sim:.3f}")
            logger.info(f"Revenue query similarity: {revenue_sim:.3f}")
            logger.info(f"Dissimilar query similarity: {dissimilar_sim:.3f}")
            
            # Similar queries should have higher similarity
            assert fin_sim > dissimilar_sim, "Similar financial queries should be more similar than dissimilar ones"
            assert revenue_sim > dissimilar_sim, "Similar revenue queries should be more similar than dissimilar ones"
            
            logger.info("✅ Query similarity test passed")
            
        except Exception as e:
            logger.error(f"❌ Query similarity test failed: {e}")
            raise


def run_comprehensive_tests():
    """Run all tests and provide a summary."""
    logger.info("="*80)
    logger.info("STARTING COMPREHENSIVE AI Q&A SYSTEM TESTS")
    logger.info("="*80)
    
    test_results = {
        'pdf_parsing': None,
        'embedding_generation': None,
        'integration_pipeline': None,
        'query_similarity': None
    }
    
    # Test 1: PDF Parsing
    logger.info("\n" + "="*50)
    logger.info("TEST 1: PDF PARSING")
    logger.info("="*50)
    try:
        parser_test = TestDocumentParser()
        parser = RobustDocumentParser()
        pdf_results = parser_test.test_pdf_parsing_all_files(parser)
        test_results['pdf_parsing'] = {'status': 'passed', 'results': pdf_results}
        logger.info("✅ PDF Parsing tests PASSED")
    except Exception as e:
        test_results['pdf_parsing'] = {'status': 'failed', 'error': str(e)}
        logger.error(f"❌ PDF Parsing tests FAILED: {e}")
    
    # Test 2: Embedding Generation
    logger.info("\n" + "="*50)
    logger.info("TEST 2: EMBEDDING GENERATION")
    logger.info("="*50)
    try:
        embed_test = TestEmbeddingGenerator()
        generator = RobustEmbeddingGenerator()
        embed_test.test_embedding_providers_initialization(generator)
        embed_test.test_embedding_generation_basic(generator)
        embed_test.test_query_embedding_generation(generator)
        test_results['embedding_generation'] = {'status': 'passed'}
        logger.info("✅ Embedding Generation tests PASSED")
    except Exception as e:
        test_results['embedding_generation'] = {'status': 'failed', 'error': str(e)}
        logger.error(f"❌ Embedding Generation tests FAILED: {e}")
    
    # Test 3: Integration Pipeline
    logger.info("\n" + "="*50)
    logger.info("TEST 3: INTEGRATION PIPELINE")
    logger.info("="*50)
    try:
        pipeline_test = TestIntegrationPipeline()
        pipeline_results = pipeline_test.test_pdf_to_embeddings_pipeline()
        test_results['integration_pipeline'] = {'status': 'passed', 'results': pipeline_results}
        logger.info("✅ Integration Pipeline tests PASSED")
    except Exception as e:
        test_results['integration_pipeline'] = {'status': 'failed', 'error': str(e)}
        logger.error(f"❌ Integration Pipeline tests FAILED: {e}")
    
    # Test 4: Query Similarity
    logger.info("\n" + "="*50)
    logger.info("TEST 4: QUERY SIMILARITY")
    logger.info("="*50)
    try:
        pipeline_test = TestIntegrationPipeline()
        pipeline_test.test_query_embedding_similarity()
        test_results['query_similarity'] = {'status': 'passed'}
        logger.info("✅ Query Similarity tests PASSED")
    except Exception as e:
        test_results['query_similarity'] = {'status': 'failed', 'error': str(e)}
        logger.error(f"❌ Query Similarity tests FAILED: {e}")
    
    # Final Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
    passed_tests = sum(1 for result in test_results.values() if result and result['status'] == 'passed')
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        if result:
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            logger.info(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status'].upper()}")
            if result['status'] == 'failed':
                logger.info(f"    Error: {result['error']}")
        else:
            logger.info(f"⚠️  {test_name.replace('_', ' ').title()}: NOT RUN")
    
    logger.info(f"\nOverall Success Rate: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - AI Q&A System is ready for production!")
    elif passed_tests >= total_tests * 0.75:
        logger.info("⚠️  MOSTLY PASSING - Minor issues need attention")
    else:
        logger.info("❌ SIGNIFICANT ISSUES - Major fixes required")
    
    return test_results


if __name__ == "__main__":
    # Run comprehensive tests
    results = run_comprehensive_tests()
    
    # Exit with appropriate code
    passed_count = sum(1 for r in results.values() if r and r['status'] == 'passed')
    total_count = len(results)
    
    if passed_count == total_count:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed
