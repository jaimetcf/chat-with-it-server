import uuid
from typing import List, Optional
from firebase_admin import firestore as admin_firestore
from firebase_functions import https_fn
from firebase_admin import auth
import asyncio


def create_user_session(uid: str) -> dict:
    """Create a new session for the user."""
    try:
        db = admin_firestore.client()
        
        # Generate a random session ID
        session_id = str(uuid.uuid4())
        
        # Create the session document
        session_ref = db.collection('sessions').document(session_id)
        session_ref.set({
            'sessionId': session_id,
            'userId': uid,
            'name': None,  # Will be set when first message is sent
            'createdAt': admin_firestore.SERVER_TIMESTAMP,
            'updatedAt': admin_firestore.SERVER_TIMESTAMP,
        })
        
        return {
            'success': True,
            'message': 'Session created successfully',
            'data': {
                'sessionId': session_id,
                'name': None
            }
        }
        
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        return {
            'success': False,
            'message': f'Error creating session: {str(e)}',
            'data': None
        }


def list_user_sessions(uid: str) -> dict:
    """List all sessions for a user, sorted by most recent first."""
    try:
        db = admin_firestore.client()
        
        # Query sessions for the user, ordered by updatedAt descending
        sessions_ref = db.collection('sessions')
        query = sessions_ref.where('userId', '==', uid).order_by('updatedAt', direction=admin_firestore.Query.DESCENDING)
        
        docs = list(query.stream())
        sessions = []
        
        for doc in docs:
            data = doc.to_dict()
            sessions.append({
                'sessionId': data.get('sessionId'),
                'name': data.get('name'),
                'createdAt': data.get('createdAt'),
                'updatedAt': data.get('updatedAt')
            })
        
        return {
            'success': True,
            'message': 'Sessions retrieved successfully',
            'data': sessions
        }
        
    except Exception as e:
        print(f"Error listing sessions: {str(e)}")
        return {
            'success': False,
            'message': f'Error listing sessions: {str(e)}',
            'data': None
        }


def delete_user_session(uid: str, session_id: str) -> dict:
    """Delete a session and all its messages."""
    try:
        db = admin_firestore.client()
        
        # Verify the session belongs to the user
        session_ref = db.collection('sessions').document(session_id)
        session_doc = session_ref.get()
        
        if not session_doc.exists:
            return {
                'success': False,
                'message': 'Session not found',
                'data': None
            }
        
        session_data = session_doc.to_dict()
        if session_data.get('userId') != uid:
            return {
                'success': False,
                'message': 'Unauthorized to delete this session',
                'data': None
            }
        
        # Delete all messages in the session
        messages_ref = session_ref.collection('messages')
        messages = list(messages_ref.stream())
        
        batch = db.batch()
        for message in messages:
            batch.delete(message.reference)
        
        # Delete the session document
        batch.delete(session_ref)
        
        # Commit the batch
        batch.commit()
        
        return {
            'success': True,
            'message': 'Session deleted successfully',
            'data': None
        }
        
    except Exception as e:
        print(f"Error deleting session: {str(e)}")
        return {
            'success': False,
            'message': f'Error deleting session: {str(e)}',
            'data': None
        }


def generate_session_name(prompt: str) -> str:
    """Generate a session name by summarizing the first user message."""
    try:
        # Lazy import to avoid deployment timeout
        from agents import Agent, Runner, ModelSettings
        
        # Create a simple agent to generate session names
        agent = Agent(
            name="Session Name Generator",
            instructions=(
                "You are a session name generator. Your task is to create a concise, "
                "descriptive title (maximum 50 characters) for a chat session based on "
                "the user's first message. The title should capture the main topic or "
                "intent of the conversation. Return only the title, nothing else."
            ),
            model="gpt-4.1",
            model_settings=ModelSettings(temperature=0.3),
        )
        
        # Run the agent to generate the session name
        result = asyncio.run(Runner.run(agent, prompt))
        session_name = result.final_output or "New Chat"
        
        # Ensure the name is not too long
        if len(session_name) > 50:
            session_name = session_name[:47] + "..."
        
        return session_name.strip()
        
    except Exception as e:
        print(f"Error generating session name: {str(e)}")
        return "New Chat"
