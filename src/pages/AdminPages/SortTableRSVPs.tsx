import * as React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    TableSortLabel,
} from '@mui/material';
import { TableVirtuoso, TableComponents } from 'react-virtuoso';

export interface Data {
    first: string;
    last: string;
    first_last: string;
    email: string;
    phone: string;
    pronouns: string;
    rsvp_status: string;
  
    address_info: string,
  
    dietary: string,
  
    date_link_requested: boolean;
    link: string;
    pair_first_last: string;
  }

interface HeadCell {
    disablePadding: boolean;
    id: keyof Data;
    label: string;
    numeric: boolean;
    width: number;
    smallScreenWidth: number;
}

type Order = 'asc' | 'desc';

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
    if (b[orderBy] < a[orderBy]) return -1;
    if (b[orderBy] > a[orderBy]) return 1;
    return 0;
}
  
function getComparator<Key extends keyof any>(
    order: Order,
    orderBy: Key
): (a: { [key in Key]: any }, b: { [key in Key]: any }) => number {
    return order === 'desc'
        ? (a, b) => descendingComparator(a, b, orderBy)
        : (a, b) => -descendingComparator(a, b, orderBy);
}

const numCols = 7;
const overallWidth = 850;

const headCells: readonly HeadCell[] = [
    {
        id: 'first',
        numeric: false,
        disablePadding: true,
        label: 'First',
        width: overallWidth/numCols,
        smallScreenWidth: 40,
    },
    {
        id: 'last',
        numeric: false,
        disablePadding: true,
        label: 'Last',
        width: overallWidth/numCols,
        smallScreenWidth: 40,
    },
    {
        id: 'phone',
        numeric: false,
        disablePadding: true,
        label: 'Phone',
        width: overallWidth/numCols,
        smallScreenWidth: 40,
    },
    {
        id: 'pair_first_last',
        numeric: false,
        disablePadding: true,
        label: 'Date Pair',
        width: overallWidth/numCols,
        smallScreenWidth: 40,
    },
    {
        id: 'address_info',
        numeric: false,
        disablePadding: true,
        label: 'Address',
        width: overallWidth/numCols,
        smallScreenWidth: 40,
    },
    {
        id: 'dietary',
        numeric: false,
        disablePadding: true,
        label: 'Dietary Info',
        width: overallWidth/numCols,
        smallScreenWidth: 40,
    },
    {
        id: 'email',
        numeric: false,
        disablePadding: true,
        label: 'Email',
        width: overallWidth/numCols,
        smallScreenWidth: 40,
    },
    // more fields also
];

const VirtuosoTableComponents: TableComponents<Data> = {
    Scroller: React.forwardRef<HTMLDivElement>((props, ref) => (
      <TableContainer
        component={Paper}
        ref={ref}
        {...props}
        sx={{ backgroundColor: 'beige', width: 850 }}
      />
    )),
    Table: (props) => (
      <Table
        {...props}
        size="small"
        sx={{ borderCollapse: 'separate', tableLayout: 'fixed', width: 850 }}
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


export default function SortTableRSVPs({ rsvpData }: {rsvpData: Data[]})  {
    
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof Data>('last');
  
    const handleSort = (property: keyof Data) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const sortedRows = React.useMemo(
        () => [...(rsvpData || [])].sort(getComparator(order, orderBy)),
        [rsvpData, order, orderBy]
      );
  
    const fixedHeaderContent = () => (
        <TableRow>
            {headCells.map((column) => (
                <TableCell
                    key={column.id}
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
                    sortDirection={orderBy === column.id ? order : false}
                >
                    <TableSortLabel
                        active={orderBy === column.id}
                        direction={orderBy === column.id ? order : 'asc'}
                        onClick={() => handleSort(column.id)}
                    >
                        {column.label}
                    </TableSortLabel>
                </TableCell>
            )
        )}
      </TableRow>
    );
  
    const rowContent = (index: number, row: Data) => {
        const notComing = row.rsvp_status != 'ATTENDING';
        return (
            <TableRow
                key={row.email}
                sx={{
                    backgroundColor: 'khaki',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    width: "100%",
                    display: "inline-table",
                    opacity: notComing ? 0.5 : 1
                }}
            >
                {headCells.map((column) => (
                    <TableCell
                        key={column.id}
                        align={column.numeric ? 'right' : 'left'}
                        sx={{
                            fontSize: '10px',
                            width: column.width,
                            maxWidth: column.width,
                            minWidth: column.width,
                            textDecoration: notComing ? 'line-through' : 'none'
                        }}
                    >

                        {row[column.id]}

                    </TableCell>
                ))}
            </TableRow>
        );
    };
  
    return (
        <Paper style={{ height: 600, width: 850, margin: '0 auto' }}>
            <TableVirtuoso
                data={sortedRows}
                components={VirtuosoTableComponents}
                fixedHeaderContent={fixedHeaderContent}
                itemContent={(index, item) => rowContent(index, item)}
            />
        </Paper>
    );
}