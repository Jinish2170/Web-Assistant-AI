import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Card,
  CardContent,
  Link,
  CircularProgress,
  Chip,
  Divider
} from '@mui/material';
import { Search as SearchIcon, Language as LanguageIcon } from '@mui/icons-material';
import { aiService } from '../services/aiService';
import toast from 'react-hot-toast';

const WebSearch = ({ open, onClose, onSearch }) => {
  const [query, setQuery] = useState('');
  const [numResults, setNumResults] = useState(3);
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setSearching(true);
    try {
      const searchResults = await aiService.searchWeb(query, numResults);
      setResults(searchResults.results || []);
      onSearch(query, searchResults.results || []);
      toast.success(`Found ${searchResults.total_found || 0} results`);
    } catch (error) {
      console.error('Search error:', error);
      toast.error(`Search failed: ${error.message}`);
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleClose = () => {
    if (!searching) {
      setQuery('');
      setResults([]);
      onClose();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !searching) {
      handleSearch();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SearchIcon />
          Web Search & Analysis
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="Search Query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your search query..."
            disabled={searching}
            variant="outlined"
            sx={{ mb: 2 }}
          />

          <TextField
            type="number"
            label="Number of Results"
            value={numResults}
            onChange={(e) => setNumResults(Math.max(1, Math.min(10, parseInt(e.target.value) || 3)))}
            disabled={searching}
            size="small"
            sx={{ width: 150 }}
            inputProps={{ min: 1, max: 10 }}
          />
        </Box>

        {searching && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <CircularProgress size={24} />
            <Typography>Searching and analyzing results...</Typography>
          </Box>
        )}

        {results.length > 0 && (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <LanguageIcon />
              Search Results ({results.length})
            </Typography>

            {results.map((result, index) => (
              <Card key={index} sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'start', mb: 1 }}>
                    <Typography variant="h6" component="div" sx={{ flex: 1 }}>
                      {result.search_title || result.title || 'Untitled'}
                    </Typography>
                    <Chip
                      size="small"
                      label={`${result.word_count || 0} words`}
                      color="primary"
                      variant="outlined"
                    />
                  </Box>

                  <Link
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    variant="body2"
                    sx={{ display: 'block', mb: 1, wordBreak: 'break-all' }}
                  >
                    {result.url}
                  </Link>

                  {result.search_snippet && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      <strong>Summary:</strong> {result.search_snippet}
                    </Typography>
                  )}

                  {result.ai_summary && (
                    <>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>AI Analysis:</strong>
                      </Typography>
                      <Typography variant="body2" color="text.primary">
                        {result.ai_summary}
                      </Typography>
                    </>
                  )}

                  {result.content && result.content.length > 500 && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      <strong>Content Preview:</strong> {result.content.substring(0, 300)}...
                    </Typography>
                  )}

                  {result.metadata && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Status: {result.metadata.status_code} | 
                        Content-Type: {result.metadata.content_type || 'Unknown'}
                        {result.metadata.last_modified && ` | Modified: ${result.metadata.last_modified}`}
                      </Typography>
                    </Box>
                  )}

                  {result.error && (
                    <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                      <strong>Error:</strong> {result.error}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            ))}
          </Box>
        )}

        {!searching && results.length === 0 && query && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              No results found. Try a different search query.
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={searching}>
          Close
        </Button>
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={!query.trim() || searching}
          startIcon={<SearchIcon />}
        >
          {searching ? 'Searching...' : 'Search'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default WebSearch;
