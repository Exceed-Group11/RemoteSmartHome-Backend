def header_decoder(header_str: str):
    """This function is used to decode the
    bearer header token.
    """
    if type(header_str) != str:
        raise ValueError(f"The header is not str (Got {type(header_str)})")
    splitted_header = header_str.split(" ")
    if len(splitted_header) != 2:
        raise ValueError(f"The passed header_str is invalud ({header_str})")
    return splitted_header[1]
