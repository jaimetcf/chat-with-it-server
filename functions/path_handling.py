
def get_user_id(file_path: str) -> str:
    """
    Extract user ID from file path.
    
    Args:
        file_path: Path to the file in storage (e.g., '/user-documents/user123/document.pdf')
        
    Returns:
        str: User ID extracted from the path
    """
    # Parse the path to extract userId
    # Path format: /user-documents/{userId}/{fileName}
    path_parts = file_path.split('/')
    
    if len(path_parts) >= 3:
        return path_parts[-2]  # userId
    else:
        return "unknown"


def get_file_name(file_path: str) -> str:
    """
    Extract file name from file path.
    
    Args:
        file_path: Path to the file in storage (e.g., '/user-documents/user123/document.pdf')
        
    Returns:
        str: File name extracted from the path
    """
    # Parse the path to extract fileName
    # Path format: /user-documents/{userId}/{fileName}
    path_parts = file_path.split('/')

    if len(path_parts) >= 3:
        return path_parts[-1]  # fileName
    else:
        # Fallback if path structure is different
        return path_parts[-1] if path_parts else "unknown"
