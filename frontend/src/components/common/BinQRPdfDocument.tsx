import React from 'react';
import { Document, Page, Text, View, StyleSheet, Image } from '@react-pdf/renderer';
import { Bin } from '../../types';

export interface BinWithQrData extends Bin {
  qrDataUrl: string;
  binUrl: string;
}

const styles = StyleSheet.create({
  page: {
    padding: 8,
    backgroundColor: '#FFFFFF',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'Helvetica',
  },

  card: {
    width: '100%',
    height: '100%',
    borderWidth: 1.5,
    borderColor: '#CBD5E1',
    borderRadius: 16,
    paddingTop: 20,
    paddingBottom: 16,
    paddingHorizontal: 24,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },

  header: {
    width: '100%',
    borderBottomWidth: 1.5,
    borderBottomColor: '#E2E8F0',
    paddingBottom: 10,
    marginBottom: 14,
    alignItems: 'center',
    textAlign: 'center',
  },

  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 3,
  },

  brandTitle: {
    fontSize: 22,
    fontFamily: 'Helvetica-Bold',
    color: '#059669',
    letterSpacing: 2,
  },

  instituteName: {
    fontSize: 9,
    fontFamily: 'Helvetica-Bold',
    color: '#1E293B',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 2,
  },

  tagline: {
    fontSize: 7.5,
    color: '#64748B',
    letterSpacing: 0.2,
  },

  mainContent: {
    width: '100%',
    flexGrow: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },

  qrContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: '#0F172A',
    borderRadius: 16,
    padding: 12,
    backgroundColor: '#FFFFFF',
    marginBottom: 12,
  },

  qrImage: {
    width: 160,
    height: 160,
  },

  qrSubtitle: {
    fontSize: 7.5,
    color: '#64748B',
    marginTop: 4,
    fontFamily: 'Helvetica',
  },

  binCodeSection: {
    alignItems: 'center',
    marginBottom: 10,
  },

  binCodeLabel: {
    fontSize: 8,
    fontFamily: 'Helvetica-Bold',
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 2,
  },

  binCodeValue: {
    fontSize: 24,
    fontFamily: 'Helvetica-Bold',
    color: '#0F172A',
    letterSpacing: 1,
  },

  wasteStreamBox: {
    width: '80%',
    backgroundColor: '#F8FAFC',
    borderWidth: 1.5,
    borderColor: '#0F172A',
    borderRadius: 10,
    paddingVertical: 7,
    paddingHorizontal: 12,
    alignItems: 'center',
    marginBottom: 10,
  },

  wasteStreamLabel: {
    fontSize: 7,
    fontFamily: 'Helvetica-Bold',
    color: '#475569',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 2,
  },

  wasteStreamValue: {
    fontSize: 13,
    fontFamily: 'Helvetica-Bold',
    color: '#0F172A',
    textTransform: 'uppercase',
  },

  detailsRow: {
    width: '88%',
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 10,
    marginBottom: 8,
  },

  detailBox: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 10,
  },

  detailLabel: {
    fontSize: 6.5,
    fontFamily: 'Helvetica-Bold',
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 2,
  },

  detailTitle: {
    fontSize: 9.5,
    fontFamily: 'Helvetica-Bold',
    color: '#0F172A',
  },

  detailSubtitle: {
    fontSize: 7.5,
    color: '#64748B',
    marginTop: 1.5,
  },

  statusText: {
    fontSize: 7.5,
    fontFamily: 'Helvetica-Bold',
    color: '#059669',
    marginTop: 1.5,
  },

  footer: {
    width: '100%',
    borderTopWidth: 1.5,
    borderTopColor: '#E2E8F0',
    paddingTop: 8,
    alignItems: 'center',
    textAlign: 'center',
  },

  footerInstruction: {
    fontSize: 8,
    fontFamily: 'Helvetica-Bold',
    color: '#334155',
    marginBottom: 2,
  },

  footerUrl: {
    fontSize: 7,
    color: '#64748B',
  },
});

interface BinQRPdfDocumentProps {
  bins: BinWithQrData[];
}

export const BinQRPdfDocument: React.FC<BinQRPdfDocumentProps> = ({ bins }) => {
  return (
    <Document
      title="EcoSense Bin QR Placards"
      author="EcoSense DBIT Mumbai"
    >
      {bins.map((bin) => {
        const wasteTypeName =
          bin.waste_type?.name || 'GENERAL RECYCLABLE';

        const locationName =
          bin.location?.name || 'Campus Grounds';

        const locationSub = [
          bin.location?.building,
          bin.location?.floor,
        ]
          .filter(Boolean)
          .join(' • ');

        const capacityText =
          `${bin.capacity_liters || 100} Litres`;

        const statusText =
          `Status: ${bin.status || 'ACTIVE'}`;

        return (
          <Page
            key={bin.bin_id}
            size={[420, 637.5]}
            style={styles.page}
          >
            <View style={styles.card} wrap={false}>

              <View style={styles.header}>
                <View style={styles.brandRow}>
                  <Text style={styles.brandTitle}>
                    ECOSENSE
                  </Text>
                </View>

                <Text style={styles.instituteName}>
                  DON BOSCO INSTITUTE OF TECHNOLOGY (DBIT), MUMBAI
                </Text>

                <Text style={styles.tagline}>
                  AI-Based Zero Waste Smart Campus Management
                </Text>
              </View>

              <View style={styles.mainContent}>

                <View style={styles.qrContainer}>
                  {bin.qrDataUrl ? (
                    <Image
                      src={bin.qrDataUrl}
                      style={styles.qrImage}
                    />
                  ) : null}

                  <Text style={styles.qrSubtitle}>
                    Scan with any camera or QR app
                  </Text>
                </View>

                <View style={styles.binCodeSection}>
                  <Text style={styles.binCodeLabel}>
                    PHYSICAL BIN CODE
                  </Text>

                  <Text style={styles.binCodeValue}>
                    {bin.bin_code}
                  </Text>
                </View>

                <View style={styles.wasteStreamBox}>
                  <Text style={styles.wasteStreamLabel}>
                    DESIGNATED WASTE STREAM
                  </Text>

                  <Text style={styles.wasteStreamValue}>
                    {wasteTypeName}
                  </Text>
                </View>

                <View style={styles.detailsRow}>
                  <View style={styles.detailBox}>
                    <Text style={styles.detailLabel}>
                      LOCATION
                    </Text>

                    <Text style={styles.detailTitle}>
                      {locationName}
                    </Text>

                    {locationSub ? (
                      <Text style={styles.detailSubtitle}>
                        {locationSub}
                      </Text>
                    ) : null}
                  </View>

                  <View style={styles.detailBox}>
                    <Text style={styles.detailLabel}>
                      CAPACITY & STATUS
                    </Text>

                    <Text style={styles.detailTitle}>
                      {capacityText}
                    </Text>

                    <Text style={styles.statusText}>
                      {statusText}
                    </Text>
                  </View>
                </View>

              </View>

              <View style={styles.footer}>
                <Text style={styles.footerInstruction}>
                  Scan to view this bin in EcoSense and record waste disposal.
                </Text>

                <Text style={styles.footerUrl}>
                  URL: {bin.binUrl}
                </Text>
              </View>

            </View>
          </Page>
        );
      })}
    </Document>
  );
};