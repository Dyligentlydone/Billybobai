import { useQuery } from 'react-query';
import { AxiosError } from 'axios';
import api from '../services/api';
import { AnalyticsData } from '../types/analytics';

/**
 * Fetch consolidated analytics for a business.
 * Optional date range can be passed in ISO format; defaults to last 30 days.
 */
export function useAnalytics(businessId: string, start?: string, end?: string) {
  const queryKey = ['analytics', businessId, start, end];

  const emptyAnalytics: AnalyticsData = {
    overview: {
      totalInteractions: '0',
      totalCost: 0,
      averageResponseTime: '0s',
      successRate: 0,
    },
    sms: {
      totalCount: '0',
      responseTime: '0s',
      deliveryRate: 0,
      optOutRate: 0,
      aiCost: 0,
      serviceCost: 0,
      qualityMetrics: [],
      responseTypes: [],
      dailyCosts: [],
      hourlyActivity: [],
      conversations: [],
    },
    voice: {
      totalCount: '0',
      inboundCalls: 0,
      outboundCalls: 0,
      averageDuration: 0,
      successRate: 0,
      hourlyActivity: [],
    },
    email: {
      totalCount: '0',
      responseTime: '0s',
      openRate: 0,
      clickRate: 0,
      bounceRate: 0,
      hourlyActivity: [],
    },
    dateRange: {
      start: start || new Date().toISOString(),
      end: end || new Date().toISOString(),
    },
  };

  const query = useQuery<AnalyticsData>(
    queryKey,
    async () => {
      if (!businessId) throw new Error('No business selected');
      try {
        const res = await api.get<AnalyticsData>(`/api/analytics/${businessId}`, {
          params: { start, end },
        });
        return res.data;
      } catch (err) {
        const axErr = err as AxiosError;
        if (axErr.response?.status === 404) {
          // Business not found – return empty metrics instead of throwing
          return emptyAnalytics;
        }
        throw err;
      }
    },
    {
      enabled: !!businessId,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  return {
    analytics: query.data,
    ...query,
  };
}
