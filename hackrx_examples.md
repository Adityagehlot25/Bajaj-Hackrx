# HackRX Endpoint Examples

## PowerShell Test
```powershell
$request = @{
    documents = "https://example.com/document.pdf"
    questions = @(
        "What is the main topic?",
        "What are the key findings?",
        "What are the recommendations?"
    )
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer hackrx2024"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://localhost:3000/hackrx/run" -Method POST -Body $request -Headers $headers
```

## Curl Example
```bash
curl -X POST "http://localhost:3000/hackrx/run" \
  -H "Authorization: Bearer hackrx2024" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/document.pdf",
    "questions": [
      "What is the main topic of this document?",
      "What are the key findings?",
      "What recommendations are provided?"
    ]
  }'
```

## Expected Response Format
```json
{
  "success": true,
  "document_url": "https://example.com/document.pdf",
  "document_processed": true,
  "document_id": "doc_12345",
  "chunks_processed": 15,
  "questions_processed": 3,
  "answers": [
    {
      "question": "What is the main topic of this document?",
      "success": true,
      "answer": "The main topic is...",
      "rationale": "Based on my analysis of the document...",
      "source_chunks": ["Relevant text chunk 1", "Relevant text chunk 2"],
      "confidence": "high",
      "sources_used": 3,
      "model": "gemini-2.0-flash-exp"
    }
  ],
  "processing_summary": {
    "total_questions": 3,
    "successful_answers": 3,
    "failed_answers": 0,
    "document_chunks": 15,
    "embedding_model": "embedding-001",
    "ai_model": "gemini-2.0-flash-exp"
  }
}
```

## Authorization Tokens
Valid authorization headers:
- "Bearer hackrx2024"
- "Bearer api-key-12345" 
- "hackrx2024"
- Custom token from HACKRX_API_KEY environment variable

## Supported Document Types
- PDF files
- DOCX files
- Text files
- Any URL-accessible document

## Error Responses
- 401: Missing Authorization header
- 403: Invalid authorization token
- 400: Invalid document URL or parsing error
- 500: Internal processing error
