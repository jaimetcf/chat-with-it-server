# Chat with It - Serverless Backend

This project contains the serverless backend for the [Chat with It UI](https://github.com/jaimetcf/chat-with-it-ui/). It provides a scalable, event-driven architecture for document processing, AI chat functionality, and session management using Google Cloud Functions.

## Overview

The backend is built as a collection of Google Cloud Functions that handle:
- **Document Processing**: Automatic vectorization and indexing of uploaded documents
- **AI Chat**: Intelligent conversation with context from user documents
- **Session Management**: Chat session creation, listing, and deletion
- **File Management**: Secure file deletion from OpenAI storage and vector stores

## Technologies Used

### Core Infrastructure
- **Google Cloud Functions**: Serverless compute platform for event-driven processing
- **Google Cloud Firestore**: NoSQL document database for session and user data
- **Google Cloud Storage**: Object storage for document uploads and management

### AI and Machine Learning
- **OpenAI Agents SDK**: Framework for building intelligent AI agents
- **OpenAI's Vector Storage**: Semantic search and document indexing
- **OpenAI's FileSearch Tool**: Document search and retrieval capabilities
- **Large Language Models (LLMs)**: GPT-4.1 for natural language processing

### Development and Deployment
- **Firebase Functions**: Python runtime for cloud function development
- **Firebase Admin SDK**: Server-side Firebase integration
- **Python 3.13**: Runtime environment for cloud functions

## Cloud Functions

The following cloud functions are defined in `main.py`:

### Session Management Functions

#### `create_session`
- **Type**: Callable HTTP function
- **Purpose**: Creates a new chat session for an authenticated user
- **Authentication**: Required (Firebase Auth)
- **Returns**: Session ID and metadata

#### `list_sessions`
- **Type**: Callable HTTP function
- **Purpose**: Retrieves all chat sessions for an authenticated user
- **Authentication**: Required (Firebase Auth)
- **Returns**: List of sessions sorted by most recent activity

#### `delete_session`
- **Type**: Callable HTTP function
- **Purpose**: Deletes a specific chat session and all associated messages
- **Authentication**: Required (Firebase Auth)
- **Parameters**: `sessionId` (required)
- **Returns**: Success/failure status

### Chat Function

#### `chat`
- **Type**: Callable HTTP function
- **Purpose**: Processes user prompts using OpenAI Agents SDK with document context
- **Authentication**: Required (Firebase Auth)
- **Parameters**: 
  - `prompt` (required): User's message
  - `sessionId` (optional): Chat session ID (defaults to 'default')
  - `clientMessageId` (optional): For deduplication
- **Returns**: AI assistant response with session metadata

### Document Management Functions

#### `delete_document`
- **Type**: Callable HTTP function
- **Purpose**: Deletes a document from OpenAI storage and vector stores
- **Authentication**: Required (Firebase Auth)
- **Parameters**: `fileName` (required)
- **Returns**: Deletion status and metadata

#### `vectorize_file`
- **Type**: Storage trigger function
- **Purpose**: Automatically processes uploaded documents for AI consumption
- **Trigger**: File upload to Firebase Storage bucket
- **Returns**: Processing status message

## Data Flow

### Document Upload and Processing Flow

1. **File Upload Trigger**
   - User uploads document to Firebase Storage
   - Triggers `vectorize_file` function automatically

2. **File Processing Pipeline**
   ```
   File Upload → vectorize_file() → File Type Detection → OpenAI Upload → Vector Store Creation → Indexing → Status Update
   ```

3. **Processing Steps**:
   - **File Type Detection**: Validates supported file formats
   - **Status Tracking**: Updates Firestore with processing progress
   - **OpenAI Upload**: Uploads file to OpenAI storage
   - **Vector Store Management**: Creates or retrieves user's vector store
   - **Indexing**: Adds file to vector store for semantic search
   - **Completion**: Updates final status in Firestore

### Chat Processing Flow

1. **User Message**
   - Authenticated user sends message via `chat` function
   - Function validates authentication and input

2. **Context Retrieval**
   - Retrieves user's vector store IDs from Firestore
   - Prepares FileSearchTool with user's document context

3. **AI Agent Processing**
   ```
   User Message → OpenAI Agent → FileSearchTool → Document Context → LLM Response → Session Storage
   ```

4. **Response Generation**:
   - **Agent Creation**: Configures AI agent with FileSearchTool
   - **Document Search**: Searches user's vector stores for relevant information
   - **Response Generation**: LLM generates response using document context
   - **Session Management**: Stores conversation in Firestore
   - **Session Naming**: Generates session name for first message

### Session Management Flow

1. **Session Creation**
   - Generates unique session ID
   - Creates Firestore document with user metadata
   - Returns session information to client

2. **Session Listing**
   - Queries Firestore for user's sessions
   - Orders by most recent activity
   - Returns session metadata

3. **Session Deletion**
   - Validates session ownership
   - Deletes session document and all messages
   - Cleans up associated data

### Document Deletion Flow

1. **Deletion Request**
   - User requests document deletion via `delete_document`
   - Function validates authentication and file ownership

2. **Cleanup Process**
   ```
   Delete Request → Status Update → Vector Store Cleanup → OpenAI Storage Cleanup → Firestore Cleanup
   ```

3. **Cleanup Steps**:
   - **Status Update**: Sets deletion status in Firestore
   - **Vector Store Cleanup**: Removes file from OpenAI vector store
   - **Storage Cleanup**: Deletes file from OpenAI storage
   - **Metadata Cleanup**: Removes processing status from Firestore

## Deployment Instructions

### Prerequisites

1. **Google Cloud Project**: Create or use existing Google Cloud project
2. **Firebase Project**: Set up Firebase project in the same Google Cloud project
3. **Billing**: Enable billing for Google Cloud project
4. **APIs**: Enable required APIs:
   - Cloud Functions API
   - Cloud Firestore API
   - Cloud Storage API
   - Firebase API

### Environment Setup

1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase**:
   ```bash
   firebase login
   ```

3. **Install Python Dependencies**:
   ```bash
   cd functions
   pip install -r requirements.txt
   ```

### Configuration

1. **Firebase Configuration**:
   - Update `.firebaserc` with your project ID
   - Configure `firebase.json` for your deployment settings

2. **Environment Variables**:
   Set the following environment variables in Firebase Functions:
   ```bash
   firebase functions:config:set openai.api_key="your_openai_api_key"
   ```

3. **Firestore Rules**:
   - Review and update `firestore.rules` for security
   - Deploy rules: `firebase deploy --only firestore:rules`

4. **Storage Rules**:
   - Review and update `storage.rules` for file access control
   - Deploy rules: `firebase deploy --only storage`

### Deployment Commands

1. **Deploy All Functions**:
   ```bash
   firebase deploy --only functions
   ```

2. **Deploy Specific Function**:
   ```bash
   firebase deploy --only functions:functionName
   ```

3. **Deploy Everything**:
   ```bash
   firebase deploy
   ```

### Post-Deployment

1. **Verify Functions**:
   - Check Firebase Console > Functions for deployed functions
   - Verify function URLs and triggers

2. **Test Integration**:
   - Test document uploads trigger vectorization
   - Test chat functionality with uploaded documents
   - Verify session management operations

3. **Monitor Logs**:
   ```bash
   firebase functions:log
   ```

### Local Development

1. **Start Emulators**:
   ```bash
   firebase emulators:start
   ```

2. **Test Functions Locally**:
   - Functions run on `http://localhost:5001`
   - Storage emulator on port `9199`
   - Firestore emulator on default port

3. **Debug Functions**:
   - Use Firebase CLI debug mode
   - Check emulator logs for errors

### Security Considerations

1. **Authentication**: All functions require Firebase authentication
2. **Authorization**: Functions validate user ownership of resources
3. **Input Validation**: All inputs are validated before processing
4. **Error Handling**: Comprehensive error handling and logging
5. **Rate Limiting**: Configure appropriate rate limits in Firebase

### Monitoring and Maintenance

1. **Function Monitoring**:
   - Use Firebase Console for function metrics
   - Monitor execution times and error rates
   - Set up alerts for function failures

2. **Cost Optimization**:
   - Monitor function execution costs
   - Optimize function timeout settings
   - Review and adjust memory allocation

3. **Regular Updates**:
   - Keep dependencies updated
   - Monitor for security vulnerabilities
   - Update Firebase CLI and SDKs regularly

## Project Structure

```
server/
├── functions/                 # Cloud Functions source code
│   ├── main.py              # Function definitions and routing
│   ├── chat.py              # Chat processing logic
│   ├── vectorize_file.py    # Document processing pipeline
│   ├── session_management.py # Session CRUD operations
│   ├── delete_file.py       # File deletion logic
│   ├── firestore_session.py # Firestore session management
│   ├── path_handling.py     # File path utilities
│   ├── file_handling.py     # File type detection
│   ├── image_to_description.py # Image processing
│   ├── requirements.txt     # Python dependencies
│   └── venv/               # Virtual environment (local)
├── firebase.json           # Firebase project configuration
├── .firebaserc            # Firebase project selection
├── firestore.rules        # Firestore security rules
├── firestore.indexes.json # Firestore indexes
├── storage.rules          # Storage security rules
└── db-model.py           # Database model definitions
```

## Integration with Frontend

The backend integrates with the [Chat with It UI](https://github.com/jaimetcf/chat-with-it-ui/) through:

1. **Firebase Authentication**: Shared user authentication
2. **Firestore Database**: Shared session and user data
3. **Cloud Storage**: Document upload and management
4. **Cloud Functions**: API endpoints for chat and document operations

The frontend calls these functions using the Firebase Functions SDK and handles the user interface, while the backend processes the business logic and AI interactions.
