import { useState } from 'react';
import { Badge } from '../ui/Badge';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Table } from '../ui/Table';
import type { AuditEntry } from '../../types';

interface AuditLogTableProps {
  entries: AuditEntry[];
  pageSize?: number;
}

const resultVariant: Record<string, 'success' | 'error' | 'warning' | 'info'> = {
  pass: 'success',
  fail: 'error',
  warn: 'warning',
  info: 'info',
};

export function AuditLogTable({ entries, pageSize = 15 }: AuditLogTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const columns = [
    {
      key: 'created_at',
      header: 'Timestamp',
      sortable: true,
      render: (row: AuditEntry) => (
        <span className="text-xs whitespace-nowrap">
          {new Date(row.created_at).toLocaleString('en-GB', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      ),
    },
    {
      key: 'actor_name',
      header: 'Actor',
      render: (row: AuditEntry) => (
        <div>
          <span className="font-medium">{row.actor_name}</span>
          <span className="ml-1 text-xs text-[var(--color-text-muted)]">({row.actor_type})</span>
        </div>
      ),
    },
    { key: 'action', header: 'Action', sortable: true },
    {
      key: 'gate',
      header: 'Gate',
      sortable: true,
      render: (row: AuditEntry) => <span>Gate {row.gate}</span>,
    },
    {
      key: 'result',
      header: 'Result',
      sortable: true,
      render: (row: AuditEntry) => (
        <Badge variant={resultVariant[row.result] || 'neutral'}>{row.result}</Badge>
      ),
    },
    {
      key: 'details',
      header: 'Details',
      render: (row: AuditEntry) => (
        <div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setExpandedId(expandedId === row.id ? null : row.id);
            }}
            className="flex items-center gap-1 text-xs text-[var(--color-primary)] hover:underline"
          >
            {expandedId === row.id ? 'Hide' : 'Show'}
            {expandedId === row.id ? (
              <ChevronUp className="w-3 h-3" />
            ) : (
              <ChevronDown className="w-3 h-3" />
            )}
          </button>
          {expandedId === row.id && (
            <p className="mt-1 text-xs text-[var(--color-text-muted)] max-w-xs">{row.details}</p>
          )}
        </div>
      ),
    },
  ];

  return (
    <Table<AuditEntry & Record<string, unknown>>
      columns={columns as Parameters<typeof Table<AuditEntry & Record<string, unknown>>>[0]['columns']}
      data={entries as (AuditEntry & Record<string, unknown>)[]}
      pageSize={pageSize}
    />
  );
}
