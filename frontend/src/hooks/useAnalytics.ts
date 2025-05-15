import { useQuery } from 'react-query';
import axios from 'axios';
import { AnalyticsData } from '../types/analytics';

/**
 * Fetch consolidated analytics for a business.
 * Optional date range can be passed in ISO format; defaults to last 30 days.
 */
export function useAnalytics(businessId: string, start?: string, end?: string) {
  const queryKey = ['analytics', businessId, start, end];

  const query = useQuery<AnalyticsData>(
    queryKey,
    async () => {
      if (!businessId) throw new Error('No business selected');
      const res = await axios.get<AnalyticsData>(`/api/analytics/${businessId}`, {
        params: {
          start,
          end,
        },
      });
      return res.data;
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
