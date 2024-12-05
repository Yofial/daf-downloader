import requests
import os
from PyPDF2 import PdfMerger, PdfReader
import io
from PyPDF2.errors import PdfReadError
import argparse
import sys

def download_pdf(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}. Error: {e}")
        return None

def is_valid_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        return len(reader.pages) > 0
    except PdfReadError:
        return False

def is_empty_pdf(pdf_file):
    return pdf_file.getbuffer().nbytes < 1000  # Assuming empty PDFs are less than 1KB

def merge_pdfs(pdf1, pdf2, output_filename):
    merger = PdfMerger()
    try:
        if is_valid_pdf(pdf1):
            merger.append(pdf1)
        else:
            print(f"Invalid PDF: {pdf1}")
            return False
        
        if pdf2 is not None and is_valid_pdf(pdf2):
            merger.append(pdf2)
        elif pdf2 is not None:
            print(f"Invalid PDF: {pdf2}")
            return False
        
        merger.write(output_filename)
        merger.close()
        return True
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False

def main(tractate, tractate_id, start_page):
    base_url = f"https://beta.hebrewbooks.org/pagefeed/hebrewbooks_org_{tractate_id}_{{0}}.pdf"
    output_dir = os.path.join("merged_pdfs", tractate)  # Using tractate name instead of ID
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://beta.hebrewbooks.org/'
    }

    output_number = max(2, ((start_page - 1) // 2) + 2)  # Ensure output number starts at 2 or higher
    page_number = start_page
    last_processed_page = start_page - 1  # Initialize to start_page - 1

    while True:
        print(f"Processing pages {page_number} and {page_number+1}")
        
        # Download two consecutive pages
        pdf1 = download_pdf(base_url.format(page_number), headers)
        pdf2 = download_pdf(base_url.format(page_number+1), headers)
        
        if pdf1 is None:
            print(f"Skipping page {page_number} due to download error")
            page_number += 1
            continue
        
        if is_empty_pdf(pdf1):
            print(f"Reached end of tractate at page {last_processed_page}")
            break
        
        output_filename = os.path.join(output_dir, f"{output_number}.pdf")
        
        if pdf2 is None or is_empty_pdf(pdf2):
            # Handle the case of a single page at the end
            if merge_pdfs(pdf1, None, output_filename):
                print(f"Created {output_filename} (single page)")
                last_processed_page = page_number
            else:
                print(f"Failed to create {output_filename}")
            break
        
        # Merge the two pages
        if merge_pdfs(pdf1, pdf2, output_filename):
            print(f"Created {output_filename}")
            last_processed_page = page_number + 1
        else:
            print(f"Failed to create {output_filename}")
        
        output_number += 1  # Increment the output number by 1 each time
        page_number += 2  # Move to the next pair of pages

    print(f"Finished processing {tractate}. Last page processed: {last_processed_page}")

if __name__ == "__main__":
    tractate_ids = {
        "BR": "36083",
        "SB": "36104",
        "ER": "36087",
        "PS": "36101",
        "SK": "36105",
        "YM": "36112",
        "SK": "36108",
        "BZ": "36082",
        "RH": "36102",
        "TN": "36109",
        "MG": "36094",
        "MK": "36097",
        "CG": "36084",
        "YV": "36111",
        "KT": "36091",
        "ND": "36098",
        "NZ": "36100",
        "ST": "36107",
        "GT": "36088",
        "KD": "36092",
        "BK": "36079",
        "BM": "36080",
        "BB": "36078",
        "SN": "36103",
        "MK": "36093",
        "SV": "36106",
        "AZ": "36077",
        "HR": "36089",
        "ZV": "36113",
        "MN": "36096",
        "CL": "36085",
        "BC": "36081",
        "AR": "36086",
        "TM": "36110",
        "CR": "36090",
        "ME": "36095",
        "NI": "36099"
    }

    parser = argparse.ArgumentParser(description="Download and merge PDFs for Talmud tractates.")
    parser.add_argument("tractate", choices=list(tractate_ids.keys()), help="Tractate to download")
    parser.add_argument("--start-page", type=int, default=1, help="Page number to start from (default: 1)")
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    main(args.tractate, tractate_ids[args.tractate], args.start_page)
