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
         if (axios.isAxiosError(err)) {
          console.error('Axios error fetching SMS analytics:', {
            message: err.message,
            code: err.code,
            response: err.response?.data,
            status: err.response?.status,
            headers: err.response?.headers
          });
          setError(
            err.response?.data?.detail ||
            `API error: ${err.response?.status} ${err.response?.statusText}` ||
            err.message
          );
        } else {
          console.error('Unknown error fetching SMS analytics:', err);
          setError('Failed to fetch analytics data');
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [businessId, page]);

  return { metrics, loading, error, page, setPage };
}
