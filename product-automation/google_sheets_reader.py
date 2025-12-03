import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class GoogleSheetsReader:
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('sheets', 'v4', credentials=creds)
    
    def read_sheet(self, spreadsheet_id, range_name='Sheet1'):
        """Read data from Google Sheet"""
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            values = result.get('values', [])
            return values
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def parse_products(self, spreadsheet_id, range_name='Sheet1'):
        """
        Parse products from Google Sheet
        Returns a dictionary where key is row number and value is product data
        Row 1 is headers, Row 2+ are data rows
        """
        data = self.read_sheet(spreadsheet_id, range_name)
        
        if not data:
            return {}
        
        products = {}
        current_product = None
        
        # Process each row (index 0 = row 1 in Google Sheets)
        for idx, row in enumerate(data):
            # Skip header row (index 0 = row 1)
            if idx == 0:
                continue
            
            # Google Sheets row number (1-indexed)
            google_row_number = idx + 1
            
            # Check if this row has a title (first column is not empty)
            if len(row) > 0 and row[0].strip():
                # Save previous product if exists
                if current_product:
                    products[current_product['row_number']] = current_product
                
                # Start new product
                current_product = {
                    'row_number': google_row_number,
                    'title': row[0].strip(),
                    'variants': []
                }
                
                # Also check if this title row has size and price (first variant)
                if len(row) >= 3:
                    size = row[1].strip() if len(row) > 1 else ''
                    price = row[2].strip() if len(row) > 2 else ''
                    
                    if size and price:
                        try:
                            price_float = float(price.replace('$', '').replace(',', ''))
                            current_product['variants'].append({
                                'size': size,
                                'price': price_float
                            })
                        except ValueError:
                            print(f"Warning: Could not parse price '{price}' for row {google_row_number}")
            
            # Add variant if we have a current product and this row doesn't have a title
            elif current_product and len(row) >= 3:
                size = row[1].strip() if len(row) > 1 else ''
                price = row[2].strip() if len(row) > 2 else ''
                
                if size and price:
                    try:
                        price_float = float(price.replace('$', '').replace(',', ''))
                        current_product['variants'].append({
                            'size': size,
                            'price': price_float
                        })
                    except ValueError:
                        print(f"Warning: Could not parse price '{price}' for row {google_row_number}")
        
        # Don't forget the last product
        if current_product:
            products[current_product['row_number']] = current_product
        
        return products

