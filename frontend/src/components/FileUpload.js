import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  LinearProgress,
  Alert,
  Chip
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { CloudUpload as CloudUploadIcon, Description as DescriptionIcon } from '@mui/icons-material';
import { aiService } from '../services/aiService';
import toast from 'react-hot-toast';

const FileUpload = ({ open, onClose, onUpload }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    onDrop: (files) => {
      handleUpload(files);
    }
  });

  const handleUpload = async (files) => {
    if (files.length === 0) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      for (const file of files) {
        const result = await aiService.uploadFile(file, (progress) => {
          setUploadProgress(progress);
        });

        setUploadedFiles(prev => [...prev, result]);
        onUpload(result);
        toast.success(`Successfully processed ${file.name}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleClose = () => {
    if (!uploading) {
      setUploadedFiles([]);
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CloudUploadIcon />
          Upload Files for Analysis
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Supported formats: PDF, TXT, MD, DOCX (max 50MB each)
          </Typography>
        </Box>

        <Box
          {...getRootProps()}
          sx={{
            border: 2,
            borderColor: isDragActive ? 'primary.main' : 'grey.300',
            borderStyle: 'dashed',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            bgcolor: isDragActive ? 'primary.light' : 'background.default',
            transition: 'all 0.2s',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'primary.light'
            }
          }}
        >
          <input {...getInputProps()} />
          <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            or click to browse files
          </Typography>
        </Box>

        {uploading && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              Uploading and processing... {uploadProgress}%
            </Typography>
            <LinearProgress variant="determinate" value={uploadProgress} />
          </Box>
        )}

        {acceptedFiles.length > 0 && !uploading && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Files to upload:
            </Typography>
            {acceptedFiles.map((file) => (
              <Chip
                key={file.name}
                icon={<DescriptionIcon />}
                label={`${file.name} (${(file.size / 1024 / 1024).toFixed(1)} MB)`}
                variant="outlined"
                sx={{ mr: 1, mb: 1 }}
              />
            ))}
          </Box>
        )}

        {uploadedFiles.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Alert severity="success" sx={{ mb: 1 }}>
              Successfully processed {uploadedFiles.length} file(s)
            </Alert>
            {uploadedFiles.map((file, index) => (
              <Box key={index} sx={{ mb: 1, p: 2, border: 1, borderColor: 'success.main', borderRadius: 1 }}>
                <Typography variant="subtitle2">{file.filename}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {file.summary}
                </Typography>
                <Chip size="small" label={`${file.file_size} bytes`} sx={{ mt: 1 }} />
              </Box>
            ))}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          {uploadedFiles.length > 0 ? 'Done' : 'Cancel'}
        </Button>
        {acceptedFiles.length > 0 && !uploading && (
          <Button 
            variant="contained" 
            onClick={() => handleUpload(acceptedFiles)}
            disabled={uploading}
          >
            Upload & Process
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default FileUpload;
