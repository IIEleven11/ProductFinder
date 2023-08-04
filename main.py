import requests
from google.oauth2 import service_account
import gspread
import pandas as pd
from fpdf import FPDF
import os


# Constants
CREDENTIALS_FILE = 'sAccount.json'
SPREADSHEET_ID = '1oSx49obp1BTxCnIB1iXhMLqOLn091H6cAsw6A1nB0Ko'
WORKSHEET_NAME = 'Sheet1'

# Authenticate and authorize Google API client
scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)

# Google Drive interaction
drive_client = gspread.authorize(credentials)

# Google Sheets interaction
drive_spreadsheet = drive_client.open_by_key(SPREADSHEET_ID)
drive_worksheet = drive_spreadsheet.worksheet(WORKSHEET_NAME)

# Create a PDF object
pdf = FPDF()
pdf.add_page()

def generate_pdf(product_name):
    # Filter product information based on product name
    product_info = drive_worksheet.get_all_records()

    # Add the product information to the PDF
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Product: {product_name}', 0, 1, 'C')
    pdf.cell(10, 10, '', 0, 1)  # empty line

    for info in product_info:
        if info['Product Name'] == product_name:
            for key, value in info.items():
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(50, 10, f'{key}:', 0, 0)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 10, str(value), 0, 1)

            pdf.cell(10, 10, '', 0, 1)  # empty line

            # Download the photo from Google Drive
            file_id = info['Product Name']
            photo_url = f'https://drive.google.com/uc?id={file_id}'
            response = requests.get(photo_url)

            # Save the photo temporarily
            photo_path = 'temp_photo.jpg'
            with open(photo_path, 'wb') as photo_file:
                photo_file.write(response.content)

            # Add the image from Google Drive to the PDF
            pdf.image(photo_path, x=10, y=pdf.get_y() + 10, w=100, h=100, type='JPEG')
            
            # Delete the temporary photo
            os.remove(photo_path)
            break

def main():
    product_name = input('Enter the product name: ')

    generate_pdf(product_name)
    pdf_file = f'{product_name}_summary.pdf'
    pdf.output(pdf_file)

    print(f'PDF generated: {pdf_file}')

if __name__ == '__main__':
    main()