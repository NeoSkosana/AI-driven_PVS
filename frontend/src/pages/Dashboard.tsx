import React from 'react';
import { useQuery } from 'react-query';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  CircularProgress,
} from '@mui/material';
import { listProblems } from '../services/api';
import { ValidationResult } from '../services/api';

const Dashboard: React.FC = () => {
  const { data: problems, isLoading, error } = useQuery('problems', listProblems);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Typography color="error">Error loading problems</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Problem Validation Dashboard
        </Typography>
        <Button
          component={RouterLink}
          to="/validate"
          variant="contained"
          color="primary"
          sx={{ mb: 3 }}
        >
          Validate New Problem
        </Button>
      </Box>

      <Grid container spacing={3}>
        {problems?.map((problem: ValidationResult) => (
          <Grid item xs={12} md={6} key={problem.problem_id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {problem.problem_id}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Validation Score: {(problem.validation_score * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Sentiment: {problem.sentiment_summary.overall_sentiment}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Total Engagement: {problem.engagement_metrics.total_engagement}
                </Typography>
                <Button
                  component={RouterLink}
                  to={`/results/${problem.problem_id}`}
                  variant="outlined"
                  color="primary"
                  sx={{ mt: 2 }}
                >
                  View Details
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Dashboard;
