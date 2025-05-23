import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {  Container,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemText,
  Tooltip,
} from '@mui/material';
import { ValidationStatusResponse } from '../types/validation';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts';
import { getValidationStatus } from '../services/api';

const ValidationResults: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, error } = useQuery<ValidationStatusResponse, Error>({
    queryKey: ['validation', id],
    queryFn: async () => {
      const response = await getValidationStatus(id!);
      return response as ValidationStatusResponse;
    },
    refetchInterval: (query) =>
      query.state.data?.status === 'completed' || query.state.data?.status === 'failed' ? false : 5000
  });

  const renderValidationFlags = () => {
    if (!data?.result?.validation_flags?.length) return null;

    const flagMessages: Record<string, string> = {
      low_sample_size: "Limited data available - results may not be fully representative",
      low_engagement: "Low engagement detected - may indicate limited market interest",
      low_activity: "Infrequent discussion activity - might be an emerging or niche problem"
    };    return (
      <Alert severity="info" sx={{ mt: 2 }}>
        <AlertTitle>Validation Notes</AlertTitle>
        <List>
          {data.result.validation_flags.map((flag: string) => (
            <ListItem key={flag}>
              <ListItemText primary={flagMessages[flag] || flag} />
            </ListItem>
          ))}
        </List>
      </Alert>
    );
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !data) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Typography color="error">Error loading validation results</Typography>
      </Box>
    );
  }

  if (data.status === 'processing') {
    return (
      <Container maxWidth="md">
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="60vh"
        >
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Validating Problem...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (data.status === 'failed') {
    return (
      <Container maxWidth="md">
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="60vh"
        >
          <Typography color="error" variant="h6">
            Validation failed. Please try again.
          </Typography>
        </Box>
      </Container>
    );
  }

  const { result } = data;
  if (!result) return null;

  const sentimentData = [
    {
      name: 'Positive',
      value: result.sentiment_summary.positive_ratio * 100,
    },
    {
      name: 'Neutral',
      value: result.sentiment_summary.neutral_ratio * 100,
    },
    {
      name: 'Negative',
      value: result.sentiment_summary.negative_ratio * 100,
    },
  ];

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        Validation Results
      </Typography>

      {renderValidationFlags()}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Validation Score
              </Typography>
              <Box display="flex" alignItems="center">
                <Typography variant="h3" color="primary" sx={{ mr: 2 }}>
                  {(result.validation_score * 100).toFixed(1)}%
                </Typography>
                <Tooltip title="Confidence in validation results">
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Confidence: {(result.confidence_score * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                </Tooltip>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall Sentiment
              </Typography>
              <Typography variant="h3" color="primary">
                {result.sentiment_summary.overall_sentiment}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Engagement
              </Typography>
              <Typography variant="h3" color="primary">
                {result.engagement_metrics.total_engagement.toFixed(0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Sentiment Analysis
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sentimentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="value" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Engagement Metrics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Typography variant="subtitle2">Average Score</Typography>
                <Typography variant="h6">
                  {result.engagement_metrics.avg_score.toFixed(1)}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="subtitle2">Average Comments</Typography>
                <Typography variant="h6">
                  {result.engagement_metrics.avg_comments.toFixed(1)}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="subtitle2">Posts per Day</Typography>
                <Typography variant="h6">
                  {result.temporal_analysis.avg_posts_per_day.toFixed(1)}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Detailed Metrics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Typography variant="subtitle2">Active Period</Typography>
                <Typography variant="h6">
                  {result.temporal_analysis.activity_period_days} days
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="subtitle2">Unique Users</Typography>
                <Typography variant="h6">
                  {result.engagement_metrics.unique_users}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="subtitle2">Average Daily Posts</Typography>
                <Typography variant="h6">
                  {result.temporal_analysis.avg_posts_per_day.toFixed(1)}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ValidationResults;
