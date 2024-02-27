def extract_reference_id(text):
    JB_IDENTIFIER = "jbkey"
    if JB_IDENTIFIER not in text:
        return None
    start_index = text.find(JB_IDENTIFIER)
    if start_index == -1:
        return None  # Start magic string not found

    new_index = start_index + len(JB_IDENTIFIER)
    end_index = text.find(JB_IDENTIFIER, new_index)
    if end_index == -1:
        return None  # End magic string not found

    return text[start_index:end_index+len(JB_IDENTIFIER)]
