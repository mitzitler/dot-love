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

interface Data {
    item_id: number;
    name: string;
    brand: string;
    price: number;
    price_string: string;
    descr: string;
    claim_state: string
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
        id: 'name',
        numeric: false,
        disablePadding: true,
        label: 'Item',
        width: 180,
        smallScreenWidth: 120,
    },
    {
        id: 'brand',
        numeric: false,
        disablePadding: false,
        label: 'Brand',
        width: 150,
        smallScreenWidth: 100,
    },
    {
        id: 'price',
        numeric: true,
        disablePadding: false,
        label: 'Price',
        width: 120,
        smallScreenWidth: 80,
    },
];

const VirtuosoTableComponents: TableComponents<Data> = {
    Scroller: React.forwardRef<HTMLDivElement>((props, ref) => (
      <TableContainer
        component={Paper}
        ref={ref}
        {...props}
        sx={{ backgroundColor: 'beige', width: 450 }}
      />
    )),
    Table: (props) => (
      <Table
        {...props}
        size="small"
        sx={{ borderCollapse: 'separate', tableLayout: 'fixed', width: 450 }}
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


export default function SortableVirtualizedTable({
        registryItemsMod,
        displayedId,
        setDisplayedId,
    }: {
        registryItemsMod: Data[];
        displayedId: number;
        setDisplayedId: (id: number) => void;
    }) 
    {
    
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof Data>('name');
  
    const handleSort = (property: keyof Data) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };
  
    const sortedRows = React.useMemo(
        () => [...registryItemsMod].sort(getComparator(order, orderBy)),
        [registryItemsMod, order, orderBy]
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
        const isSelected = row.item_id === displayedId;
        const isClaimed = row.claim_state === 'CLAIMED';
        return (
            <TableRow
                key={row.item_id}
                onClick={() => setDisplayedId(row.item_id)}
                sx={{
                    backgroundColor: isSelected 
                        ? 'khaki' 
                        : isClaimed 
                            ? 'rgba(211, 211, 211, 0.5)'
                            : 'inherit',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    opacity: isClaimed ? 0.7 : 1
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
                            textDecoration: isClaimed ? 'line-through' : 'none'
                        }}
                    >
                        {column.id === 'price' ? `$${row[column.id].toFixed(2)}` : row[column.id]}
                        
                        {column.id === 'name' && isClaimed && (
                            <span style={{ marginLeft: '5px', fontSize: '8px', color: 'green' }}>
                                (Claimed)
                            </span>
                        )}

                    </TableCell>
                ))}
            </TableRow>
        );
    };
  
    return (
        <Paper style={{ height: 450, width: 450, margin: '0 auto' }}>
            <TableVirtuoso
                data={sortedRows}
                components={VirtuosoTableComponents}
                fixedHeaderContent={fixedHeaderContent}
                itemContent={(index, item) => rowContent(index, item)}
            />
        </Paper>
    );
}