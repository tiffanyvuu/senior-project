import csv
import json
from datetime import datetime
import openai
from pathlib import Path

def load_api_key():
    """
    Load the API key from the llm/key.json file
    
    Returns:
        tuple: (api_key, base_url) from the JSON file
    
    Raises:
        FileNotFoundError: If the key.json file doesn't exist
        KeyError: If the expected keys aren't in the JSON file
    """
    print("\n" + "="*60)
    print("STEP 1: LOADING API CREDENTIALS")
    print("="*60)
    
    # Get the path to the llm/key.json file relative to the script location
    key_file_path = Path(__file__).parent / 'llm' / 'key.json'
    print(f"→ Looking for credentials at: {key_file_path}")
    
    # Check if file exists
    if not key_file_path.exists():
        print(f"✗ ERROR: File not found!")
        raise FileNotFoundError(f"Could not find {key_file_path}")
    
    print(f"✓ File found!")
    
    # Open and parse the JSON file
    print(f"→ Reading JSON file...")
    with open(key_file_path, 'r') as f:
        credentials = json.load(f)
    
    print(f"✓ JSON parsed successfully")
    
    # Extract the API key and base URL
    print(f"→ Extracting credentials...")
    api_key = credentials['OPENAI_API_KEY']
    base_url = credentials['base_url']
    
    # Show redacted API key for verification
    api_key_preview = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"✓ API Key loaded: {api_key_preview}")
    print(f"✓ Base URL: {base_url}")
    
    return api_key, base_url


def initialize_client(api_key, base_url):
    """
    Initialize the OpenAI client with UF Navigator credentials
    
    Args:
        api_key: API key for authentication
        base_url: The base URL for the API
    
    Returns:
        openai.OpenAI: Initialized OpenAI client
    """
    print("\n" + "="*60)
    print("STEP 2: INITIALIZING OPENAI CLIENT")
    print("="*60)
    
    print(f"→ Creating OpenAI client...")
    print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"   Base URL: {base_url}")
    
    # Create the OpenAI client with custom base URL
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    print(f"✓ Client initialized successfully!")
    
    return client


def call_llm(client, user_prompt, system_prompt, model, row_number):
    """
    Make an API call to the UF Navigator LLM using the OpenAI client
    
    Args:
        client: The initialized OpenAI client
        user_prompt: The user's input/question to send to the LLM
        system_prompt: The system-level instruction for the LLM
        model: The model name to use
        row_number: Current row number for logging
    
    Returns:
        str: The LLM response text, or an error message if the call fails
    """
    print(f"   → Preparing API call...")
    print(f"   → Model: {model}")
    print(f"   → Temperature: 0.7")
    
    try:
        # Make the API call using the OpenAI client
        print(f"   → Sending request to LLM...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},  # System instructions
                {"role": "user", "content": user_prompt}       # User's actual prompt
            ],
            temperature=0.7  # Controls randomness (0.7 is moderately creative)
        )
        
        print(f"   → Response received!")
        
        # Extract the text content from the LLM's response
        content = response.choices[0].message.content
        print(f"   ✓ Response extracted ({len(content)} characters)")
        
        return content
    
    except openai.APIError as e:
        # Handle API errors (e.g., network issues, API down)
        error_msg = f"OpenAI API Error: {str(e)}"
        print(f"   ✗ API ERROR: {error_msg}")
        return error_msg
    
    except openai.AuthenticationError as e:
        # Handle authentication errors
        error_msg = f"Authentication Error: {str(e)}"
        print(f"   ✗ AUTH ERROR: {error_msg}")
        return error_msg
    
    except openai.RateLimitError as e:
        # Handle rate limit errors
        error_msg = f"Rate Limit Error: {str(e)}"
        print(f"   ✗ RATE LIMIT ERROR: {error_msg}")
        return error_msg
    
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Unexpected Error: {str(e)}"
        print(f"   ✗ UNEXPECTED ERROR: {error_msg}")
        return error_msg


def process_csv():
    """
    Read prompts from the 'merge' column in the CSV file, 
    send each to the LLM, and write responses to a new 'output' column
    in a timestamped output file
    """
    print("\n" + "#"*60)
    print("# UF NAVIGATOR LLM CSV PROCESSOR")
    print("#"*60)
    
    # Define the system prompt that will be used for all rows
    #SYSTEM_PROMPT = ("Label the input/question here as appropriate only if the following two conditions are met (1) It is relevant to "
    #                 "the program goal (or any kind of computer programming) and generally appropriate information"
     #                "for a middle schooler to ask (in terms of not being too explicit or mature) "
      #               "If it is appropriate and not relevant, label it as offtopic. If it is "
       #              "inappropriate, label it as such and let me know only the explicit label."
        #             "The output should only explicitly be the labels 'appropiate', 'offtopic',"
         #            "or 'inappropriate' in all lowercase in square brackets, then an hyphen"
          #           "briefly giving the justification, use an excerpt if needed.")

    SYSTEM_PROMPT = ("Label the given input or question using exactly one of the following labels: "
                     "[appropriate]: The content is relevant to computer science or computing or robotics or a user interface or a"
                     "pedagogical agent or a programming tool or a reasonable 'how to' and would be considered suitable for"
                     " a middle school student under a reasonable school district and IRB approved standard. Do"
                     "[offtopic]: The content is appropriate for a middle school student but not related to"
                     "computer programming or computer science or anything listed under [appropriate]."
                     "[inappropriate]: The content is not suitable for a middle school student under a"
                     "framework that lists explicit content in a school context, regardless of topic relevance."
                     "Always label the input."
                     "Always include a brief justification after a hyphen. Use a short excerpt only if helpful.")         
    
    # Define the model to use
    MODEL = "gpt-4.1-nano"
    
    # Get the user's home directory in a cross-platform way
    home_dir = Path.home()
    
    print(f"\n→ Home directory detected: {home_dir}")
    
    # Construct the full path to the input CSV file
    input_file = home_dir / 'Downloads' / 'llm test prompts_clean.csv'
    
    # Create a timestamp in [hh:mm:ss] format for the output filename
    timestamp = datetime.now().strftime("%H-%M-%S")
    
    # Construct the output filename with the timestamp
    output_file = home_dir / 'Downloads' / f'llm test prompts_clean_output_{timestamp}.csv'
    
    # Load the API credentials from the JSON file
    try:
        api_key, base_url = load_api_key()
    except Exception as e:
        print(f"\n✗ FATAL ERROR: Could not load API credentials: {e}")
        print("Exiting...")
        return
    
    # Initialize the OpenAI client
    try:
        client = initialize_client(api_key, base_url)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: Could not initialize OpenAI client: {e}")
        print("Exiting...")
        return
    
    print("\n" + "="*60)
    print("STEP 3: LOCATING INPUT FILE")
    print("="*60)
    print(f"→ Looking for: {input_file}")
    
    # Check if the input file exists
    if not input_file.exists():
        print(f"✗ ERROR: Input file not found!")
        print(f"   Expected location: {input_file}")
        print("Exiting...")
        return
    
    print(f"✓ Input file found!")
    
    # Get file size for info
    file_size = input_file.stat().st_size
    print(f"→ File size: {file_size:,} bytes")
    
    print("\n" + "="*60)
    print("STEP 4: READING CSV STRUCTURE")
    print("="*60)
    
    # List to store all rows (header + data)
    rows = []
    
    # Counter to track which row we're processing
    row_count = 0
    skipped_count = 0
    error_count = 0
    success_count = 0
    
    # Open and read the input CSV file
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # DictReader allows us to access columns by name
        
        # Get the original column names
        fieldnames = reader.fieldnames
        
        print(f"→ Found {len(fieldnames)} columns:")
        for i, col in enumerate(fieldnames, 1):
            marker = "★" if col == "merge" else " "
            print(f"   {marker} {i}. {col}")
        
        # Check if 'merge' column exists
        if 'merge' not in fieldnames:
            print(f"\n✗ ERROR: Required column 'merge' not found!")
            print(f"   Available columns: {', '.join(fieldnames)}")
            print("Exiting...")
            return
        
        print(f"\n✓ Required 'merge' column found!")
        
        # Add 'output' as a new column name
        output_fieldnames = list(fieldnames) + ['output']
        
        # Store the header row
        rows.append(output_fieldnames)
        
        print(f"→ Will add new column: 'output'")
        
        print("\n" + "="*60)
        print("STEP 5: PROCESSING ROWS")
        print("="*60)
        print(f"→ Output will be saved to: {output_file.name}")
        print(f"→ Model: {MODEL}")
        print(f"→ System prompt: {SYSTEM_PROMPT[:100]}...")
        print("\n" + "-"*60)
        
        # Process each row in the CSV
        for row in reader:
            row_count += 1
            
            print(f"\n[Row {row_count}]")
            
            # Get the prompt from the 'merge' column
            user_prompt = row.get('merge', '').strip()
            
            # Skip empty rows (where merge column is empty)
            if not user_prompt:
                print(f"   ⊘ Skipping - Empty prompt")
                skipped_count += 1
                # Still add the row but with empty output
                row_values = [row[col] for col in fieldnames] + ['']
                rows.append(row_values)
                continue
            
            # Display a preview of what we're processing
            prompt_length = len(user_prompt)
            preview = user_prompt[:60] + "..." if len(user_prompt) > 60 else user_prompt
            print(f"   → User Prompt ({prompt_length} chars): \"{preview}\"")
            
            # Call the LLM with the user prompt and system prompt
            response = call_llm(client, user_prompt, SYSTEM_PROMPT, MODEL, row_count)
            
            # Check if response is an error
            if "Error:" in response:
                error_count += 1
                print(f"   ⚠ Row {row_count} completed with ERROR")
            else:
                success_count += 1
                # Display the response
                response_preview = response[:80] + "..." if len(response) > 80 else response
                print(f"   → LLM Output: \"{response_preview}\"")
                print(f"   ✓ Row {row_count} completed successfully")
            
            # Create the output row by appending the response to the original row data
            row_values = [row[col] for col in fieldnames] + [response]
            rows.append(row_values)
    
    print("\n" + "="*60)
    print("STEP 6: WRITING OUTPUT FILE")
    print("="*60)
    print(f"→ Writing {len(rows)} rows to output file...")
    
    # Write all rows to the output CSV file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"✓ File written successfully!")
    
    # Get output file size
    output_size = output_file.stat().st_size
    print(f"→ Output file size: {output_size:,} bytes")
    
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Total Rows Processed:  {row_count}")
    print(f"  ✓ Successful:        {success_count}")
    print(f"  ⚠ Errors:            {error_count}")
    print(f"  ⊘ Skipped (empty):   {skipped_count}")
    print(f"\nOutput saved to:")
    print(f"  {output_file}")
    print("\n" + "="*60)
    print("DONE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Entry point of the script
    try:
        process_csv()
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user (Ctrl+C)")
        print("Exiting...")
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("Exiting...")
