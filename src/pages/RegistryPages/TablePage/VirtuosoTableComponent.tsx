import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { TableVirtuoso, TableComponents } from 'react-virtuoso';

interface Data {
  item_id: number;
  name: string;
  brand: string;
  price_cents: number;
  price_string: string;
  descr: string;
}

interface ColumnData {
  dataKey: keyof Data;
  label: string;
  numeric?: boolean;
  width?: number;
  smallScreenWidth?: number;
}

const columns: ColumnData[] = [
  {
    width: 180,
    smallScreenWidth: 120,
    label: 'Item',
    dataKey: 'name',
  },
  {
    width: 150,
    smallScreenWidth: 100,
    label: 'Brand',
    dataKey: 'brand',
  },
  {
    width: 120,
    smallScreenWidth: 80,
    label: 'Price',
    dataKey: 'price_string',
    numeric: false,
  },
];

const VirtuosoTableComponents: TableComponents<Data> = {
  Scroller: React.forwardRef<HTMLDivElement>((props, ref) => (
    <TableContainer
      component={Paper}
      {...props}
      ref={ref}
      sx={{
        backgroundColor: 'beige',
        width: 450, // total of column widths
      }}
    />
  )),
  Table: (props) => (
    <Table
      {...props}
      size="small"
      sx={{
        borderCollapse: 'separate',
        tableLayout: 'fixed',
        width: 450,
      }}
    />
  ),
  TableHead: React.forwardRef<HTMLTableSectionElement>((props, ref) => (
    <TableHead {...props} ref={ref} />
  )),
  TableRow,
  TableBody: React.forwardRef<HTMLTableSectionElement>((props, ref) => (
    <TableBody {...props} ref={ref} />
  )),
};

function fixedHeaderContent() {
  return (
    <TableRow>
      {columns.map((column) => (
        <TableCell
          key={column.dataKey}
          variant="head"
          align={column.numeric ? 'right' : 'left'}
          sx={{
            backgroundColor: 'beige',
            fontSize: '11px',
            fontWeight: 'bold',
            width: column.width,
            maxWidth: column.width,
            minWidth: column.width,
          }}
        >
          {column.label}
        </TableCell>
      ))}
    </TableRow>
  );
}

export default function ReactVirtualizedTable({
  registryItemsMod,
  displayedId,
  setDisplayedId,
}) {
  const handleRowClick = (item: Data) => {
    setDisplayedId(item.item_id);
  };

  function rowContent(index: number, row: Data) {
    const isSelected = row.item_id === displayedId;

    return (
      <TableRow
        onClick={() => handleRowClick(row)}
        sx={{
          backgroundColor: isSelected ? 'khaki' : 'inherit',
          cursor: 'pointer',
          transition: 'background-color 0.2s ease',
        }}
      >
        {columns.map((column) => (
          <TableCell
            key={column.dataKey}
            align={column.numeric ? 'right' : 'left'}
            sx={{
              fontSize: '10px',
              width: column.width,
              maxWidth: column.width,
              minWidth: column.width,
            }}
          >
            {row[column.dataKey]}
          </TableCell>
        ))}
      </TableRow>
    );
  }

  return (
    <Paper style={{ height: 450, width: 450, margin: '0 auto' }}>
      <TableVirtuoso
        data={registryItemsMod}
        components={VirtuosoTableComponents}
        fixedHeaderContent={fixedHeaderContent}
        itemContent={(index, item) => rowContent(index, item)}
      />
    </Paper>
  );
}