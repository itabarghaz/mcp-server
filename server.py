import PyPDF2
from typing import Any, List, Dict
import re
import os
import threading
from mcp.server.fastmcp import FastMCP
from flask import Flask, request, jsonify

# Initialize FastMCP server
mcp = FastMCP("mcp_server_test1")

# Create Flask app for HTTP access
app = Flask(__name__)

@mcp.tool()
async def search_words(query: str) -> str:
    """Search for a query within the text content of mosip.pdf.

    Args:
        query: The text to search for within the PDF document.
    """
    return search_pdf(query)

def search_pdf(query: str) -> str:
    """Implementation of PDF search that can be used by both MCP and HTTP endpoints"""
    # Use container path instead of host path
    pdf_path = "/app/mosip.pdf"
    found_text = []

    try:
        if not os.path.exists(pdf_path):
            return f"Error: The file {pdf_path} was not found."
            
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(reader.pages)
            
            # Search in each page
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                if not text:
                    continue
                    
                # Case-insensitive search
                if query.lower() in text.lower():
                    # Find the context around the match
                    lower_text = text.lower()
                    query_lower = query.lower()
                    
                    # Get all occurrences of the query in this page
                    all_positions = [m.start() for m in re.finditer(re.escape(query_lower), lower_text)]
                    
                    for pos in all_positions:
                        # Extract context (about 100 chars before and after the match)
                        start_pos = max(0, pos - 100)
                        end_pos = min(len(text), pos + len(query) + 100)
                        
                        # Get the actual text (original case)
                        context = text[start_pos:end_pos]
                        
                        # Add ellipsis if we're not at the beginning/end
                        prefix = "..." if start_pos > 0 else ""
                        suffix = "..." if end_pos < len(text) else ""
                        
                        # Format the result
                        snippet = f"Found on page {page_num + 1}:\n{prefix}{context}{suffix}\n---"
                        found_text.append(snippet)

        if not found_text:
            return f"Query '{query}' not found in the PDF document."

        # Return the results with a summary
        return f"Found {len(found_text)} occurrences of '{query}' in the document:\n\n" + "\n".join(found_text)

    except Exception as e:
        return f"An error occurred while processing the PDF: {e}"

# HTTP endpoint for search
@app.route('/search', methods=['POST'])
def http_search():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    
    result = search_pdf(data['query'])
    return jsonify({"result": result})

# Function to run the MCP server in a separate thread
def run_mcp_server():
    print("Starting MCP Server with stdio transport")
    mcp.run(transport='stdio')

# Function to run the Flask server
def run_flask_server():
    print("Starting Flask HTTP server on port 8080")
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    # Start the MCP server in a separate thread
    mcp_thread = threading.Thread(target=run_mcp_server)
    mcp_thread.daemon = True
    mcp_thread.start()
    
    # Run the Flask server in the main thread
    run_flask_server()