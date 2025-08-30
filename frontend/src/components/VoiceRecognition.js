import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Box, Typography, IconButton, Tooltip } from '@mui/material';
import { Mic as MicIcon, Stop as StopIcon } from '@mui/icons-material';

let SpeechRecognition;
let webkitSpeechRecognition;

if (typeof window !== 'undefined') {
  SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  webkitSpeechRecognition = window.webkitSpeechRecognition;
}

const VoiceRecognition = ({ onResult, onError }) => {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (SpeechRecognition) {
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onstart = () => {
        setIsListening(true);
        setTranscript('');
        setError('');
      };

      recognitionInstance.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscript(finalTranscript || interimTranscript);

        if (finalTranscript && onResult) {
          onResult(finalTranscript);
        }
      };

      recognitionInstance.onerror = (event) => {
        setError(event.error);
        setIsListening(false);
        if (onError) {
          onError(event.error);
        }
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }

    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, []);

  const startListening = () => {
    if (recognition && !isListening) {
      try {
        recognition.start();
      } catch (err) {
        setError('Failed to start recognition');
        if (onError) {
          onError('Failed to start recognition');
        }
      }
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  if (!SpeechRecognition) {
    return (
      <Box sx={{ textAlign: 'center', p: 2 }}>
        <Typography variant="body2" color="error">
          Speech recognition is not supported in this browser
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 100,
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        textAlign: 'center',
        bgcolor: 'background.paper',
        border: 2,
        borderColor: isListening ? 'secondary.main' : 'primary.main',
        borderRadius: 4,
        p: 2,
        minWidth: 300,
        boxShadow: 3
      }}
    >
      {isListening && (
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <MicIcon sx={{ fontSize: 48, color: 'secondary.main', mb: 1 }} />
        </motion.div>
      )}

      <Typography variant="h6" gutterBottom>
        {isListening ? 'Listening...' : 'Ready to listen'}
      </Typography>

      {transcript && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          "{transcript}"
        </Typography>
      )}

      {error && (
        <Typography variant="body2" color="error" sx={{ mb: 2 }}>
          Error: {error}
        </Typography>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
        {!isListening ? (
          <Tooltip title="Start listening">
            <IconButton
              onClick={startListening}
              color="primary"
              size="large"
              sx={{
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' }
              }}
            >
              <MicIcon />
            </IconButton>
          </Tooltip>
        ) : (
          <Tooltip title="Stop listening">
            <IconButton
              onClick={stopListening}
              color="secondary"
              size="large"
              sx={{
                bgcolor: 'secondary.main',
                color: 'white',
                '&:hover': { bgcolor: 'secondary.dark' }
              }}
            >
              <StopIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
        Speak clearly and wait for the response
      </Typography>
    </Box>
  );
};

export default VoiceRecognition;
