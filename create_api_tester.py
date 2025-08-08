#!/usr/bin/env python3
"""
Simple Browser Test for HackRX API
Creates a simple HTML page to test the API
"""

html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>HackRX API Tester</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
        .success { background-color: #d4edda; border-color: #c3e6cb; }
        .error { background-color: #f8d7da; border-color: #f5c6cb; }
        input, textarea, button { width: 100%; padding: 10px; margin: 5px 0; }
        button { background-color: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .result { white-space: pre-wrap; max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 HackRX API Tester</h1>
        <p>Test your document Q&A API endpoint</p>
        
        <div class="section">
            <h3>📍 API Endpoint</h3>
            <p><strong>URL:</strong> http://localhost:8000/api/v1/hackrx/run</p>
            <p><strong>Method:</strong> POST</p>
        </div>
        
        <div class="section">
            <h3>🧪 Test Request</h3>
            <label>Document URL:</label>
            <input type="url" id="docUrl" value="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" placeholder="Enter document URL">
            
            <label>Questions (one per line):</label>
            <textarea id="questions" rows="5" placeholder="Enter questions, one per line">What is this document about?
What are the main points?
Who is the target audience?</textarea>
            
            <button onclick="testAPI()">🚀 Test API</button>
        </div>
        
        <div class="section" id="resultSection" style="display: none;">
            <h3>📄 Results</h3>
            <div id="results" class="result"></div>
        </div>
        
        <div class="section">
            <h3>💡 Sample cURL Command</h3>
            <pre id="curlCommand">curl -X POST "http://localhost:8000/api/v1/hackrx/run" \\
  -H "Content-Type: application/json" \\
  -d '{
    "document_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    "questions": [
      "What is this document about?",
      "What are the main points?"
    ]
  }'</pre>
        </div>
    </div>
    
    <script>
        async function testAPI() {
            const docUrl = document.getElementById('docUrl').value;
            const questionsText = document.getElementById('questions').value;
            const questions = questionsText.split('\\n').filter(q => q.trim());
            
            const resultSection = document.getElementById('resultSection');
            const resultsDiv = document.getElementById('results');
            
            if (!docUrl || questions.length === 0) {
                resultsDiv.innerHTML = '❌ Please provide both document URL and questions';
                resultsDiv.className = 'result error';
                resultSection.style.display = 'block';
                return;
            }
            
            resultsDiv.innerHTML = '🔄 Testing API... Please wait...';
            resultsDiv.className = 'result';
            resultSection.style.display = 'block';
            
            try {
                const response = await fetch('http://localhost:8000/api/v1/hackrx/run', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        document_url: docUrl,
                        questions: questions
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    
                    let output = '✅ SUCCESS!\\n\\n';
                    output += '📝 ANSWERS:\\n';
                    output += '=' + '='.repeat(50) + '\\n';
                    
                    result.answers.forEach((answer, index) => {
                        output += `Q${index + 1}: ${questions[index]}\\n`;
                        output += `A${index + 1}: ${answer}\\n\\n`;
                    });
                    
                    if (result.processing_info) {
                        const info = result.processing_info;
                        output += '📊 PROCESSING INFO:\\n';
                        output += '-'.repeat(30) + '\\n';
                        output += `Chunks created: ${info.chunks_created || 'N/A'}\\n`;
                        output += `Embeddings generated: ${info.embeddings_generated || 'N/A'}\\n`;
                        output += `Processing time: ${info.total_time_seconds || 'N/A'} seconds\\n`;
                    }
                    
                    resultsDiv.innerHTML = output;
                    resultsDiv.className = 'result success';
                    
                } else {
                    const errorText = await response.text();
                    resultsDiv.innerHTML = `❌ API Error (${response.status}): ${errorText}`;
                    resultsDiv.className = 'result error';
                }
                
            } catch (error) {
                resultsDiv.innerHTML = `❌ Request failed: ${error.message}`;
                resultsDiv.className = 'result error';
            }
        }
    </script>
</body>
</html>'''

# Write the HTML file
with open('hackrx_api_tester.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Created hackrx_api_tester.html")
print("🌐 Open this file in your browser to test the API")
print("📍 File location: hackrx_api_tester.html")
print()
print("💡 Alternative testing methods:")
print("1. Browser: Open hackrx_api_tester.html")
print("2. Python: python quick_test_api.py") 
print("3. Documentation: http://localhost:8000/docs")
print("4. Health check: http://localhost:8000/api/v1/hackrx/health")
