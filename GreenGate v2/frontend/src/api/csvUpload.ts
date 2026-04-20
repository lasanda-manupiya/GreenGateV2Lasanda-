import client from './client';

export interface CsvUploadEntry {
  scope: number;
  category: string;
  activity_data: number;
  activity_unit: string;
  emission_factor: number;
  co2e_tonnes: number;
  transaction_count: number;
}

export interface UncategorisedRow {
  row_number: number;
  description: string;
  amount: number;
  category: string;
}

export interface CsvUploadResult {
  entries_created: number;
  categorised_count: number;
  uncategorised_count: number;
  total_co2e_tonnes: number;
  entries: CsvUploadEntry[];
  uncategorised: UncategorisedRow[];
}

export interface FileResult {
  filename: string;
  entries_created: number;
  co2e_tonnes: number;
  errors: string | null;
}

export interface FolderScanResult {
  files_processed: number;
  total_entries_created: number;
  total_co2e_tonnes: number;
  file_results: FileResult[];
}

export const uploadCsv = async (
  file: File,
  reportingYear: number = 2025,
): Promise<CsvUploadResult> => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await client.post<CsvUploadResult>(
    `/emissions/upload/csv?reporting_year=${reportingYear}`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return res.data;
};

export const scanFolder = async (
  folderPath: string,
  reportingYear: number = 2025,
): Promise<FolderScanResult> => {
  const res = await client.post<FolderScanResult>('/emissions/upload/folder', {
    folder_path: folderPath,
    reporting_year: reportingYear,
  });
  return res.data;
};
