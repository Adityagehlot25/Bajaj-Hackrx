import re

def split_text(text, max_chunk_size=2000):
    """
    Splits a large text into smaller chunks of a maximum size, trying to respect sentence boundaries.
    """
    
    # First, try to split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 < max_chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    # If any chunk is still too large, split it by words
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            words = chunk.split()
            new_chunk = ""
            for word in words:
                if len(new_chunk) + len(word) + 1 < max_chunk_size:
                    new_chunk += word + " "
                else:
                    final_chunks.append(new_chunk.strip())
                    new_chunk = word + " "
            if new_chunk:
                final_chunks.append(new_chunk.strip())
        else:
            final_chunks.append(chunk)
            
    return final_chunks

if __name__ == '__main__':
    # Example usage with a large text file
    with open('e:/final try/uploads/bajaj.pdf.txt', 'r', encoding='utf-8') as f:
        text = f.read()
        
    chunks = split_text(text)
    
    print(f"Successfully split text into {len(chunks)} chunks.")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: {len(chunk)} characters")
