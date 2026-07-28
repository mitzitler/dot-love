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

interface Gift {
    gift: string;
    brand: string;
    price_cents: number | null;
}

interface Data {
    id: string;
    guest: string;
    partner: string;
    gifts: Gift[];
    status: string;
    updated_at: string;
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

const headCells: readonly HeadCell[] = [
    {
        id: 'guest',
        numeric: false,
        disablePadding: true,
        label: 'Guest',
        width: 140,
        smallScreenWidth: 50,
    },
    {
        id: 'partner',
        numeric: false,
        disablePadding: false,
        label: 'Partner',
        width: 140,
        smallScreenWidth: 50,
    },
    {
        id: 'gifts',
        numeric: false,
        disablePadding: false,
        label: 'Gifts',
        width: 220,
        smallScreenWidth: 50,
    },
    {
        id: 'status',
        numeric: false,
        disablePadding: false,
        label: 'Status',
        width: 90,
        smallScreenWidth: 50,
    },
    {
        id: 'updated_at',
        numeric: false,
        disablePadding: false,
        label: 'Updated',
        width: 160,
        smallScreenWidth: 50,
    },
];

const VirtuosoTableComponents: TableComponents<Data> = {
    Scroller: React.forwardRef<HTMLDivElement>((props, ref) => (
      <TableContainer
        component={Paper}
        ref={ref}
        {...props}
        sx={{ backgroundColor: 'beige', width: 750 }}
      />
    )),
    Table: (props) => (
      <Table
        {...props}
        size="small"
        sx={{ borderCollapse: 'separate', tableLayout: 'fixed', width: 750 }}
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

function SortTableLetters(
    { lettersData, selectedLetterId, onSelectLetter }:
    { lettersData: Data[], selectedLetterId?: string, onSelectLetter: (row: Data) => void }
) {

    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof Data>('guest');

    const handleSort = (property: keyof Data) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const sortedRows = React.useMemo(
        () => [...lettersData].sort(getComparator(order, orderBy)),
        [lettersData, order, orderBy]
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
        const isSelected = row.id === selectedLetterId;
        return (
            <TableRow
                key={row.id}
                onClick={() => onSelectLetter(row)}
                sx={{
                    backgroundColor: isSelected ? 'khaki' : 'inherit',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    width: "100%",
                    display: "inline-table"
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
                            minWidth: column.width
                        }}
                    >
                        {column.id === 'gifts'
                            ? row.gifts.map((g) => g.gift).join(', ')
                            : row[column.id]}
                    </TableCell>
                ))}
            </TableRow>
        );
    };

    return (
        <Paper style={{ height: 600, width: 750, margin: '0 auto' }}>
            <TableVirtuoso
                data={sortedRows}
                components={VirtuosoTableComponents}
                fixedHeaderContent={fixedHeaderContent}
                itemContent={(index, item) => rowContent(index, item)}
            />
        </Paper>
    );
}

export default React.memo(SortTableLetters);
