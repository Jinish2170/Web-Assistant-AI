import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  TextField,
  IconButton,
  Box,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Chip,
  Fab,
  Tooltip,
  LinearProgress,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Badge
} from '@mui/material';
import {
  Send as SendIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  VolumeUp as VolumeUpIcon,
  Upload as UploadIcon,
  Web as WebIcon,
  Calculate as CalculateIcon,
  Psychology as PsychologyIcon,
  SmartToy as SmartToyIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';

import { useChatStore } from '../store/chatStore';
import { aiService } from '../services/aiService';
import { voiceService } from '../services/voiceService';
import VoiceRecognition from './VoiceRecognition';
import FileUpload from './FileUpload';
import WebSearch from './WebSearch';

const ChatInterface = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [showWebSearch, setShowWebSearch] = useState(false);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const { messages, addMessage, sessionId } = useChatStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText = message, messageType = 'text') => {
    if (!messageText.trim() && messageType === 'text') return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: messageText,
      messageType: messageType,
      timestamp: new Date()
    };

    addMessage(userMessage);
    setMessage('');
    setIsLoading(true);

    try {
      const response = await aiService.sendMessage({
        message: messageText,
        message_type: messageType,
        session_id: sessionId,
        context: { timestamp: new Date().toISOString() }
      });

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response,
        messageType: response.response_type || 'text',
        metadata: response.metadata,
        suggestions: response.suggestions,
        timestamp: new Date()
      };

      addMessage(aiMessage);

      // Speak the response if voice is enabled
      if (messageType === 'voice') {
        voiceService.speak(response.response);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        messageType: 'text',
        timestamp: new Date()
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceToggle = () => {
    setIsListening(!isListening);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setMessage(suggestion);
    inputRef.current?.focus();
  };

  const handleQuickAction = async (action) => {
    switch (action) {
      case 'calculate':
        setMessage('Help me with a calculation: ');
        inputRef.current?.focus();
        break;
      case 'search':
        setShowWebSearch(true);
        break;
      case 'upload':
        setShowUpload(true);
        break;
      case 'voice':
        handleVoiceToggle();
        break;
      default:
        break;
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    noClick: true,
    onDrop: (files) => {
      if (files.length > 0) {
        setShowUpload(true);
      }
    }
  });

  return (
    <Container maxWidth="lg" sx={{ height: '100vh', py: 2 }}>
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* Header */}
        <Grid item xs={12}>
          <AppBar position="static" elevation={1} sx={{ borderRadius: 2 }}>
            <Toolbar>
              <SmartToyIcon sx={{ mr: 2 }} />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                DariusAI - Advanced Web Assistant
              </Typography>
              <Badge badgeContent={messages.length} color="secondary">
                <PsychologyIcon />
              </Badge>
            </Toolbar>
          </AppBar>
        </Grid>

        {/* Chat Area */}
        <Grid item xs={12} md={8}>
          <Paper
            elevation={3}
            sx={{
              height: 'calc(100vh - 200px)',
              display: 'flex',
              flexDirection: 'column',
              position: 'relative'
            }}
            {...getRootProps()}
          >
            <input {...getInputProps()} />
            
            {isDragActive && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: 'rgba(25, 118, 210, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 10,
                  border: '2px dashed #1976d2',
                  borderRadius: 1
                }}
              >
                <Typography variant="h5" color="primary">
                  Drop files here to upload and analyze
                </Typography>
              </Box>
            )}

            {/* Messages */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
              {messages.length === 0 ? (
                <Box sx={{ textAlign: 'center', mt: 4 }}>
                  <SmartToyIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h5" gutterBottom>
                    Welcome to DariusAI
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Your advanced AI assistant is ready to help! Try asking questions, uploading files, or searching the web.
                  </Typography>
                </Box>
              ) : (
                <List>
                  <AnimatePresence>
                    {messages.map((msg) => (
                      <motion.div
                        key={msg.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                      >
                        <ListItem
                          alignItems="flex-start"
                          sx={{
                            flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                            mb: 1
                          }}
                        >
                          <Avatar
                            sx={{
                              bgcolor: msg.role === 'user' ? 'primary.main' : 'secondary.main',
                              mx: 1
                            }}
                          >
                            {msg.role === 'user' ? 'U' : 'AI'}
                          </Avatar>
                          
                          <Paper
                            elevation={1}
                            sx={{
                              p: 2,
                              maxWidth: '70%',
                              backgroundColor: msg.role === 'user' ? 'primary.light' : 'grey.100'
                            }}
                          >
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                            
                            {msg.suggestions && msg.suggestions.length > 0 && (
                              <Box sx={{ mt: 1 }}>
                                {msg.suggestions.map((suggestion, idx) => (
                                  <Chip
                                    key={idx}
                                    label={suggestion}
                                    size="small"
                                    onClick={() => handleSuggestionClick(suggestion)}
                                    sx={{ mr: 1, mb: 1 }}
                                    color="primary"
                                    variant="outlined"
                                  />
                                ))}
                              </Box>
                            )}
                            
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                              {new Date(msg.timestamp).toLocaleTimeString()}
                            </Typography>
                          </Paper>
                        </ListItem>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </List>
              )}
              
              {isLoading && (
                <Box sx={{ width: '100%', mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    DariusAI is thinking...
                  </Typography>
                </Box>
              )}
              
              <div ref={messagesEndRef} />
            </Box>

            {/* Input Area */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TextField
                  ref={inputRef}
                  fullWidth
                  multiline
                  maxRows={3}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything..."
                  variant="outlined"
                  disabled={isLoading}
                />
                
                <Tooltip title="Voice Input">
                  <IconButton
                    color={isListening ? "secondary" : "default"}
                    onClick={handleVoiceToggle}
                    disabled={isLoading}
                  >
                    {isListening ? <MicIcon /> : <MicOffIcon />}
                  </IconButton>
                </Tooltip>
                
                <Tooltip title="Send Message">
                  <IconButton
                    color="primary"
                    onClick={() => handleSendMessage()}
                    disabled={isLoading || !message.trim()}
                  >
                    <SendIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: 'calc(100vh - 200px)' }}>
            {/* Quick Actions */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  <Chip
                    icon={<CalculateIcon />}
                    label="Calculator"
                    onClick={() => handleQuickAction('calculate')}
                    clickable
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<WebIcon />}
                    label="Web Search"
                    onClick={() => handleQuickAction('search')}
                    clickable
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<UploadIcon />}
                    label="Upload File"
                    onClick={() => handleQuickAction('upload')}
                    clickable
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<VolumeUpIcon />}
                    label="Voice Mode"
                    onClick={() => handleQuickAction('voice')}
                    clickable
                    color={isListening ? "secondary" : "primary"}
                    variant={isListening ? "filled" : "outlined"}
                  />
                </Box>
              </CardContent>
            </Card>

            {/* Status */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Status
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Session: {sessionId.slice(0, 8)}...
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Messages: {messages.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Voice: {isListening ? 'Listening' : 'Ready'}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        </Grid>
      </Grid>

      {/* Voice Recognition Component */}
      {isListening && (
        <VoiceRecognition
          onResult={(text) => {
            handleSendMessage(text, 'voice');
            setIsListening(false);
          }}
          onError={() => {
            setIsListening(false);
            toast.error('Voice recognition failed');
          }}
        />
      )}

      {/* File Upload Dialog */}
      <FileUpload
        open={showUpload}
        onClose={() => setShowUpload(false)}
        onUpload={(result) => {
          toast.success(`File uploaded: ${result.filename}`);
          handleSendMessage(`I've uploaded and processed "${result.filename}". What would you like to know about it?`);
        }}
      />

      {/* Web Search Dialog */}
      <WebSearch
        open={showWebSearch}
        onClose={() => setShowWebSearch(false)}
        onSearch={(query, results) => {
          handleSendMessage(`I searched for "${query}" and found ${results.length} relevant results. Here's what I found...`);
        }}
      />
    </Container>
  );
};

export default ChatInterface;
