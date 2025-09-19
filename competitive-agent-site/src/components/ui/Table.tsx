"use client";
import React from "react";

export type Column<T> = {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
  width?: number | string;
  sortable?: boolean;
};

export type TableProps<T> = {
  columns: Column<T>[];
  data: T[];
  emptyText?: string;
  isLoading?: boolean;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number) => void;
  };
};

export default function Table<T>({ columns, data, emptyText = "No data", isLoading = false }: TableProps<T>) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={String(col.key)} style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #e5e7eb", width: col.width }}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan={columns.length} style={{ padding: 12 }}>Loading...</td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} style={{ padding: 12, color: "#6b7280" }}>{emptyText}</td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr key={idx}>
                {columns.map((col) => (
                  <td key={String(col.key)} style={{ padding: 8, borderBottom: "1px solid #f3f4f6" }}>
                    {col.render ? col.render(row) : (row as any)[col.key as any]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}


