import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from 'react-query';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Chip,
  Alert,
} from '@mui/material';
import { validateProblem } from '../services/api';

const ProblemForm: React.FC = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [keyword, setKeyword] = useState('');
  const [keywords, setKeywords] = useState<string[]>([]);
  const [targetMarket, setTargetMarket] = useState('');

  const validation = useMutation(validateProblem, {
    onSuccess: (data) => {
      navigate(`/results/${data.request_id}`);
    },
  });

  const handleAddKeyword = () => {
    if (keyword.trim() && !keywords.includes(keyword.trim())) {
      setKeywords([...keywords, keyword.trim()]);
      setKeyword('');
    }
  };

  const handleRemoveKeyword = (keywordToRemove: string) => {
    setKeywords(keywords.filter((k) => k !== keywordToRemove));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title && description && keywords.length > 0) {
      validation.mutate({
        title,
        description,
        keywords,
        target_market: targetMarket || undefined,
      });
    }
  };

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Validate Problem Statement
        </Typography>

        <form onSubmit={handleSubmit}>
          <TextField
            label="Problem Title"
            fullWidth
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            margin="normal"
            required
          />

          <TextField
            label="Problem Description"
            fullWidth
            multiline
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            margin="normal"
            required
          />

          <Box sx={{ mt: 2, mb: 2 }}>
            <TextField
              label="Add Keyword"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
            />
            <Button
              onClick={handleAddKeyword}
              variant="outlined"
              sx={{ ml: 1 }}
            >
              Add
            </Button>
          </Box>

          <Box sx={{ mt: 2, mb: 2 }}>
            {keywords.map((k) => (
              <Chip
                key={k}
                label={k}
                onDelete={() => handleRemoveKeyword(k)}
                sx={{ mr: 1, mb: 1 }}
              />
            ))}
          </Box>

          <TextField
            label="Target Market (Optional)"
            fullWidth
            value={targetMarket}
            onChange={(e) => setTargetMarket(e.target.value)}
            margin="normal"
          />

          {validation.isError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              Error submitting problem for validation
            </Alert>
          )}

          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            fullWidth
            sx={{ mt: 3 }}
            disabled={!title || !description || keywords.length === 0 || validation.isLoading}
          >
            {validation.isLoading ? 'Validating...' : 'Validate Problem'}
          </Button>
        </form>
      </Paper>
    </Container>
  );
};

export default ProblemForm;
