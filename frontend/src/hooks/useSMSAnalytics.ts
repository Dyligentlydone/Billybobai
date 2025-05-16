import { useState, useEffect } from 'react';
import { SMSMetrics } from '../types/analytics';
import axios from 'axios';

export function useSMSAnalytics(businessId: string, clientId: string) {
  const [metrics, setMetrics] = useState<SMSMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  useEffect(() => {
    async function fetchData() {
      if (!businessId) return;
      
      try {
        setLoading(true);
        setError(null);

        // Clean businessId to remove any curly braces or whitespace
        const cleanBusinessId = typeof businessId === 'string' ? businessId.replace(/[{}\s]/g, '') : businessId;
        console.log('Fetching SMS analytics for businessId:', cleanBusinessId);
        const [metricsRes, conversationsRes] = await Promise.all([
          axios.get(`/api/analytics/conversations/metrics/${cleanBusinessId}`),
          axios.get(`/api/analytics/conversations/${cleanBusinessId}`, {
            params: { page, per_page: 5 }
          })
        ]);

        // Transform data to match SMSMetrics interface
        const transformedData: SMSMetrics = {
          totalCount: metricsRes.data.total_messages || 0,
          responseTime: metricsRes.data.response_times.average || 0,
          aiCost: 0, // TODO: Add to backend
          serviceCost: 0, // TODO: Add to backend
          deliveryRate: 0.98, // TODO: Add to backend
          optOutRate: 0.02, // TODO: Add to backend
          qualityMetrics: [], // TODO: Add to backend
          responseTypes: metricsRes.data.topics.map((t: any) => ({
            type: t.topic,
            count: t.count
          })),
          dailyCosts: [], // TODO: Add to backend
          hourlyActivity: metricsRes.data.hourly_activity,
          conversations: conversationsRes.data.conversations
        };

        setMetrics(transformedData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch analytics data');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [businessId, page]);

  return { metrics, loading, error, page, setPage };
}
