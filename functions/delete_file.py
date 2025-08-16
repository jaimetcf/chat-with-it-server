#!/usr/bin/env python3
"""
Delete file from OpenAI storage and vector stores.
This module handles the cleanup of files when they are deleted from Firebase Storage.
"""
from firebase_admin import firestore
from openai import OpenAI
import os
from datetime import datetime


def delete_file_from_openai(
    user_id: str, 
    file_name: str
) -> dict:
    """
    Delete a file from OpenAI storage and vector stores.
    
    Args:
        user_id: ID of the user
        file_name: Name of the file to delete
        
    Returns:
        dict: Success/failure message
    """
    try:
        # Initialize clients
        db_client = firestore.client()
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Set deletion status immediately
        document_id = f"{user_id}_{file_name}"
        update_deletion_status(db_client, user_id, file_name, 'deleting')
        
        # Get the document processing status to find file_id and vector_store_id
        status_doc = db_client.collection('document_processing_status').document(document_id).get()
        
        if not status_doc.exists:
            return {
                'success': False,
                'message': f'No processing status found for file: {file_name}',
                'data': None
            }
        
        status_data = status_doc.to_dict()
        file_id = status_data.get('file_id')
        vector_store_id = status_data.get('vector_store_id')
        
        if not file_id:
            return {
                'success': False,
                'message': f'No OpenAI file ID found for: {file_name}',
                'data': None
            }
        
        # Delete from vector store if vector_store_id exists
        if vector_store_id:
            try:
                # Delete the file from the vector store
                openai_client.vector_stores.files.delete(
                    vector_store_id=vector_store_id,
                    file_id=file_id
                )
                print(f"Deleted file {file_id} from vector store {vector_store_id}")
            except Exception as e:
                print(f"Error deleting from vector store: {str(e)}")
                # Continue with file deletion even if vector store deletion fails
        
        # Delete the file from OpenAI storage
        try:
            openai_client.files.delete(file_id=file_id)
            print(f"Deleted file {file_id} from OpenAI storage")
        except Exception as e:
            print(f"Error deleting from OpenAI storage: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to delete file from OpenAI storage: {str(e)}',
                'data': None
            }
        
        # Delete the processing status document
        try:
            db_client.collection('document_processing_status').document(document_id).delete()
            print(f"Deleted processing status for {file_name}")
        except Exception as e:
            print(f"Error deleting processing status: {str(e)}")
            # Continue even if status deletion fails
        
        return {
            'success': True,
            'message': f'Successfully deleted {file_name} from OpenAI storage and vector stores',
            'data': {
                'file_id': file_id,
                'vector_store_id': vector_store_id
            }
        }
        
    except Exception as e:
        error_msg = f"Error deleting file from OpenAI: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'message': error_msg,
            'data': None
        }


def update_deletion_status(
    db_client, 
    user_id: str, 
    file_name: str, 
    status: str
) -> None:
    """
    Update the deletion status of a document in Firestore for real-time notifications.
    
    Args:
        db_client: Firestore client instance
        user_id: ID of the user
        file_name: Name of the file being deleted
        status: Current deletion status
    """
    try:
        # Create a unique document ID that combines user_id and file_name
        document_id = f"{user_id}_{file_name}"
        status_ref = db_client.collection('document_processing_status').document(document_id)
        
        update_data = {
            'user_id': user_id,
            'file_name': file_name,
            'status': status,
            'updated_at': datetime.now()
        }
        
        if status == 'deleting':
            update_data['started_at'] = datetime.now()
            
        status_ref.set(update_data, merge=True)
        print(f"Updated deletion status for {file_name}: {status}")
        
    except Exception as e:
        print(f"Error updating deletion status: {str(e)}")

def delete_vector_store_from_openai(
    user_id: str,
    vector_store_id: str
) -> dict:
    """
    Delete an entire vector store from OpenAI.
    
    Args:
        user_id: ID of the user
        vector_store_id: ID of the vector store to delete
        
    Returns:
        dict: Success/failure message
    """
    try:
        # Initialize clients
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Delete the entire vector store
        openai_client.vector_stores.delete(vector_store_id=vector_store_id)
        print(f"Deleted vector store {vector_store_id}")
        
        # Update Firestore to remove the vector store ID from user's list
        db_client = firestore.client()
        user_vector_stores_ref = db_client.collection('user_vector_stores').document(user_id)
        user_vector_stores_doc = user_vector_stores_ref.get()
        
        if user_vector_stores_doc.exists:
            user_data = user_vector_stores_doc.to_dict()
            vector_store_ids = user_data.get('vector_store_ids', [])
            
            if vector_store_id in vector_store_ids:
                vector_store_ids.remove(vector_store_id)
                user_vector_stores_ref.update({
                    'vector_store_ids': vector_store_ids
                })
                print(f"Removed vector store {vector_store_id} from user {user_id}")
        
        return {
            'success': True,
            'message': f'Successfully deleted vector store {vector_store_id}',
            'data': {
                'vector_store_id': vector_store_id
            }
        }
        
    except Exception as e:
        error_msg = f"Error deleting vector store from OpenAI: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'message': error_msg,
            'data': None
        }
