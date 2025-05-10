export interface ValidationResult {
  problem_id: string;
  validation_score: number;
  confidence_score: number;
  validation_flags: string[];
  sentiment_summary: {
    overall_sentiment: string;
    positive_ratio: number;
    negative_ratio: number;
    neutral_ratio: number;
    average_score: number;
    weighted_average_score: number;
  };
  engagement_metrics: {
    avg_score: number;
    avg_comments: number;
    total_engagement: number;
    unique_users: number;
  };
  temporal_analysis: {
    earliest_post: string;
    latest_post: string;
    avg_posts_per_day: number;
    activity_period_days: number;
  };
}

export interface ValidationStatusResponse {
  status: 'processing' | 'completed' | 'failed';
  request_id: string;
  timestamp: string;
  result?: ValidationResult;
}
