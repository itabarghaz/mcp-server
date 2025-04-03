import PyPDF2
from typing import Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_server_test1")

@mcp.tool()
async def search_words(query: str) -> str:
    """Search for a query within the text content of mosip.pdf.

    Args:
        query: The text to search for within the PDF document.
    """
    # Use relative path inside the container where Dockerfile copies the PDF
    pdf_path = "mosip.pdf"
    found_text = []

    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text and query.lower() in text.lower():
                    # Basic implementation: return the whole page text if query is found
                    # More sophisticated extraction could be added here (e.g., surrounding sentences)
                    snippet = f"Found on page {page_num + 1}:\n...\n{text[:500]}...\n---" # Limit snippet size and fix f-string
                    found_text.append(snippet)

        if not found_text:
            return f"Query '{query}' not found in {pdf_path}."

        return "\n".join(found_text)

    except FileNotFoundError:
        return f"Error: The file {pdf_path} was not found inside the container."
    except Exception as e:
        return f"An error occurred while processing the PDF: {e}"

if __name__ == "__main__":
    # Initialize and run the server using WebSocket transport
    print("Starting MCP server on WebSocket ws://0.0.0.0:8080") # Added print for clarity
    mcp.run(transport='websocket', host='0.0.0.0', port=8080)