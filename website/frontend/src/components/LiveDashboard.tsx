import React from 'react';
import { Box, Grid, Paper, Typography, CircularProgress } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Line } from 'react-chartjs-2';
import { useWebSocket } from '../hooks/useWebSocket';
import { useStore } from '../store';
import { ComplianceCard } from './ComplianceCard';
import { CategoryScores } from './CategoryScores';
import { RecentActivity } from './RecentActivity';

export const LiveDashboard: React.FC<{ organizationId: string }> = ({ organizationId }) => {
  const theme = useTheme();
  const { connectionStatus, updates, metrics } = useStore();
  useWebSocket(organizationId);

  // Prepare chart data
  const chartData = {
    labels: metrics.timestamps,
    datasets: [
      {
        label: 'Overall Compliance Score',
        data: metrics.scores,
        fill: false,
        borderColor: theme.palette.primary.main,
        tension: 0.1,
      },
      ...Object.entries(metrics.categoryScores).map(([category, scores]) => ({
        label: category,
        data: scores,
        fill: false,
        borderColor: theme.palette.secondary[category.toLowerCase()],
        tension: 0.1,
      })),
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: true,
        text: 'Compliance Score Trends',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
      },
    },
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Connection Status */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="h6">
          Status: {connectionStatus}
        </Typography>
        {connectionStatus === 'connected' ? (
          <Box sx={{ color: 'success.main' }}>●</Box>
        ) : (
          <CircularProgress size={20} />
        )}
      </Box>

      {/* Main Grid */}
      <Grid container spacing={3}>
        {/* Compliance Overview */}
        <Grid item xs={12} md={4}>
          <ComplianceCard
            score={metrics.currentScore}
            trend={metrics.scoreTrend}
            status={metrics.currentScore >= 0.6 ? 'PASS' : 'FAIL'}
          />
        </Grid>

        {/* Category Scores */}
        <Grid item xs={12} md={8}>
          <CategoryScores scores={metrics.latestCategoryScores} />
        </Grid>

        {/* Trend Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Line data={chartData} options={chartOptions} />
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <RecentActivity updates={updates.slice(0, 10)} />
        </Grid>

        {/* Compliance Issues */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Active Issues
            </Typography>
            {metrics.activeIssues.map((issue) => (
              <Box key={issue.id} sx={{ mb: 2 }}>
                <Typography variant="subtitle1" color="error">
                  {issue.category}
                </Typography>
                <Typography variant="body2">
                  {issue.description}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};