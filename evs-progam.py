# the Extract-validate-sanitize (EVS) program.
# This program extracts data from various sources, validates it against predefined rules,
# and sanitizes it to ensure it is safe for further processing.

# phase 1: Input Ingestion & Pr-Scrubbing
import re
def ingest_data(source):
    # Simulate data ingestion from a source
    raw_data = source.read()
    return raw_data
def pre_scrub(data):
    # Basic pre-scrubbing to remove unwanted characters
    safe_data = data.replace('\x00', '')  # Remove null bytes
    if len(safe_data) > 5000:
        raise ValueError("Input data exceeds maximum allowed size.")
    return safe_data
# phase 2: Data Extraction
def extract_data(data):
    # Extract relevant information (e.g., emails, phone numbers)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', data)
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', data)
    urls = re.findall(r'\bhttps?://[^\s]+\b', data)
    credit_cards = re.findall(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', data)
    currency = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', data)
    return {'emails': emails, 'phones': phones, 'urls': urls, 'credit_cards': credit_cards, 'currency': currency}
# phase 3: Defensive Validation & Trnasformation
def validate_data(extracted):
    # Validate extracted data against predefined rules
    validated = {}
    validated['emails'] = [email for email in extracted['emails'] if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email)]
    validated['phones'] = [phone for phone in extracted['phones'] if re.match(r'^\d{3}[-.]?\d{3}[-.]?\d{4}$', phone)]
    validated['urls'] = [url for url in extracted['urls'] if re.match(r'^https?://[^\s]+$', url)]
    validated['credit_cards'] = [cc for cc in extracted['credit_cards'] if re.match(r'^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$', cc)]
    validated['currency'] = [cur for cur in extracted['currency'] if re.match(r'^\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?$', cur)]
    return validated

# phase 4: Data Sanitization & Output into a JSON or a Dictionary
def sanitize_data(validated):
    sanitized = validated.copy()
    # Sanitize data to ensure safety (e.g., mask credit card numbers)
    masked_cards = []
    for cc in validated['credit_cards']:
        digits_only = re.sub(r'[- ]', '', cc)
        masked_cards.append('**** **** **** ' + digits_only[-4:])
    sanitized['credit_cards'] = masked_cards
    return sanitized
    # Metadata Generation
def generate_metadata(sanitized):
    metadata = {
        'total_emails': len(sanitized['emails']),
        'total_phones': len(sanitized['phones']),
        'total_urls': len(sanitized['urls']),
        'total_credit_cards': len(sanitized['credit_cards']),
        'total_currency': len(sanitized['currency']),
    }
    return metadata 
# Main EVS Function
def evs_process(source):
    raw_data = ingest_data(source)
    scrubbed_data = pre_scrub(raw_data)
    extracted = extract_data(scrubbed_data)
    validated = validate_data(extracted)
    sanitized = sanitize_data(validated)
    metadata = generate_metadata(sanitized)
    return {'sanitized_data': sanitized, 'metadata': metadata}


# Main function to use agianst a file source
import json

if __name__ == "__main__":
    try:
        # 1. Open the sample input file
        with open('sample_input.txt', 'r') as file_source:
            # 2. Process the file through the EVS pipeline
            result = evs_process(file_source)
            print(json.dumps(result, indent=4))
            final_output = evs_process(file_source)
            # 3. Print the final sanitized output and metadata strore in an external file
            print("---DATA EXTRACTION & SANITIZATION SUMMARY---")
            print(json.dumps(final_output, indent=4))
            with open('evs_output.json', 'w') as output_file:
                json.dump(result, output_file, indent=4)
            print("---DATA EXTRACTION & SANITIZATION COMPLETE---")
            print("Output written to evs_output.json")
    except FileNotFoundError:
        print("Error: The input file was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        