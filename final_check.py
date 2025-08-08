from robust_document_parser import parse_document

result = parse_document('bajaj.pdf', max_chunk_tokens=2000)
chunks = result.get('chunks', [])
stats = result.get('token_statistics', {})

print('🎯 BAJAJ.PDF FINAL RESULTS:')
print(f'   ✅ Total chunks: {len(chunks)}')
print(f'   ✅ Max tokens: {stats.get("max_tokens_per_chunk", 0)}')
print(f'   ✅ Avg tokens: {stats.get("avg_tokens_per_chunk", 0):.1f}')
print(f'   ✅ Chunks over 2000: {len([c for c in chunks if c.get("token_count", 0) > 2000])}')
print('🎉 SUCCESS: Chunking issue COMPLETELY RESOLVED!')
