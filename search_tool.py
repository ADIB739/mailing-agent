import os
from langchain.tools import tool
import requests
from dotenv import load_dotenv

load_dotenv()

@tool
def web_search_tool(query: str) -> str:
    """
    Search the web for information on any topic.
    
    Args:
        query: Search query string
    
    Returns:
        Search results with relevant information
    """
    try:
        # Using SerpAPI (get free API key from serpapi.com)
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        
        if not serpapi_key:
            return "Error: SERPAPI_API_KEY not found. Please get a free API key from serpapi.com"
        
        # SerpAPI search
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": serpapi_key,
            "engine": "google",
            "num": 5  # Top 5 results
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "organic_results" not in data:
            return f"No search results found for: {query}"
        
        # Format results
        results = []
        for i, result in enumerate(data["organic_results"][:5], 1):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No description")
            link = result.get("link", "")
            
            results.append(f"{i}. **{title}**\n   {snippet}\n   🔗 {link}\n")
        
        search_summary = f"🔍 **Web Search Results for:** {query}\n\n" + "\n".join(results)
        return search_summary
        
    except Exception as e:
        # Fallback to DuckDuckGo (free, no API key needed)
        return fallback_search(query)

def fallback_search(query: str) -> str:
    """Fallback search using DuckDuckGo (no API key required)"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # DuckDuckGo instant answers
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        results = []
        
        # Get abstract
        if data.get("Abstract"):
            results.append(f"📄 **Overview:** {data['Abstract']}")
        
        # Get definition
        if data.get("Definition"):
            results.append(f"📖 **Definition:** {data['Definition']}")
        
        # Get related topics
        if data.get("RelatedTopics"):
            topics = []
            for topic in data["RelatedTopics"][:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    topics.append(f"• {topic['Text'][:100]}...")
            if topics:
                results.append(f"🔗 **Related:**\n" + "\n".join(topics))
        
        if results:
            return f"🔍 **Search Results for:** {query}\n\n" + "\n\n".join(results)
        else:
            return f"🔍 Search completed for '{query}' but no detailed results available. Try being more specific."
            
    except Exception as e:
        return f"❌ Search failed: {str(e)}"