#!/usr/bin/env python3
"""
Quick Start Questions for Interactive Q&A
Copy and paste these questions into your interactive session
"""

print("🤖 GEMINI 2.0 FLASH - INTERACTIVE Q&A QUESTIONS")
print("=" * 60)
print()
print("🚀 TO START:")
print("Run: python interactive_qa.py")
print("Choose document: bajaj.pdf or chotgdp.pdf")
print()

print("📄 QUESTIONS FOR BAJAJ.PDF:")
print("-" * 40)
bajaj_questions = [
    "What is Bajaj Auto's main business?",
    "What are the key financial highlights for this year?", 
    "Who are the top management personnel?",
    "What products and services does Bajaj offer?",
    "What are Bajaj's future growth strategies?",
    "How did the company perform financially?",
    "What are the main market segments Bajaj operates in?",
    "What challenges does Bajaj face?",
    "What is Bajaj's competitive position?",
    "What are the key risks mentioned in the report?"
]

for i, q in enumerate(bajaj_questions, 1):
    print(f"{i:2}. {q}")

print()
print("📊 QUESTIONS FOR CHOTGDP.PDF:")
print("-" * 40)
gdp_questions = [
    "What is GDP and how is it measured?",
    "What are the main components of GDP?", 
    "How has GDP growth changed over time?",
    "What factors drive GDP growth?",
    "What is the difference between real and nominal GDP?",
    "How does GDP relate to living standards?",
    "What are the limitations of GDP as a measure?",
    "How does India's GDP compare globally?",
    "What economic policies affect GDP?",
    "What are the future GDP projections?"
]

for i, q in enumerate(gdp_questions, 1):
    print(f"{i:2}. {q}")

print()
print("🔍 FOLLOW-UP QUESTION IDEAS:")
print("-" * 40)
follow_ups = [
    "Can you explain that in more detail?",
    "What are some specific examples?",
    "How does this compare to previous years?",
    "What are the implications of this?",
    "Can you summarize the key points?",
    "What data supports this conclusion?",
    "Are there any risks or limitations?",
    "How reliable is this information?",
    "What trends do you see?",
    "What should I know about this topic?"
]

for i, q in enumerate(follow_ups, 1):
    print(f"{i:2}. {q}")

print()
print("💡 CONVERSATION TIPS:")
print("-" * 40)
print("✅ Start broad, then get specific")
print("✅ Ask for examples and details") 
print("✅ Request comparisons and trends")
print("✅ Seek explanations for technical terms")
print("✅ Ask about implications and significance")
print()

print("🎯 READY TO START!")
print("1. Run: python interactive_qa.py") 
print("2. Choose your document")
print("3. Copy-paste any question above")
print("4. Have a natural conversation!")
print("=" * 60)
