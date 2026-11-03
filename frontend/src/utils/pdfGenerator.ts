import React from 'react';
import QRCode from 'qrcode';
import { pdf } from '@react-pdf/renderer';
import { Bin } from '../types';
import { BinQRPdfDocument, BinWithQrData } from '../components/common/BinQRPdfDocument';

/**
 * Generate a high-resolution QR code Data URL for a given target URL.
 */
export const generateQrDataUrl = async (url: string): Promise<string> => {
  return await QRCode.toDataURL(url, {
    width: 450,
    margin: 1,
    errorCorrectionLevel: 'H',
    color: {
      dark: '#000000',
      light: '#FFFFFF',
    },
  });
};

/**
 * Convert an array of Bin objects into BinWithQrData objects with resolved URLs and QR images.
 */
export const prepareBinsForPdf = async (
  bins: Bin[],
  baseUrl?: string
): Promise<BinWithQrData[]> => {
  const origin = baseUrl || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:5173');

  return await Promise.all(
    bins.map(async (bin) => {
      const binUrl = `${origin}/bin/${bin.qr_token}`;
      const qrDataUrl = await generateQrDataUrl(binUrl);
      return {
        ...bin,
        binUrl,
        qrDataUrl,
      };
    })
  );
};

/**
 * Generate and trigger download of an A4 Multi-Page PDF containing one placard per bin.
 */
export const downloadBinQRPdf = async (
  bins: Bin[],
  customFilename?: string
): Promise<void> => {
  if (!bins || bins.length === 0) {
    throw new Error('No bins available to export.');
  }

  const binsWithQr = await prepareBinsForPdf(bins);
  const doc = React.createElement(BinQRPdfDocument, { bins: binsWithQr });
  const blob = await pdf(doc as any).toBlob();

  const filename =
    customFilename ||
    (bins.length === 1
      ? `EcoSense_Bin_${bins[0].bin_code}_QR.pdf`
      : 'EcoSense_Bin_QR_Codes.pdf');

  const blobUrl = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = blobUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(blobUrl);
};
