import * as React from 'react';
import {
    Checkbox,
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
import LetterAssigneeToggle, { ASSIGNEE_OPTIONS, Assignee, assigneeOf } from './LetterAssigneeToggle';

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
    address_confirmed: boolean;
    assignee?: string;
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

const STATUS_ROW_COLOR: Record<string, string> = {
    DRAFT: '#dbeafe',
    WRITTEN: '#fed7aa',
    READY_TO_SEND: '#bbf7d0',
    SENT: '#e9d5ff',
};

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
    if (b[orderBy] < a[orderBy]) return -1;
    if (b[orderBy] > a[orderBy]) return 1;
    return 0;
}

// Sort assignees in the order the toggle shows them (Mitzi, Matthew, Either)
// rather than alphabetically.
function assigneeRank(row: Data) {
    return ASSIGNEE_OPTIONS.findIndex((o) => o.value === assigneeOf(row));
}

function getComparator<Key extends keyof any>(
    order: Order,
    orderBy: Key
): (a: { [key in Key]: any }, b: { [key in Key]: any }) => number {
    if (orderBy === 'assignee') {
        const sign = order === 'desc' ? -1 : 1;
        return (a, b) => sign * (assigneeRank(a as Data) - assigneeRank(b as Data));
    }
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
        width: 125,
        smallScreenWidth: 50,
    },
    {
        id: 'partner',
        numeric: false,
        disablePadding: false,
        label: 'Partner',
        width: 105,
        smallScreenWidth: 50,
    },
    {
        id: 'gifts',
        numeric: false,
        disablePadding: false,
        label: 'Gifts',
        width: 150,
        smallScreenWidth: 50,
    },
    {
        id: 'status',
        numeric: false,
        disablePadding: false,
        label: 'Status',
        width: 85,
        smallScreenWidth: 50,
    },
    {
        id: 'address_confirmed',
        numeric: false,
        disablePadding: false,
        label: 'Addr',
        width: 45,
        smallScreenWidth: 50,
    },
    {
        id: 'assignee',
        numeric: false,
        disablePadding: false,
        label: 'For',
        width: 90,
        smallScreenWidth: 50,
    },
    {
        id: 'updated_at',
        numeric: false,
        disablePadding: false,
        label: 'Updated',
        width: 150,
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
    { lettersData, selectedLetterId, onSelectLetter, onToggleAddressConfirmed, onSetAssignee }:
    {
        lettersData: Data[],
        selectedLetterId?: string,
        onSelectLetter: (row: Data) => void,
        onToggleAddressConfirmed: (row: Data) => void,
        onSetAssignee: (row: Data, value: Assignee) => void,
    }
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
                    backgroundColor: STATUS_ROW_COLOR[row.status] || 'inherit',
                    // Row color shows status, so mark selection with an outline
                    boxShadow: isSelected ? 'inset 0 0 0 2px #902E6B' : 'none',
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
                            fontWeight: isSelected ? 'bold' : 'normal',
                            width: column.width,
                            maxWidth: column.width,
                            minWidth: column.width,
                            ...(column.id === 'assignee' ? { paddingX: '4px' } : {}),
                        }}
                    >
                        {column.id === 'gifts' ? (
                            row.gifts.map((g) => g.gift).join(', ')
                        ) : column.id === 'address_confirmed' ? (
                            <Checkbox
                                size="small"
                                sx={{ padding: 0 }}
                                checked={!!row.address_confirmed}
                                // Tick without also selecting the row
                                onClick={(e) => e.stopPropagation()}
                                onChange={() => onToggleAddressConfirmed(row)}
                                inputProps={{ 'aria-label': `Address confirmed for ${row.guest}` }}
                            />
                        ) : column.id === 'assignee' ? (
                            <LetterAssigneeToggle
                                compact
                                value={assigneeOf(row)}
                                guest={row.guest}
                                onChange={(value) => onSetAssignee(row, value)}
                            />
                        ) : (
                            row[column.id]
                        )}
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
