#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP
import pdfplumber
from markdownify import markdownify as md_convert
import os

app = FastMCP("PDF-Md-Converter-server", dependencies=["pdfplumber", "markdownify"])

@app.tool()
def pdf_to_markdown(input_path: str, output_path: str) -> str:
    """
    Receive the path of a PDF file and translates it to markdown, optionally saving it to another file if an output path is specified.

    :param input_path: Path to the PDF file.
    :param output_path: Optional path to save the Markdown file.
    :return: String with Markdown content.
    """
    if not os.path.exists(input_path):
        return f"Error: The file {input_path} does not exist."
    
    try:
        md_blocks = []
        with pdfplumber.open(input_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                # Convertir el texto extraído a formato Markdown
                converted_text = md_convert(text, heading_style="ATX")
                md_blocks.append(f"## Page {page_num}\n\n{converted_text}")
        
        markdown_content = "\n\n".join(md_blocks)
        
        # Guardar el contenido en un archivo si se proporciona output_path
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(markdown_content)
            return f"Markdown file saved in: {output_path}"
        
        return markdown_content
    
    except Exception as e:
        return f"Error processing the PDF: {str(e)}"

if __name__ == "__main__":
    app.run(transport="stdio")