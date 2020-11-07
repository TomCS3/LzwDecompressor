###############################################################################################
"""
A decompressor library for the LZW algorithm, applicable to 12bit fixed width compressed files.
Main functions: Decompress, Extract
Test function: included at the end of the file
Language: Python 3.8.5
Author: Tom Howie
"""
###############################################################################################

# Imported Library 
from io import StringIO

def read_codes(archive_file: str) -> list:
    """Reads archive file in binary and produces integer codes to be decompressed

    Parameters - archive_file: The file location of the archive
    Returns - archive_codes: a list of the compressed codes to be decompressed
    """

    # Creates an empty list to append codes and opens the archive in binary read format
    archive_codes = [] 
    with open(archive_file, "rb") as archive:
        chunk = archive.read(3)
        while chunk:
            if len(chunk) == 3:
                
                # Creates a 16-bit integer, and performs bitwise operations
                # gains the 8 bits of the first byte and the 4 msb from the second byte
                code1 = 0xFF
                code1 = (code1 & chunk[0]) << 4
                code1 = code1 | chunk[1] >> 4

                # Creates a 16-bit integer, and performs bitwise operations 
                # gains the 4 lsb from the second byte and the 8 bits from the third byte
                code2 = 0xFFF
                code2 = code2 & chunk[1] << 8
                code2 = code2 | chunk[2]

                # Appends codes to a list for decompression
                archive_codes.append(code1)
                archive_codes.append(code2)

            elif len(chunk) == 2:
                # An odd number of codes indicates that the 12bit is padded to 16 bit
                # Performs bitwise operations to account for it
                code = (0xFFF & chunk[0] << 8) | chunk[1]
                archive_codes.append(code)
            
            elif len(chunk) == 1:
                raise RuntimeError("Data is Invalid")

            chunk = archive.read(3)

    return archive_codes

def decode_to_text(archive_codes: list) -> str:
    """Reads the archives codes and decodes them to text

    Parameters - archive_codes: List of integer codes to be decoded
    Returns - text: The decoded string from the archive file
    """

    # Intialises the dictionary
    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}

    # Removes the first code in the archive, converts it to a single character string
    # writes it to the StringIO buffer
    previous_code = chr(archive_codes.pop(0))
    text = StringIO()
    text.write(previous_code)

    # For each archive code, converts it to text using the dictionary
    for code in archive_codes:
        if code in dictionary:
            dict_entry = dictionary[code]
        elif code == dict_size:
            dict_entry = previous_code + previous_code[0]
        else:
            raise ValueError("Faulty archive compression code: {code}")

        # Adds the new string pattern to the dictionary and increases the dictionary size
        dictionary[dict_size] = previous_code + dict_entry[0]
        dict_size += 1
        
        # If the dictionary reaches its limit, it is reset to the intial values
        if dict_size == 4096:
            dict_size = 256

        text.write(dict_entry)
        previous_code = dict_entry

    return text.getvalue()

def decompress(archive_file :str) -> str:
    """Decompresses the archive using the read_codes and decode_to_text functions

    Parameters: archive_file: file path of the archive to be decompressed
    Returns: text: the decoded string from the archive file
    """
    return decode_to_text(read_codes(archive_file))

def extract(archive_file :str, output_file :str) -> None:
    """Extracts the archive to an output file, using the decompress function

    Parameters - archive_file: file path of the archive to be decompressed
               - output_file: file path of the data file to be created
    Returns: nothing, just the output file to be found in chosen location
    """
    with open(output_file, "w") as decompressed_file:
        decompressed_file.write(decompress(archive_file))

def test():
    """ Simple test function to validate code """

    archive_file = "LzwInputData/compressedfile1.z"
    output_file = "Lzwoutputdata/decompressedfile1.txt"

    print(decompress(archive_file))
    extract(archive_file, output_file)

test()

