#!/usr/bin/env python3
"""
Smart Insurance Query Examples for Testing
Advanced queries that showcase Gemini 2.0 Flash reasoning capabilities
"""

def show_smart_queries():
    """Display smart insurance queries for testing"""
    
    print("🧠 SMART INSURANCE QUERIES FOR GEMINI 2.0 FLASH")
    print("=" * 70)
    print("These queries test complex reasoning, policy analysis, and edge cases")
    print()
    
    # Complex Medical Procedure Queries
    print("🏥 COMPLEX MEDICAL PROCEDURE QUERIES")
    print("-" * 50)
    
    medical_queries = [
        {
            "query": "A 32-year-old male needs bypass surgery after 18 months of policy coverage. The surgery costs ₹8 lakhs and will be done at Apollo Hospital Chennai. What is the eligible payout and are there any waiting period restrictions?",
            "tests": ["Waiting periods", "Cost limits", "Hospital network", "Age factors"]
        },
        {
            "query": "A 55-year-old female diabetic patient requires dialysis treatment. She has been covered for 6 months. The treatment is ongoing and costs ₹15,000 per session, 3 times per week. What coverage applies for this chronic condition?",
            "tests": ["Pre-existing conditions", "Chronic treatment", "Session limits", "Ongoing costs"]
        },
        {
            "query": "Emergency appendectomy for a 28-year-old male during a business trip to Dubai. Policy active for 3 years. Surgery cost $12,000 USD. Hospital not in network. What is the coverage for overseas emergency treatment?",
            "tests": ["International coverage", "Emergency vs planned", "Currency conversion", "Network restrictions"]
        },
        {
            "query": "A 45-year-old woman needs knee replacement surgery due to a sports injury that occurred 2 years before policy inception. Policy has been active for 30 months. Surgery recommended by orthopedic specialist. What are the coverage implications?",
            "tests": ["Pre-existing injury", "Waiting periods", "Specialist recommendations", "Sports-related injuries"]
        }
    ]
    
    for i, item in enumerate(medical_queries, 1):
        print(f"\n{i}. QUERY:")
        print(f"   {item['query']}")
        print(f"   🧪 TESTS: {', '.join(item['tests'])}")
    
    print("\n" + "=" * 70)
    
    # Maternity and Family Queries
    print("\n👶 MATERNITY & FAMILY COVERAGE QUERIES")
    print("-" * 50)
    
    maternity_queries = [
        {
            "query": "A 29-year-old newly married woman wants to plan pregnancy. Policy active for 8 months. What is the waiting period for maternity coverage and what expenses are included for normal delivery vs C-section?",
            "tests": ["Maternity waiting periods", "Delivery types", "Coverage scope", "Planning scenarios"]
        },
        {
            "query": "Newborn baby needs NICU care immediately after birth. Mother's policy covers delivery but baby not yet added to policy. NICU costs ₹2 lakhs. What coverage applies for newborn emergency care?",
            "tests": ["Newborn coverage", "Emergency care", "Policy addition timing", "High-cost scenarios"]
        },
        {
            "query": "Family floater policy for 4 members (parents aged 45, 42 and children aged 15, 12). Teenager breaks leg during sports, requires surgery costing ₹1.5 lakhs. How does family floater coverage work for dependent children?",
            "tests": ["Family floater mechanics", "Dependent coverage", "Sports injuries", "Age-based coverage"]
        }
    ]
    
    for i, item in enumerate(maternity_queries, 1):
        print(f"\n{i}. QUERY:")
        print(f"   {item['query']}")
        print(f"   🧪 TESTS: {', '.join(item['tests'])}")
    
    print("\n" + "=" * 70)
    
    # Edge Case and Limitation Queries
    print("\n🔍 EDGE CASE & POLICY LIMITATION QUERIES")
    print("-" * 50)
    
    edge_queries = [
        {
            "query": "Policy holder moves from Mumbai to rural Assam. Local hospital not in network, nearest network hospital 200km away. Patient has heart attack requiring immediate surgery. What coverage applies for emergency care outside network due to geographical constraints?",
            "tests": ["Geographic limitations", "Network availability", "Emergency exceptions", "Rural healthcare access"]
        },
        {
            "query": "A 60-year-old man with existing hypertension develops COVID-19 complications requiring ventilator support for 15 days. ICU costs ₹12 lakhs. Policy active for 2 years. How does pandemic coverage interact with pre-existing condition clauses?",
            "tests": ["Pandemic coverage", "Pre-existing interactions", "ICU limits", "Extended treatment"]
        },
        {
            "query": "Policy holder undergoes experimental cancer treatment not yet approved in India, but available in Germany. Treatment costs €50,000. Patient willing to pay and wants reimbursement. What coverage applies for experimental/overseas treatments?",
            "tests": ["Experimental treatments", "International care", "Approval requirements", "Reimbursement limits"]
        },
        {
            "query": "Corporate group policy converted to individual policy after job change. Waiting periods reset or continued? Employee had gastric surgery planned under group policy. Individual policy active for 2 months. What coverage continuity applies?",
            "tests": ["Policy conversions", "Waiting period continuity", "Group to individual", "Planned procedures"]
        }
    ]
    
    for i, item in enumerate(edge_queries, 1):
        print(f"\n{i}. QUERY:")
        print(f"   {item['query']}")
        print(f"   🧪 TESTS: {', '.join(item['tests'])}")
    
    print("\n" + "=" * 70)
    
    # Multi-factor Analysis Queries
    print("\n🎯 MULTI-FACTOR ANALYSIS QUERIES")
    print("-" * 50)
    
    complex_queries = [
        {
            "query": "Compare coverage for same procedure (cataract surgery) for three scenarios: 1) 35-year-old with 6 months coverage 2) 65-year-old with 3 years coverage 3) 50-year-old senior citizen plan with 1 year coverage. Analyze eligibility, waiting periods, and payout differences.",
            "tests": ["Comparative analysis", "Age factors", "Plan types", "Multiple scenarios"]
        },
        {
            "query": "Family claims analysis: Father needs cardiac surgery (₹5 lakhs), mother needs diabetes management (₹50,000/year), teenage son breaks bone (₹75,000). Family floater limit ₹5 lakhs. Policy active 2 years. Prioritize claims and analyze coverage strategy for family.",
            "tests": ["Multiple claims", "Family prioritization", "Limit management", "Strategic planning"]
        },
        {
            "query": "Risk assessment query: 45-year-old smoker with family history of heart disease wants to understand policy coverage for potential cardiac events. What preventive care is covered? How do lifestyle factors affect claims? What are the coverage limitations for lifestyle-related conditions?",
            "tests": ["Risk assessment", "Preventive care", "Lifestyle factors", "Predictive analysis"]
        }
    ]
    
    for i, item in enumerate(complex_queries, 1):
        print(f"\n{i}. QUERY:")
        print(f"   {item['query']}")
        print(f"   🧪 TESTS: {', '.join(item['tests'])}")
    
    print("\n" + "=" * 70)
    
    # How to Test
    print("\n🚀 HOW TO TEST THESE QUERIES:")
    print("-" * 50)
    print("1. 📂 Run: python insurance_claim_analyzer.py")
    print("2. 📋 Copy any query above")
    print("3. 🤖 Watch Gemini 2.0 Flash analyze multiple factors")
    print("4. 🧠 See structured reasoning with source references")
    print("5. ⚖️ Observe professional insurance logic")
    print()
    print("💡 WHAT MAKES THESE QUERIES SMART:")
    print("✅ Multiple variables (age, duration, cost, location)")
    print("✅ Edge cases and policy conflicts")
    print("✅ Real-world complexity")
    print("✅ Professional decision-making scenarios")
    print("✅ Comparative and predictive analysis")
    print()
    print("🎯 YOUR GEMINI 2.0 FLASH SYSTEM WILL:")
    print("✅ Parse complex scenarios")
    print("✅ Apply multiple policy rules")
    print("✅ Provide structured reasoning")
    print("✅ Reference specific policy sections")
    print("✅ Handle uncertainty professionally")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    show_smart_queries()
