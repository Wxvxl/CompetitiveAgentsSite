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

  
  const tableWrapperStyle: React.CSSProperties = {
    overflowX: "auto",
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
    backgroundColor: "#ffffff",
  };

  const tableStyle: React.CSSProperties = {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "0.9rem",
  };

  const thStyle: React.CSSProperties = {
    textAlign: "left",
    padding: "0.75rem 1rem",
    fontWeight: 600,
    color: "#4b5563",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    borderBottom: "1px solid #e5e7eb",
    backgroundColor: "#f9fafb", 
  };


  const tdStyle: React.CSSProperties = {
    padding: "0.75rem 1rem",
    borderBottom: "1px solid #e5e7eb",
    color: "#374151",
  };


  const trEvenStyle: React.CSSProperties = {
    backgroundColor: "#f9fafb",
  };

  const placeholderCellStyle: React.CSSProperties = {
    padding: "2rem",
    textAlign: "center",
    color: "#6b7280",
    fontStyle: "italic",
  };

  return (
    <div style={tableWrapperStyle}>
      <table style={tableStyle}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={String(col.key)} style={{ ...thStyle, width: col.width }}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr><td colSpan={columns.length} style={placeholderCellStyle}>Loading...</td></tr>
          ) : data.length === 0 ? (
            <tr><td colSpan={columns.length} style={placeholderCellStyle}>{emptyText}</td></tr>
          ) : (
            data.map((row, idx) => {
              const isEvenRow = idx % 2 === 0;


              const finalTdStyle = (idx === data.length - 1)
                ? { ...tdStyle, borderBottom: 'none' }
                : tdStyle;

              return (
                <tr
                  key={idx}
                  style={isEvenRow ? trEvenStyle : {}} 
                >
                  {columns.map((col) => (
                    <td key={String(col.key)} style={finalTdStyle}>
                      {col.render ? col.render(row) : (row as any)[col.key as any]}
                    </td>
                  ))}
                </tr>
              )
            })
          )}
        </tbody>
      </table>
    </div>
  );
}