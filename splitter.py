import os
from PyPDF2 import PdfWriter, PdfReader
import argparse
import sys

def process_pdf(input_pdf, tractate, start_page, end_page):
    """
    Process a PDF file by splitting it into groups of two pages and saving them as separate files.
    Files are always named starting from 2.pdf onwards.
    
    Args:
        input_pdf (str): Path to the input PDF file
        tractate (str): Name of the tractate (used for output directory)
        start_page (int): First page to process (1-based index)
        end_page (int): Last page to process (1-based index)
    """
    # Create output directory
    output_dir = os.path.join("merged_pdfs", tractate)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Open the input PDF
        reader = PdfReader(input_pdf)
        
        # Validate page range
        total_pages = len(reader.pages)
        if start_page < 1 or start_page > total_pages:
            print(f"Error: Start page {start_page} is out of range (1-{total_pages})")
            return
        if end_page > total_pages:
            print(f"Warning: End page {end_page} exceeds PDF length. Using last page ({total_pages}) instead.")
            end_page = total_pages
        
        # Convert to 0-based index
        start_idx = start_page - 1
        end_idx = end_page - 1
        
        # Always start output files from 2.pdf
        output_number = 2
        
        # Process pages in pairs
        current_idx = start_idx
        while current_idx <= end_idx:
            writer = PdfWriter()
            
            # Add first page
            writer.add_page(reader.pages[current_idx])
            
            # Add second page if available and within range
            if current_idx + 1 <= end_idx:
                writer.add_page(reader.pages[current_idx + 1])
            
            # Save the output file
            output_filename = os.path.join(output_dir, f"{output_number}.pdf")
            with open(output_filename, "wb") as output_file:
                writer.write(output_file)
            
            print(f"Created {output_filename}")
            
            current_idx += 2
            output_number += 1
        
        print(f"Finished processing {tractate}. Created files from page {start_page} to {end_page}")
        
    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDF pages into grouped files.")
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("tractate", help="Tractate name for output directory")
    parser.add_argument("--start-page", type=int, required=True, help="First page to process")
    parser.add_argument("--end-page", type=int, required=True, help="Last page to process")
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    
    process_pdf(args.input_pdf, args.tractate, args.start_page, args.end_page)
