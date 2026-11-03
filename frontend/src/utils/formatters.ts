/**
 * EcoSense Global Formatting and Null-Safety Utilities
 * Ensures zero values render cleanly as 0 / 0% without ever displaying NaN or undefined.
 */

/**
 * Calculates a safe percentage with protection against division by zero, null, undefined, and NaN.
 * Clamps result between 0 and 100 by default.
 */
export function safePercentage(
  numerator: number | string | null | undefined,
  denominator: number | string | null | undefined,
  decimals: number = 0,
  clamp: boolean = true
): number {
  const num = typeof numerator === 'string' ? parseFloat(numerator) : Number(numerator);
  const den = typeof denominator === 'string' ? parseFloat(denominator) : Number(denominator);

  if (isNaN(num) || isNaN(den) || den <= 0 || !isFinite(num) || !isFinite(den)) {
    return 0;
  }

  const result = (num / den) * 100;
  const rounded = Number(result.toFixed(decimals));
  
  if (clamp) {
    return Math.max(0, Math.min(100, rounded));
  }
  return rounded;
}

/**
 * Formats a percentage value safely into a string with '%' suffix.
 */
export function formatPercentage(
  value: number | string | null | undefined,
  decimals: number = 0
): string {
  if (value === null || value === undefined || value === '') {
    return '0%';
  }
  const num = typeof value === 'string' ? parseFloat(value) : Number(value);
  if (isNaN(num) || !isFinite(num)) {
    return '0%';
  }
  return `${num.toFixed(decimals)}%`;
}

/**
 * Formats weights in kg safely (e.g. "12.5 kg" or "0 kg").
 */
export function formatWeight(
  kg: number | string | null | undefined,
  decimals: number = 1
): string {
  if (kg === null || kg === undefined || kg === '') {
    return '0 kg';
  }
  const num = typeof kg === 'string' ? parseFloat(kg) : Number(kg);
  if (isNaN(num) || !isFinite(num) || num <= 0) {
    return '0 kg';
  }
  return `${num.toFixed(decimals)} kg`;
}

/**
 * Formats integer/counts safely (e.g. 0, 42, 1,200).
 */
export function formatNumber(
  val: number | string | null | undefined,
  fallback: string = '0'
): string {
  if (val === null || val === undefined || val === '') {
    return fallback;
  }
  const num = typeof val === 'string' ? parseFloat(val) : Number(val);
  if (isNaN(num) || !isFinite(num)) {
    return fallback;
  }
  return num.toLocaleString();
}

/**
 * Formats date string safely without showing technical errors.
 */
export function formatDate(
  dateStr: string | null | undefined,
  fallback: string = '—'
): string {
  if (!dateStr) return fallback;
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return fallback;
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return fallback;
  }
}
