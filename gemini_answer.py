"""
Gemini AI Answer Generation Module
Provides intelligent question-answering using Google Gemini API with document context
"""

import requests
import json
import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get API key from environment
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBH6ls3I80rOI3il-uX-7p8eUTSoox05cc')

def get_gemini_answer(
    user_question: str, 
    relevant_clauses: str,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    max_tokens: int = 1000,
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Generate an intelligent answer using Google Gemini API based on user question and relevant document clauses.
    
    Args:
        user_question: The question asked by the user
        relevant_clauses: Document text/clauses relevant to the question  
        api_key: Optional Gemini API key (uses environment variable if not provided)
        model: Gemini model to use (gemini-2.0-flash-exp, gemini-1.5-pro, etc.)
        max_tokens: Maximum tokens in the response
        temperature: Response creativity (0.0 = deterministic, 1.0 = creative)
    
    Returns:
        Dictionary containing the structured response from Gemini API
    """
    
    # Use provided API key or fall back to environment variable
    if not api_key:
        api_key = GEMINI_API_KEY
    
    if not api_key:
        return {
            "success": False,
            "error": "No Gemini API key provided. Set GEMINI_API_KEY environment variable.",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
    
    # Validate inputs
    if not user_question or not user_question.strip():
        return {
            "success": False,
            "error": "User question cannot be empty",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
    
    if not relevant_clauses or not relevant_clauses.strip():
        return {
            "success": False,
            "error": "Relevant clauses cannot be empty",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
    
    # Construct the prompt for Gemini
    prompt = f"""You are an intelligent document analysis assistant. Your task is to provide a precise, well-reasoned answer to a user question based on the provided document context.

INSTRUCTIONS:
1. Provide a clear, accurate answer to the user's question
2. Base your answer strictly on the information provided in the document context
3. Include a detailed rationale explaining your reasoning process
4. Identify specific text chunks that support your answer
5. If the document context doesn't contain enough information, state this clearly
6. Return your response as a JSON object with the exact structure shown below

USER QUESTION:
{user_question}

DOCUMENT CONTEXT:
{relevant_clauses}

REQUIRED RESPONSE FORMAT (return only valid JSON):
{{
    "answer": "Your comprehensive answer to the user question based on the provided context",
    "rationale": "Detailed explanation of your reasoning process, including how you analyzed the context and arrived at your answer",
    "source_chunks": ["Relevant text excerpt 1 that supports your answer", "Relevant text excerpt 2 that supports your answer", "Additional supporting excerpts as needed"]
}}

IMPORTANT: 
- Base your answer ONLY on the provided document context
- Include multiple source chunks in the array if they support different aspects of your answer
- Make your rationale detailed enough to understand your thought process
- Ensure the JSON is properly formatted and valid"""

    # Prepare the API request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    # Construct request payload for Gemini API
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
            "topP": 0.8,
            "topK": 40
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }
    
    try:
        # Make the API request
        logger.info(f"Sending request to Gemini API for question: {user_question[:100]}...")
        
        response = requests.post(
            url, 
            headers=headers, 
            json=payload,
            timeout=30
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        
        # Extract the generated text
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            candidate = response_data["candidates"][0]
            
            if "content" in candidate and "parts" in candidate["content"]:
                generated_text = candidate["content"]["parts"][0].get("text", "")
                
                # Try to parse the JSON response from Gemini
                try:
                    # Clean the response (remove markdown code blocks if present)
                    cleaned_text = generated_text.strip()
                    if cleaned_text.startswith("```json"):
                        cleaned_text = cleaned_text[7:]
                    if cleaned_text.endswith("```"):
                        cleaned_text = cleaned_text[:-3]
                    cleaned_text = cleaned_text.strip()
                    
                    # Parse JSON response
                    parsed_response = json.loads(cleaned_text)
                    
                    # Validate required keys
                    required_keys = ["answer", "rationale", "source_chunks"]
                    if all(key in parsed_response for key in required_keys):
                        return {
                            "success": True,
                            "answer": parsed_response["answer"],
                            "rationale": parsed_response["rationale"],
                            "source_chunks": parsed_response["source_chunks"],
                            "model": model,
                            "tokens_used": response_data.get("usageMetadata", {}).get("totalTokenCount", 0),
                            "raw_response": generated_text
                        }
                    else:
                        # Fallback if JSON structure is incorrect
                        return {
                            "success": True,
                            "answer": parsed_response.get("answer", generated_text),
                            "rationale": parsed_response.get("rationale", "Response parsed from unstructured format"),
                            "source_chunks": parsed_response.get("source_chunks", ["See raw response"]),
                            "model": model,
                            "tokens_used": response_data.get("usageMetadata", {}).get("totalTokenCount", 0),
                            "raw_response": generated_text,
                            "note": "JSON structure was incomplete, parsed partial response"
                        }
                        
                except json.JSONDecodeError:
                    # If JSON parsing fails, return raw text
                    return {
                        "success": True,
                        "answer": generated_text,
                        "rationale": "Response provided in natural language format",
                        "source_chunks": "See raw response for source information",
                        "model": model,
                        "tokens_used": response_data.get("usageMetadata", {}).get("totalTokenCount", 0),
                        "raw_response": generated_text,
                        "note": "Could not parse JSON response, returning raw text"
                    }
            else:
                return {
                    "success": False,
                    "error": "No content generated in Gemini response",
                    "answer": None,
                    "rationale": None,
                    "source_chunks": None,
                    "raw_response": response_data
                }
        else:
            return {
                "success": False,
                "error": "No candidates returned in Gemini response",
                "answer": None,
                "rationale": None,
                "source_chunks": None,
                "raw_response": response_data
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request to Gemini API timed out",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
        
    except requests.exceptions.HTTPError as e:
        error_details = ""
        try:
            error_response = response.json()
            error_details = error_response.get("error", {}).get("message", str(e))
        except:
            error_details = str(e)
            
        return {
            "success": False,
            "error": f"Gemini API HTTP error: {error_details}",
            "answer": None,
            "rationale": None,
            "source_chunks": None,
            "status_code": response.status_code if 'response' in locals() else None
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request error: {str(e)}",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in get_gemini_answer: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }


async def get_gemini_answer_async(
    user_question: str, 
    relevant_clauses: str,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    max_tokens: int = 1000,
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Async version of get_gemini_answer for use in FastAPI endpoints.
    
    Args:
        user_question: The question asked by the user
        relevant_clauses: Document text/clauses relevant to the question
        api_key: Optional Gemini API key
        model: Gemini model to use
        max_tokens: Maximum tokens in response
        temperature: Response creativity level
    
    Returns:
        Dictionary containing the structured response from Gemini API
    """
    
    # Use provided API key or fall back to environment variable
    if not api_key:
        api_key = GEMINI_API_KEY
    
    if not api_key:
        return {
            "success": False,
            "error": "No Gemini API key provided",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
    
    # Validate inputs
    if not user_question or not user_question.strip():
        return {
            "success": False,
            "error": "User question cannot be empty",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
    
    if not relevant_clauses or not relevant_clauses.strip():
        return {
            "success": False,
            "error": "Relevant clauses cannot be empty", 
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
    
    # Construct the prompt
    prompt = f"""You are an intelligent document analysis assistant. Your task is to provide a precise, well-reasoned answer to a user question based on the provided document context.

INSTRUCTIONS:
1. Provide a clear, accurate answer to the user's question
2. Base your answer strictly on the information provided in the document context
3. Include a detailed rationale explaining your reasoning process
4. Identify specific text chunks that support your answer
5. If the document context doesn't contain enough information, state this clearly
6. Return your response as a JSON object with the exact structure shown below

USER QUESTION:
{user_question}

DOCUMENT CONTEXT:
{relevant_clauses}

REQUIRED RESPONSE FORMAT (return only valid JSON):
{{
    "answer": "Your comprehensive answer to the user question based on the provided context",
    "rationale": "Detailed explanation of your reasoning process, including how you analyzed the context and arrived at your answer",
    "source_chunks": ["Relevant text excerpt 1 that supports your answer", "Relevant text excerpt 2 that supports your answer", "Additional supporting excerpts as needed"]
}}

IMPORTANT: 
- Base your answer ONLY on the provided document context
- Include multiple source chunks in the array if they support different aspects of your answer
- Make your rationale detailed enough to understand your thought process
- Ensure the JSON is properly formatted and valid"""

    # Prepare API request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
            "topP": 0.8,
            "topK": 40
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Extract generated text
                    if "candidates" in response_data and len(response_data["candidates"]) > 0:
                        candidate = response_data["candidates"][0]
                        
                        if "content" in candidate and "parts" in candidate["content"]:
                            generated_text = candidate["content"]["parts"][0].get("text", "")
                            
                            # Try to parse JSON response
                            try:
                                cleaned_text = generated_text.strip()
                                if cleaned_text.startswith("```json"):
                                    cleaned_text = cleaned_text[7:]
                                if cleaned_text.endswith("```"):
                                    cleaned_text = cleaned_text[:-3]
                                cleaned_text = cleaned_text.strip()
                                
                                parsed_response = json.loads(cleaned_text)
                                
                                return {
                                    "success": True,
                                    "answer": parsed_response.get("answer", generated_text),
                                    "rationale": parsed_response.get("rationale", "See raw response"),
                                    "source_chunks": parsed_response.get("source_chunks", "See raw response"),
                                    "model": model,
                                    "tokens_used": response_data.get("usageMetadata", {}).get("totalTokenCount", 0),
                                    "raw_response": generated_text
                                }
                                
                            except json.JSONDecodeError:
                                return {
                                    "success": True,
                                    "answer": generated_text,
                                    "rationale": "Response provided in natural language format",
                                    "source_chunks": "See raw response",
                                    "model": model,
                                    "raw_response": generated_text,
                                    "note": "Could not parse JSON, returning raw text"
                                }
                        else:
                            return {
                                "success": False,
                                "error": "No content generated in response",
                                "answer": None,
                                "rationale": None,
                                "source_chunks": None
                            }
                    else:
                        return {
                            "success": False,
                            "error": "No candidates in response",
                            "answer": None,
                            "rationale": None,
                            "source_chunks": None
                        }
                else:
                    error_data = await response.text()
                    return {
                        "success": False,
                        "error": f"API error {response.status}: {error_data}",
                        "answer": None,
                        "rationale": None,
                        "source_chunks": None
                    }
                    
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Request timed out",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Async request error: {str(e)}",
            "answer": None,
            "rationale": None,
            "source_chunks": None
        }


# Example usage and testing functions
def example_usage():
    """Example usage of the get_gemini_answer function"""
    
    # Example user question
    user_question = "What are the payment terms mentioned in the contract?"
    
    # Example relevant clauses (would come from your vector search)
    relevant_clauses = """
    Section 3.1: Payment Terms
    The Client shall pay the full amount within 30 days of invoice date.
    Late payments will incur a 2% monthly interest charge.
    
    Section 3.2: Payment Method
    Payments must be made via bank transfer or certified check.
    Credit card payments are not accepted for amounts over $10,000.
    """
    
    # Get answer from Gemini
    result = get_gemini_answer(user_question, relevant_clauses)
    
    if result["success"]:
        print("SUCCESS: Gemini provided an answer")
        print(f"Answer: {result['answer']}")
        print(f"Rationale: {result['rationale']}")
        print(f"Source Clauses: {result['source_chunks']}")
        if "tokens_used" in result:
            print(f"Tokens used: {result['tokens_used']}")
    else:
        print(f"ERROR: {result['error']}")
    
    return result


if __name__ == "__main__":
    # Test the function
    print("Testing get_gemini_answer function...")
    example_usage()
