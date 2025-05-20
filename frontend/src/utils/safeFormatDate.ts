// Defensive date formatting utility for analytics
export function safeFormatDate(date: string | Date | null | undefined, formatStr: string): string {
  if (!date) return 'Unknown';
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    if (!d || isNaN(d.getTime())) return 'Unknown';
    // Use date-fns for formatting if available, else fallback
    try {
      // Dynamically import date-fns/format to avoid circular deps
      // @ts-ignore
      return require('date-fns/format')(d, formatStr);
    } catch {
      return d.toLocaleString();
    }
  } catch {
    return 'Unknown';
  }
}
