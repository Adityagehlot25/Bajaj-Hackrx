#!/usr/bin/env python3
"""
HackRX API Deployment Diagnostic Tool
Identifies and provides solutions for server processing errors
"""

import os
import asyncio
import aiohttp
import json
import requests
from datetime import datetime
import traceback

class HackRXDiagnostic:
    def __init__(self):
        self.base_url = "https://bajaj-hackrx-bnm2.onrender.com"
        self.api_key = "AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ"
        
    def test_gemini_api_key(self):
        """Test if the Gemini API key works locally"""
        print("\n🔑 Testing Gemini API Key Locally...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content("Hello, this is a test.")
            
            if response.text:
                print("✅ Gemini API Key: WORKING")
                print(f"📝 Test Response: {response.text[:100]}...")
                return True
            else:
                print("❌ Gemini API Key: No response generated")
                return False
                
        except Exception as e:
            print(f"❌ Gemini API Key: FAILED - {e}")
            return False
    
    def test_health_endpoint(self):
        """Test the health endpoint to check API key status"""
        print("\n🏥 Testing Health Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/v1/hackrx/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Health Endpoint: WORKING")
                print(f"🔑 API Key Status: {health_data.get('api_key_status', 'unknown')}")
                print(f"📊 Overall Status: {health_data.get('status', 'unknown')}")
                
                if health_data.get('api_key_status') == 'missing':
                    print("\n❌ CRITICAL ISSUE: API Key Missing in Render Environment!")
                    print("🔧 SOLUTION: Add GEMINI_API_KEY to Render environment variables")
                    return False
                elif health_data.get('api_key_status') == 'configured':
                    print("✅ API Key is configured in Render")
                    return True
                    
            else:
                print(f"❌ Health Endpoint: Failed ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Health Endpoint: ERROR - {e}")
            return False
    
    def test_simple_processing(self):
        """Test with a very simple document and question"""
        print("\n🧪 Testing Simple Document Processing...")
        
        # Use a very small, simple PDF
        test_payload = {
            "document_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "questions": ["What is this document?"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer hackrx_test_token_12345"
        }
        
        try:
            print("⏳ Sending request to deployed API...")
            start_time = datetime.now()
            
            response = requests.post(
                f"{self.base_url}/api/v1/hackrx/run",
                headers=headers,
                json=test_payload,
                timeout=90  # 90 second timeout
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"⏱️ Processing Time: {processing_time:.1f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                answers = result.get('answers', [])
                processing_info = result.get('processing_info', {})
                
                print("✅ Request Status: SUCCESS")
                print(f"📄 Answers Received: {len(answers)}")
                
                for i, answer in enumerate(answers):
                    print(f"\n🤖 Answer {i+1}:")
                    print(f"   {answer[:150]}...")
                    
                    if "server error" in answer.lower():
                        print("   ❌ SERVER ERROR DETECTED!")
                        self.analyze_server_error(answer)
                    elif "error" in answer.lower():
                        print("   ⚠️ Processing error detected")
                        self.analyze_processing_error(answer)
                    else:
                        print("   ✅ Answer generated successfully")
                
                # Show processing info if available
                if processing_info:
                    print(f"\n📊 Processing Info:")
                    for key, value in processing_info.items():
                        print(f"   {key}: {value}")
                
                return True
                
            else:
                print(f"❌ Request Status: FAILED ({response.status_code})")
                try:
                    error_data = response.json()
                    print(f"🚫 Error Details: {error_data}")
                except:
                    print(f"🚫 Error Text: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏱️ REQUEST TIMEOUT - This suggests:")
            print("   • Free tier memory/CPU limits exceeded")
            print("   • Large document processing taking too long")
            print("   • Cold start delays")
            return False
            
        except Exception as e:
            print(f"❌ Request Error: {e}")
            traceback.print_exc()
            return False
    
    def analyze_server_error(self, answer):
        """Analyze server error message for specific issues"""
        print("\n🔍 Analyzing Server Error...")
        
        if "api" in answer.lower() and "key" in answer.lower():
            print("   🔑 Likely Cause: Gemini API Key Issue")
            print("   🔧 Solutions:")
            print("      1. Check API key in Render environment variables")
            print("      2. Verify API key format (starts with AIza, 39 chars)")
            print("      3. Test API key quota/billing status")
            
        elif "memory" in answer.lower() or "timeout" in answer.lower():
            print("   💾 Likely Cause: Resource Limits")
            print("   🔧 Solutions:")
            print("      1. Upgrade Render plan for more memory")
            print("      2. Use smaller documents for testing")
            print("      3. Optimize chunk sizes in processing")
            
        elif "quota" in answer.lower() or "limit" in answer.lower():
            print("   📊 Likely Cause: API Rate/Quota Limits")
            print("   🔧 Solutions:")
            print("      1. Check Gemini API quota in Google Cloud Console")
            print("      2. Add delays between API calls")
            print("      3. Verify billing is enabled for Gemini API")
            
        else:
            print("   ❓ Generic server error")
            print("   🔧 General Solutions:")
            print("      1. Check Render deployment logs")
            print("      2. Verify all environment variables")
            print("      3. Try with minimal test document")
    
    def analyze_processing_error(self, answer):
        """Analyze processing error for specific issues"""
        print("\n🔍 Analyzing Processing Error...")
        
        if "embedding" in answer.lower():
            print("   🧮 Embedding Generation Issue")
            print("   🔧 Solutions:")
            print("      1. Check Gemini embedding API access")
            print("      2. Reduce batch sizes for embeddings")
            print("      3. Add retry logic with exponential backoff")
            
        elif "download" in answer.lower():
            print("   📥 Document Download Issue")
            print("   🔧 Solutions:")
            print("      1. Verify document URL is accessible")
            print("      2. Check network connectivity from Render")
            print("      3. Try with different document URL")
            
        elif "parse" in answer.lower():
            print("   📄 Document Parsing Issue")
            print("   🔧 Solutions:")
            print("      1. Verify document format (PDF/DOCX)")
            print("      2. Check document isn't corrupted")
            print("      3. Try with simpler document format")
    
    def provide_solutions(self):
        """Provide prioritized solutions based on test results"""
        print("\n" + "="*60)
        print("🎯 PRIORITIZED SOLUTIONS")
        print("="*60)
        
        print("\n🥇 HIGHEST PRIORITY (Fix These First):")
        print("1. 🔑 Verify Render Environment Variables:")
        print("   • Go to Render Dashboard → Your Service → Environment")
        print("   • Add: GEMINI_API_KEY=AIzaSyBDjD9Y7eCR79neOpjIpdxeoppXRiZHqtQ")
        print("   • Save Changes (triggers automatic redeploy)")
        
        print("\n🥈 MEDIUM PRIORITY (Performance Optimization):")
        print("2. 💾 Upgrade Render Plan:")
        print("   • Free tier: 512MB RAM, 0.1 CPU")
        print("   • Starter plan: 1GB RAM, 0.5 CPU ($7/month)")
        print("   • Better for document processing workloads")
        
        print("3. ⚡ Optimize Processing:")
        print("   • Use smaller documents for initial testing")
        print("   • Reduce chunk sizes (500 tokens instead of 1000)")
        print("   • Process fewer questions per request")
        
        print("\n🥉 LOW PRIORITY (Advanced Optimization):")
        print("4. 🔧 Code Optimizations:")
        print("   • Add better error handling and retry logic")
        print("   • Implement caching for repeated documents")
        print("   • Add request queuing for high load")
        
        print("\n🚀 QUICK TEST COMMAND:")
        print("After fixing environment variables, test with:")
        print("curl -X POST https://bajaj-hackrx-bnm2.onrender.com/api/v1/hackrx/run \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -H 'Authorization: Bearer test_token_123456789' \\")
        print("  -d '{")
        print('    "document_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",')
        print('    "questions": ["What is this document about?"]')
        print("  }'")
    
    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        print("🚀 HackRX API Deployment Diagnostic Tool")
        print("="*60)
        print(f"🎯 Target API: {self.base_url}")
        print(f"📅 Test Time: {datetime.now().isoformat()}")
        
        # Test suite
        tests_passed = 0
        total_tests = 3
        
        if self.test_gemini_api_key():
            tests_passed += 1
            
        if self.test_health_endpoint():
            tests_passed += 1
            
        if self.test_simple_processing():
            tests_passed += 1
        
        # Summary
        print("\n" + "="*60)
        print(f"📊 DIAGNOSTIC SUMMARY: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED! Your API is working correctly!")
        elif tests_passed >= 2:
            print("⚠️ PARTIAL SUCCESS - Minor issues detected")
        else:
            print("❌ MAJOR ISSUES DETECTED - Requires immediate attention")
        
        self.provide_solutions()

if __name__ == "__main__":
    diagnostic = HackRXDiagnostic()
    diagnostic.run_full_diagnostic()
