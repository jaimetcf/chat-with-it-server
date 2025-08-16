def get_file_extension(file_name: str) -> str:
    """
    Extract file extension from file name.
    
    Args:
        file_name: Name of the file
        
    Returns:
        str: File extension in lowercase (e.g., '.pdf', '.png', '.jpg')
    """
    if '.' not in file_name:
        return ""
    
    # Get the last part after the last dot
    extension = file_name.split('.')[-1].lower()
    return f".{extension}"


def detect_file_type(file_extension: str) -> str:
    """
    Detect file type based on file extension.
    
    Args:
        file_extension: File extension (e.g., '.pdf', '.png', '.jpg')
        
    Returns:
        str: File type ('PDF', 'IMAGE', or 'UNSUPPORTED')
    """
    # PDF files
    if file_extension == '.pdf':
        return 'PDF'
    
    # Image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
    if file_extension in image_extensions:
        return 'IMAGE'
    
    # Unsupported files
    return 'UNSUPPORTED'
