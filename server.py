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
    pdf_path = "/Users/tarikabarghaz/UM6P/AI_PROJECTS/mcp_server_test1/mosip.pdf"
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
        return f"Error: The file {pdf_path} was not found."
    except Exception as e:
        return f"An error occurred while processing the PDF: {e}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')