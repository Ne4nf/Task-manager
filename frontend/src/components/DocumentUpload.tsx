import { useState, useRef, useEffect } from 'react';
import { Upload, File, X, AlertCircle } from 'lucide-react';
import { uploadDocument, getProjectDocuments, deleteDocument, getDocument, type DocumentUploadResponse } from '../api/client';

interface DocumentUploadProps {
  projectId: string;
  onUploadComplete?: () => void;
}

export default function DocumentUpload({ projectId, onUploadComplete }: DocumentUploadProps) {
  const [documents, setDocuments] = useState<DocumentUploadResponse[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, [projectId]);

  const loadDocuments = async () => {
    try {
      const docs = await getProjectDocuments(projectId);
      setDocuments(docs);
      
      // Auto-select first document
      if (docs.length > 0 && !selectedDoc) {
        handleDocumentClick(docs[0].id);
      }
    } catch (err: any) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleDocumentClick = async (documentId: string) => {
    try {
      const doc = await getDocument(documentId);
      setSelectedDoc(doc);
    } catch (err: any) {
      console.error('Failed to load document content:', err);
      setError('Failed to load document content');
    }
  };

  const handleFileSelect = async (file: File) => {
    // Validate file type
    const allowedTypes = ['.md', '.docx', '.pdf'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
      setError(`Invalid file type. Allowed: ${allowedTypes.join(', ')}`);
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit');
      return;
    }

    setUploading(true);
    setError('');

    try {
      await uploadDocument(projectId, file);
      await loadDocuments();
      if (onUploadComplete) {
        onUploadComplete();
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await deleteDocument(documentId);
      await loadDocuments();
    } catch (err: any) {
      console.error('Delete error:', err);
      setError(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="grid grid-cols-3 gap-6 h-full">
      {/* Left: Upload + Documents List */}
      <div className="col-span-1 space-y-4">
        {/* Upload Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-6 text-center transition cursor-pointer ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 bg-white hover:border-gray-400'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".md,.docx,.pdf"
            onChange={handleFileInput}
            className="hidden"
          />

          <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          
          {uploading ? (
            <div className="space-y-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 text-sm">Uploading...</p>
            </div>
          ) : (
            <>
              <p className="text-gray-700 font-medium text-sm mb-1">
                Upload Document
              </p>
              <p className="text-gray-500 text-xs">
                .md, .docx, .pdf (Max 10MB)
              </p>
            </>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-2 text-red-700 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Documents List */}
        {documents.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-semibold text-gray-700 text-sm">Documents ({documents.length})</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => handleDocumentClick(doc.id)}
                  className={`flex items-center justify-between border rounded-lg p-3 hover:border-blue-300 transition cursor-pointer ${
                    selectedDoc?.id === doc.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white'
                  }`}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <File className="w-4 h-4 text-blue-600 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate text-sm">
                        {doc.filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(doc.file_size)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(doc.id);
                    }}
                    className="p-1 text-gray-400 hover:text-red-600 transition"
                    title="Delete document"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {documents.length === 0 && !uploading && (
          <div className="text-center py-8 text-gray-500 text-sm">
            No documents uploaded yet
          </div>
        )}
      </div>

      {/* Right: Document Content */}
      <div className="col-span-2">
        {selectedDoc ? (
          <div className="bg-white border border-gray-200 rounded-lg p-6 h-full overflow-y-auto">
            <div className="mb-4 pb-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-800 text-lg">{selectedDoc.filename}</h3>
              <p className="text-sm text-gray-500 mt-1">
                {formatFileSize(selectedDoc.file_size)} • Uploaded {new Date(selectedDoc.uploaded_at).toLocaleString()}
              </p>
            </div>
            <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
              {selectedDoc.content || 'No content available'}
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 h-full flex items-center justify-center">
            <div className="text-center text-gray-500">
              <File className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p className="font-medium">No document selected</p>
              <p className="text-sm mt-1">Upload a document or select one from the list</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
