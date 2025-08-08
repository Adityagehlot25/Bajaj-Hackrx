#!/usr/bin/env python3
"""
Interactive Q&A Questions Demo
Great questions to try with your document Q&A system
"""

def show_sample_questions():
    """Display sample questions for interactive Q&A"""
    
    print("🤖 INTERACTIVE Q&A WITH GEMINI 2.0 FLASH")
    print("=" * 60)
    print("Your AI Q&A system is ready! Here are great questions to try:")
    print()
    
    # Questions for Bajaj document
    print("📄 FOR BAJAJ.PDF DOCUMENT:")
    print("-" * 40)
    bajaj_questions = [
        "What is Bajaj Auto's main business?",
        "What are the company's financial highlights?", 
        "Who are the key management personnel?",
        "What products does Bajaj manufacture?",
        "What are the company's future plans?",
        "How did Bajaj perform this year?",
        "What are the major risks mentioned?",
        "What markets does Bajaj operate in?",
        "What are the key financial ratios?",
        "What is the company's growth strategy?"
    ]
    
    for i, q in enumerate(bajaj_questions, 1):
        print(f"  {i:2d}. {q}")
    
    print()
    
    # Questions for GDP document  
    print("📊 FOR CHOTGDP.PDF DOCUMENT:")
    print("-" * 40)
    gdp_questions = [
        "What is GDP and how is it calculated?",
        "What are the components of GDP?",
        "How has GDP changed over time?", 
        "What factors affect GDP growth?",
        "What is the relationship between GDP and inflation?",
        "How does GDP compare across countries?",
        "What are the limitations of GDP?",
        "What is real vs nominal GDP?",
        "How is per capita GDP calculated?",
        "What economic policies affect GDP?"
    ]
    
    for i, q in enumerate(gdp_questions, 1):
        print(f"  {i:2d}. {q}")
    
    print()
    
    # General analysis questions
    print("🔍 ADVANCED ANALYSIS QUESTIONS:")
    print("-" * 40)
    advanced_questions = [
        "Summarize the key points in this document",
        "What are the main conclusions drawn?",
        "Compare and contrast different sections",
        "What trends or patterns are mentioned?", 
        "What are the implications of these findings?",
        "Explain the methodology used",
        "What are the strengths and weaknesses discussed?",
        "How does this relate to current market conditions?",
        "What recommendations are provided?",
        "What questions remain unanswered?"
    ]
    
    for i, q in enumerate(advanced_questions, 1):
        print(f"  {i:2d}. {q}")
    
    print()
    print("🎯 HOW TO USE INTERACTIVE Q&A:")
    print("-" * 40)
    print("1. Run: python interactive_qa.py")
    print("2. Choose a document to analyze")
    print("3. Ask any question from the list above")
    print("4. Try follow-up questions for deeper insights")
    print("5. Use commands like 'help', 'docs', 'stats'")
    print()
    
    print("💡 TIPS FOR BETTER ANSWERS:")
    print("-" * 40)
    print("✅ Be specific: 'What is Bajaj's revenue?' vs 'Tell me about Bajaj'")
    print("✅ Ask follow-ups: 'Can you explain that in more detail?'") 
    print("✅ Compare data: 'How does 2023 compare to 2022?'")
    print("✅ Request examples: 'Give me examples of this concept'")
    print("✅ Seek clarification: 'What does this technical term mean?'")
    print()
    
    print("🚀 READY TO START?")
    print("Run: python interactive_qa.py")
    print("=" * 60)

def demo_quick_questions():
    """Demo with a few quick questions"""
    
    print("\n🧪 QUICK DEMO - TRY THESE RIGHT NOW:")
    print("=" * 60)
    
    try:
        # Import the QA system
        import sys
        sys.path.append('.')
        
        # Check if documents are available
        import os
        docs_available = []
        
        if os.path.exists('bajaj.pdf'):
            docs_available.append('bajaj.pdf')
        if os.path.exists('chotgdp.pdf'):  
            docs_available.append('chotgdp.pdf')
        
        if docs_available:
            print(f"📚 Documents found: {', '.join(docs_available)}")
            print("\n🎯 Try these questions:")
            
            if 'bajaj.pdf' in docs_available:
                print("  python -c \"from interactive_qa import DocumentQASession; qa = DocumentQASession(); qa.load_document('bajaj.pdf'); print(qa.ask_question('What is Bajaj Auto?'))\"")
            
            print("\n💡 Or start interactive mode:")
            print("  python interactive_qa.py")
            
        else:
            print("📄 No documents found. Place your PDFs in this directory first.")
            
    except ImportError:
        print("🔧 System needs setup. Run: python setup_api_key.py first")
    
    print("=" * 60)

if __name__ == "__main__":
    show_sample_questions()
    demo_quick_questions()
