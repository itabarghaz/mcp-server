import PyPDF2
from typing import Any, List, Dict
import re
import os
from mcp.server.fastmcp import FastMCP
from mcp.transports.sse import SSETransport

# Initialize FastMCP server
mcp = FastMCP("mcp_server_test1")

@mcp.tool()
async def search_words(query: str) -> str:
    """Search for a query within the text content of mosip.pdf.

    Args:
        query: The text to search for within the PDF document.
    """
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

if __name__ == "__main__":
    # Configure SSE transport with explicit host and port
    transport = SSETransport(host="0.0.0.0", port=8080)
    
    # Initialize and run the server using the configured SSE transport
    mcp.run(transport=transport)
    
    # Print startup message for debugging
    print(f"MCP Server started with SSE transport on 0.0.0.0:8080")