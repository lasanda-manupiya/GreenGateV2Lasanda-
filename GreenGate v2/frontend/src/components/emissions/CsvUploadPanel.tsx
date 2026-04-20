import { useState, useRef, useCallback } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Spinner } from '../ui/Spinner';
import { uploadCsv, scanFolder } from '../../api/csvUpload';
import type { CsvUploadResult, FolderScanResult } from '../../api/csvUpload';
import { Upload, FolderOpen, CheckCircle, AlertTriangle, FileText } from 'lucide-react';

interface CsvUploadPanelProps {
  onSuccess: () => void;
}

export function CsvUploadPanel({ onSuccess }: CsvUploadPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<CsvUploadResult | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const [folderPath, setFolderPath] = useState('');
  const [scanning, setScanning] = useState(false);
  const [folderResult, setFolderResult] = useState<FolderScanResult | null>(null);
  const [folderError, setFolderError] = useState<string | null>(null);

  const [reportingYear, setReportingYear] = useState(2025);

  const handleFile = useCallback(async (file: File) => {
    setUploadError(null);
    setUploadResult(null);

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setUploadError('Please upload a .csv file');
      return;
    }

    setUploading(true);
    try {
      const result = await uploadCsv(file, reportingYear);
      setUploadResult(result);
      onSuccess();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [reportingYear, onSuccess]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [handleFile]);

  const handleFolderScan = useCallback(async () => {
    if (!folderPath.trim()) return;
    setFolderError(null);
    setFolderResult(null);
    setScanning(true);
    try {
      const result = await scanFolder(folderPath.trim(), reportingYear);
      setFolderResult(result);
      onSuccess();
    } catch (err: any) {
      setFolderError(err.response?.data?.detail || err.message || 'Folder scan failed');
    } finally {
      setScanning(false);
    }
  }, [folderPath, reportingYear, onSuccess]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* CSV Upload */}
      <Card
        header={
          <div className="flex items-center gap-2">
            <Upload className="w-4 h-4 text-[var(--color-primary)]" />
            <h2 className="text-base font-semibold text-[var(--color-text)]">Upload CSV</h2>
          </div>
        }
      >
        <div className="space-y-4">
          {/* Year selector */}
          <div className="flex items-center gap-2">
            <label className="text-sm text-[var(--color-text-muted)]">Reporting Year:</label>
            <select
              value={reportingYear}
              onChange={(e) => setReportingYear(Number(e.target.value))}
              className="text-sm border border-[var(--color-border)] rounded px-2 py-1 bg-white"
            >
              {[2023, 2024, 2025, 2026].map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>

          {/* Dropzone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragging
                ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5'
                : 'border-[var(--color-border)] hover:border-[var(--color-primary)]/50 hover:bg-gray-50'
              }
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
            />
            {uploading ? (
              <div className="flex flex-col items-center gap-2">
                <Spinner size="md" />
                <p className="text-sm text-[var(--color-text-muted)]">Processing CSV...</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <FileText className="w-8 h-8 text-[var(--color-text-muted)]" />
                <p className="text-sm font-medium text-[var(--color-text)]">
                  Drop a CSV file here or click to browse
                </p>
                <p className="text-xs text-[var(--color-text-muted)]">
                  Invoices, transactions, or expense exports (.csv, max 10MB)
                </p>
              </div>
            )}
          </div>

          {/* Upload Error */}
          {uploadError && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{uploadError}</p>
            </div>
          )}

          {/* Upload Result */}
          {uploadResult && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />
                <div className="text-sm text-green-800">
                  <strong>{uploadResult.entries_created}</strong> emission entries created
                  {' • '}
                  <strong>{uploadResult.total_co2e_tonnes.toFixed(2)}</strong> tCO2e total
                </div>
              </div>

              {uploadResult.entries.length > 0 && (
                <div className="text-xs space-y-1">
                  {uploadResult.entries.map((e, i) => (
                    <div key={i} className="flex justify-between py-1 border-b border-[var(--color-border)] last:border-0">
                      <span className="text-[var(--color-text)]">
                        <Badge variant={e.scope === 1 ? 'success' : e.scope === 2 ? 'warning' : 'neutral'} className="mr-1">
                          S{e.scope}
                        </Badge>
                        {e.category}
                      </span>
                      <span className="font-medium text-[var(--color-text)]">{e.co2e_tonnes.toFixed(2)} t</span>
                    </div>
                  ))}
                </div>
              )}

              {uploadResult.uncategorised_count > 0 && (
                <div className="p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
                  <strong>{uploadResult.uncategorised_count}</strong> rows could not be categorised
                  {uploadResult.uncategorised.slice(0, 3).map((r, i) => (
                    <div key={i} className="mt-1 text-amber-700">
                      Row {r.row_number}: {r.description || 'no description'} ({r.category || 'no category'})
                    </div>
                  ))}
                  {uploadResult.uncategorised_count > 3 && (
                    <div className="mt-1 text-amber-600">...and {uploadResult.uncategorised_count - 3} more</div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Folder Scan */}
      <Card
        header={
          <div className="flex items-center gap-2">
            <FolderOpen className="w-4 h-4 text-[var(--color-primary)]" />
            <h2 className="text-base font-semibold text-[var(--color-text)]">Scan Invoice Folder</h2>
          </div>
        }
      >
        <div className="space-y-4">
          <p className="text-xs text-[var(--color-text-muted)]">
            Point to a folder on the server containing CSV invoice files. All .csv files will be processed.
          </p>

          <div className="flex gap-2">
            <input
              type="text"
              value={folderPath}
              onChange={(e) => setFolderPath(e.target.value)}
              placeholder="/path/to/invoices"
              className="flex-1 text-sm border border-[var(--color-border)] rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:border-[var(--color-primary)]"
            />
            <Button onClick={handleFolderScan} disabled={scanning || !folderPath.trim()}>
              {scanning ? <Spinner size="sm" /> : <FolderOpen className="w-4 h-4" />}
              {scanning ? 'Scanning...' : 'Scan'}
            </Button>
          </div>

          {/* Folder Error */}
          {folderError && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{folderError}</p>
            </div>
          )}

          {/* Folder Result */}
          {folderResult && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />
                <div className="text-sm text-green-800">
                  <strong>{folderResult.files_processed}</strong> files processed
                  {' • '}
                  <strong>{folderResult.total_entries_created}</strong> entries
                  {' • '}
                  <strong>{folderResult.total_co2e_tonnes.toFixed(2)}</strong> tCO2e
                </div>
              </div>

              <div className="text-xs space-y-1">
                {folderResult.file_results.map((f, i) => (
                  <div key={i} className="flex justify-between items-center py-1.5 border-b border-[var(--color-border)] last:border-0">
                    <div className="flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-[var(--color-text-muted)]" />
                      <span className="text-[var(--color-text)]">{f.filename}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {f.errors ? (
                        <Badge variant="error">Error</Badge>
                      ) : (
                        <>
                          <span className="text-[var(--color-text-muted)]">{f.entries_created} entries</span>
                          <span className="font-medium text-[var(--color-text)]">{f.co2e_tonnes.toFixed(2)} t</span>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
