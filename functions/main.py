from firebase_functions import https_fn, storage_fn
from firebase_functions.options import set_global_options, MemoryOption
from firebase_admin import initialize_app
from firebase_admin import firestore
from datetime import datetime

from path_handling import get_user_id, get_file_name
from chat import run_chat
from vectorize_file import run_vectorize_file
from session_management import create_user_session, list_user_sessions, delete_user_session
from delete_file import delete_file_from_openai, delete_vector_store_from_openai


# Maximum number of containers that can be running at the same time.
set_global_options(max_instances=2)

app = initialize_app()


# Session Management Functions
@https_fn.on_call(memory=MemoryOption.MB_256)
def create_session(req: https_fn.CallableRequest) -> dict:
    """Cloud function to create a new session."""
    # Verify authentication
    if not req.auth:
        return {'success': False, 'message': 'Unauthorized', 'data': None}
    
    uid = req.auth.uid
    return create_user_session(uid)

@https_fn.on_call(memory=MemoryOption.MB_256)
def list_sessions(req: https_fn.CallableRequest) -> dict:
    """Cloud function to list user sessions."""
    # Verify authentication
    if not req.auth:
        return {'success': False, 'message': 'Unauthorized', 'data': None}
    
    uid = req.auth.uid
    return list_user_sessions(uid)

@https_fn.on_call(memory=MemoryOption.MB_256)
def delete_session(req: https_fn.CallableRequest) -> dict:
    """Cloud function to delete a session."""
    # Verify authentication
    if not req.auth:
        return {'success': False, 'message': 'Unauthorized', 'data': None}
    
    uid = req.auth.uid
    session_id = req.data.get('sessionId')
    
    if not session_id:
        return {'success': False, 'message': 'Session ID is required', 'data': None}
    
    return delete_user_session(uid, session_id)


@https_fn.on_call(memory=MemoryOption.MB_256)
def delete_document(req: https_fn.CallableRequest) -> dict:
    """Cloud function to delete a document from OpenAI storage and vector stores."""
    # Verify authentication
    if not req.auth:
        return {'success': False, 'message': 'Unauthorized', 'data': None}
    
    uid = req.auth.uid
    file_name = req.data.get('fileName')
    
    if not file_name:
        return {'success': False, 'message': 'File name is required', 'data': None}
    
    return delete_file_from_openai(uid, file_name)


@https_fn.on_call(memory=MemoryOption.GB_1)
def chat(req: https_fn.CallableRequest) -> any:
    """Process user prompt using OpenAI Agents SDK and return response"""

    # Require authenticated user
    if not req.auth or not req.auth.uid:
        return {
            'success': False,
            'message': 'Unauthenticated request',
            'data': None
        }

    uid = req.auth.uid
    prompt = req.data.get('prompt')
    session_id = req.data.get('sessionId') or 'default'
    client_message_id = req.data.get('clientMessageId')  # optional for dedupe
    if prompt is None:
        return {
            'success': False,
            'message': 'No text prompt provided',
            'data': None
        }

    return run_chat(uid, prompt, session_id, client_message_id)


@storage_fn.on_object_finalized(bucket="chat-with-it-e09f2.firebasestorage.app", memory=MemoryOption.GB_2)
def vectorize_file(event: storage_fn.CloudEvent[storage_fn.StorageObjectData]) -> str:
    """
    Cloud function triggered by file upload to /user-documents folder.
    
    Args:
        event: CloudEvent containing storage object data
        
    Returns:
        str: The name of the uploaded file
    """
    # Extract file information from the event
    file_path = event.data.name
    bucket_name = event.data.bucket
        
    # Run the vectorization pipeline
    return run_vectorize_file(file_path, bucket_name)
