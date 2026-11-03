import { describe, it, expect, vi } from 'vitest';
import { generateQrDataUrl, prepareBinsForPdf, downloadBinQRPdf } from '../utils/pdfGenerator';
import { Bin } from '../types';

describe('PDF Generation and QR Data Pipeline', () => {
  const sampleBins: Bin[] = [
    {
      bin_id: 'bin-1',
      bin_code: 'B-001',
      location_id: 1,
      waste_type_id: 1,
      status: 'ACTIVE',
      capacity_liters: 120,
      current_fill_percentage: 10,
      qr_token: '1111-2222-3333-4444',
      location: {
        location_id: 1,
        code: 'LOC-1',
        name: 'Central Canteen',
        building: 'Main Building',
        floor: 'Ground Floor',
        is_active: true,
      },
      waste_type: {
        waste_type_id: 1,
        code: 'WET',
        name: 'WET_ORGANIC',
        is_active: true,
      },
    },
    {
      bin_id: 'bin-2',
      bin_code: 'B-002',
      location_id: 2,
      waste_type_id: 2,
      status: 'ACTIVE',
      capacity_liters: 80,
      current_fill_percentage: 45,
      qr_token: '5555-6666-7777-8888',
      location: {
        location_id: 2,
        code: 'LOC-2',
        name: 'Engineering Workshop',
        building: 'Tech Block',
        floor: '1st Floor',
        is_active: true,
      },
      waste_type: {
        waste_type_id: 2,
        code: 'DRY',
        name: 'DRY_RECYCLABLE',
        is_active: true,
      },
    },
    {
      bin_id: 'bin-3',
      bin_code: 'B-003',
      location_id: 3,
      waste_type_id: 3,
      status: 'MAINTENANCE',
      capacity_liters: 60,
      current_fill_percentage: 90,
      qr_token: '9999-0000-1111-2222',
      location: {
        location_id: 3,
        code: 'LOC-3',
        name: 'Computer Lab 4',
        building: 'IT Block',
        floor: '3rd Floor',
        is_active: true,
      },
      waste_type: {
        waste_type_id: 3,
        code: 'EWASTE',
        name: 'E_WASTE',
        is_active: true,
      },
    },
  ];

  it('generates high-resolution QR Data URLs for valid bin URLs', async () => {
    const testUrl = 'http://localhost:5173/bin/1111-2222-3333-4444';
    const dataUrl = await generateQrDataUrl(testUrl);

    expect(dataUrl).toBeDefined();
    expect(dataUrl.startsWith('data:image/png;base64,')).toBe(true);
    expect(dataUrl.length).toBeGreaterThan(100);
  });

  it('prepares multiple bins for PDF with exactly 1 QR entry per bin', async () => {
    const prepared = await prepareBinsForPdf(sampleBins, 'https://ecosenseapp.site');

    expect(prepared.length).toBe(3);
    expect(prepared[0].bin_code).toBe('B-001');
    expect(prepared[0].binUrl).toBe('https://ecosenseapp.site/bin/1111-2222-3333-4444');
    expect(prepared[0].qrDataUrl.startsWith('data:image/png;base64,')).toBe(true);

    expect(prepared[1].bin_code).toBe('B-002');
    expect(prepared[1].binUrl).toBe('https://ecosenseapp.site/bin/5555-6666-7777-8888');

    expect(prepared[2].bin_code).toBe('B-003');
    expect(prepared[2].binUrl).toBe('https://ecosenseapp.site/bin/9999-0000-1111-2222');
  });

  it('throws an error if attempting to export an empty list of bins', async () => {
    await expect(downloadBinQRPdf([])).rejects.toThrow('No bins available to export.');
  });
});
