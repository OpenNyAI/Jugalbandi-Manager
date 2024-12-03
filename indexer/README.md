## Pre processing:

The pre-processing step in indexing involves parsing the file before chunking it. The function parse_file() accepts the entire pathname of the file as a parameter and uses it to extract the extension of the file. Depending on what the file extension is, the corresponding functions for parsing the file are called. Currently, the implementation for file parsing has been provided for files of the format **pdf**, **docs**, **xslx** and **json** only.

- **DOCX Parser**:

    The parser function docx_parser() is called when the file to be parsed is of the format .docx (Microsoft word document). This function utilizes the doc2txt library to process the file. The process() function of doc2txt library is designed to extract and process text from the DOCX file and optionally save embedded images to a specified directory.

- **PDF Parser**:
    
    The parser function pdf_parser() is called when the file to be parsed is a PDF file. This function uses the Fitz python library, which is a part of PyMuPDF package, to open the PDF file specified by the pdf_file_path argument. The `fitz.open()` statement returns a Document object that provides access to the pages and content within the PDF.
    For every page in the document, the text content of that page is extracted in plain format using get_text("text"). The function, then, joins the text from all pages into one long string with each page's text separated by a newline character (\n) and returns the concatenated text as a string for further processing.

- **XLSX Parser**:

    The parser function xlsx_parser() is called when the file to be parsed is a Excel file. This function uses Pandas python package and DataFrame (a tabular data structure in pandas) for parsing. 
    `pandas.read_excel()` reads the Excel file provided (excel_file_path) into a DataFrame. By default, `pd.read_excel()` reads the first sheet of the Excel file. After reading, `df.to_string(index=False)` converts the DataFrame into a plain-text string. The result is a formatted string that represents the contents of the Excel sheet in a tabular layout, with columns and rows formatted as text.

- **JSON parser**:

    The parser function json_parser() is called when the file to be parsed is of json format. This function uses the built-in package JSON, which can be used to work with JSON data. This function first opens the file provided (json_file_path) in read only mode using `open(json_file_path, "r")`. The file is parsed using `json.load()` method which takes a file object and returns a json object. Here, `data = json.load(file)` parses the file and gives us a dictionary named data, that contains the contents of the file. `json.dumps(data, indent=4)` takes the "data" object, converts it back into a JSON-formatted string, and applies pretty-printing with an indentation level of 4 spaces.

- **Default parser**:
    
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

## Reference links:

### Reference links related to pre-processing and parsing of documents:

- **For HTML Parsing and Web Scraping**

    [BeautifulSoup (Python Library) Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
    BeautifulSoup is one of the most popular Python libraries for parsing HTML and XML documents. This link provides a complete guide on how to use it for web scraping.

    [Scrapy: Web Scraping Framework (Documentation)](https://docs.scrapy.org/en/latest/)
    Scrapy is a powerful and efficient framework for scraping websites and parsing their content. It offers tools for extracting data from HTML, JSON, and XML.

- **For XML Parsing**

    [Python’s XML Parsing Library - ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html)
    The ElementTree module in Python provides a simple and efficient API for parsing and creating XML documents. 

    [lxml: A Library for XML and HTML Parsing](https://lxml.de/)
    lxml is a high-performance library for XML and HTML parsing, and highly recommended for more complex and large documents.

- **For JSON Parsing**

    [JSON Parsing in Python](https://docs.python.org/3/library/json.html)
    Python JSON Library is one of the most efficient ways to parse JSON data, commonly used in API responses and modern data exchange.

    [Working with JSON in JavaScript (MDN Web Docs)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse)
    JavaScript's native JSON.parse() and JSON.stringify() methods are powerful tools for parsing and converting JSON data, ideal for bots that interact with web APIs.

 - **For PDF Parsing**

    [PyPDF2: Parsing PDF Files](https://pypdf2.readthedocs.io/en/3.x/)
    PyPDF2 is a Python library for extracting text, splitting, merging, and manipulating PDF files. It’s widely used for document processing in bots.

    [PDFMiner](https://pdfminersix.readthedocs.io/en/latest/)
    PDFMiner allows for extracting text, metadata, and other contents from PDFs. It’s more advanced than PyPDF2 and often better at handling complex PDFs.

- **CSV and Excel File Parsing**

    [Pandas Library for CSV/Excel Parsing](https://pandas.pydata.org/pandas-docs/stable/)
    Pandas is one of the best Python libraries widely used for parsing structured data in various formats.

    [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/)
    This Python library is specifically used for reading and writing Excel .xlsx files, allowing you to parse and manipulate Excel documents programmatically.

- **Parsing Markdown and Other Markup Languages**

    [Markdown Parsing in Python using Mistune](https://mistune.readthedocs.io/en/latest/)
    Mistune is a fast and flexible Markdown parser for Python, useful when the bot needs to interpret or convert Markdown content.
    
    [CommonMark: Markdown Parser](https://commonmark.org/)
    CommonMark provides a consistent specification for Markdown parsing and is implemented in many programming languages. It’s a good reference for working with Markdown documents.

- **Natural Language Processing (NLP) for Text Parsing**

    [SpaCy: NLP Library for Python](https://spacy.io/)
    SpaCy is an industrial-strength NLP library for Python. It can be used to parse and extract information from unstructured text, such as documents, articles, or social media posts.

    [Natural Language Toolkit (NLTK) Documentation](https://www.nltk.org/)
    The NLTK library provides tools for working with human language data, including tokenization, parsing, and information extraction.

### Reference links related to chunking of data:

[SpaCy: Text Chunking](https://spacy.io/usage/linguistic-features#chunking)
SpaCy provides an easy-to-use API for performing "noun phrase chunking," which breaks down sentences into useful chunks like noun phrases.

[NLTK: Chunking in Python (Natural Language Toolkit)](https://www.nltk.org/book/ch07.html)
The NLTK library offers robust support for chunking, including techniques like regular expression-based chunking.

[Chunking Text into Sentences or Paragraphs](https://realpython.com/natural-language-processing-spacy-python/#chunking-text)
This tutorial explains how to chunk text into sentences or paragraphs using the SpaCy library.

[Latent Dirichlet Allocation (LDA) for Topic Modeling](https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/)
This tutorial explains how to perform topic-based chunking using Latent Dirichlet Allocation (LDA), a popular method for dividing text into semantic chunks based on topics. It is useful for bots that need to understand themes or topics in a document.

[Topic Modeling and Chunking with Gensim](https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html)
Gensim provides an implementation of LDA for topic modeling, allowing bots to chunk documents based on semantic clusters or themes, rather than simple sentence or paragraph breaks.

[BERT for Sentence Embeddings and Chunking](https://huggingface.co/transformers/model_doc/bert.html)
BERT embeddings are useful for chunking documents based on semantic meaning. This link provides documentation on how to use BERT for advanced sentence embeddings, which can be used to group similar sentences or paragraphs into chunks.

[Text Chunking in PDFs with PyPDF2](https://pypdf2.readthedocs.io/en/3.x/)
PyPDF2 is a Python library for working with PDF documents. This guide explains how to chunk text extracted from PDFs into manageable pieces, such as paragraphs or sections.

[PDFMiner](https://pdfminersix.readthedocs.io/en/latest/)
PDFMiner can be used to extract and chunk text from PDFs. This guide shows how to extract text from PDFs and chunk it by pages, sections, or custom delimiters.
