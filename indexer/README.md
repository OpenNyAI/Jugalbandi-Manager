## Pre processing:

The pre-processing step in indexing involves parsing the file before chunking it. The function parse_file() accepts the entire pathname of the file as a parameter and uses it to extract the extension of the file. Depending on what the file extension is, the corresponding functions for parsing the file are called. Currently, the implementation for file parsing has been provided for files of the format **pdf**, **docs**, **xslx** and **json** only.

-**DOCX Parser**:

    The parser function docx_parser() is called when the file to be parsed is of the format .docx (Microsoft word document). This function utilizes the doc2txt library to process the file. The process() function of doc2txt library is designed to extract and process text from the DOCX file and optionally save embedded images to a specified directory.

-**PDF Parser**:
    
    The parser function pdf_parser() is called when the file to be parsed is a PDF file. This function uses the Fitz python library, which is a part of PyMuPDF package, to open the PDF file specified by the pdf_file_path argument. The `fitz.open()` statement returns a Document object that provides access to the pages and content within the PDF.
    For every page in the document, the text content of that page is extracted in plain format using get_text("text"). The function, then, joins the text from all pages into one long string with each page's text separated by a newline character (\n) and returns the concatenated text as a string for further processing.

-**XLSX Parser**:

    The parser function xlsx_parser() is called when the file to be parsed is a Excel file. This function uses Pandas python package and DataFrame (a tabular data structure in pandas) for parsing. 
    `pandas.read_excel()` reads the Excel file provided (excel_file_path) into a DataFrame. By default, `pd.read_excel()` reads the first sheet of the Excel file. After reading, `df.to_string(index=False)` converts the DataFrame into a plain-text string. The result is a formatted string that represents the contents of the Excel sheet in a tabular layout, with columns and rows formatted as text.

-**JSON parser**:

    The parser function json_parser() is called when the file to be parsed is of json format. This function uses the built-in package JSON, which can be used to work with JSON data. This function first opens the file provided (json_file_path) in read only mode using `open(json_file_path, "r")`. The file is parsed using `json.load()` method which takes a file object and returns a json object. Here, `data = json.load(file)` parses the file and gives us a dictionary named data, that contains the contents of the file. `json.dumps(data, indent=4)` takes the "data" object, converts it back into a JSON-formatted string, and applies pretty-printing with an indentation level of 4 spaces.

-**Default parser**:
    
    When the file to be parsed is not of pdf, xslx, json or docx format, then the default_parser() function is called to parse the file. This function opens the file provided (file_path) in "r" mode i.e. read only mode and returns the contents of the file as a string.


## Chunking strategy and process:

Once the files are parsed, the indexer service breaks down the collected information and arranges it into neat, searchable chunks. This helps in finding the right information quickly. The indexer breaks down the knowledge fed into Jugalbandi into smaller parts and adds labels to each part, making it easy to search and relate to other information.

### Chunking Parameters

The chunking process uses the following parameters:

- `chunk_size`: Typically **4000 characters**
- `chunk_overlap`: Usually **200 characters**
- List of separators (e.g., newline, period)

These parameters ensure smooth, logical breaks in the content.

- The `chunk_size` value indicates the maximum number of characters allowed in each chunk.
- The `chunk_overlap` value indicates how much overlap of characters must be present between consecutive chunks.

### Chunking Process

The content collected from each file is chunked in such a way that:

- Every chunk has a maximum of 4000 characters.
- The first **200 characters overlap** with the last 200 characters of the previous chunk.
- No sentences are cut in between chunks.

This results in continuous and logically structured chunks for efficient searching and retrieval.


## API and Indexer Service Workflow
