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

const cdn_fronter = "https://cdn.mitzimatthew.love/"

interface Data {
    item_id: string;
    id: string;
    name: string;
    brand: string;
    price_cents: number;
    price_cat: string;
    claimant_id: string;
    received: boolean;
    img_url: string;
    art_score: number;
    size_score: number;
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
    // col for when it was claimed
    {
        id: 'img_url',
        numeric: false,
        disablePadding: true,
        label: 'Icon',
        width: 60,
        smallScreenWidth: 50,
    },

    {
        id: 'name',
        numeric: false,
        disablePadding: true,
        label: 'Item',
        width: 120,
        smallScreenWidth: 50,
    },
    // col of the claimant's name, after join with users
    {
        id: 'claimant_id',
        numeric: false,
        disablePadding: true,
        label: 'Claimant',
        width: 120,
        smallScreenWidth: 50,
    },
    {
        id: 'brand',
        numeric: false,
        disablePadding: false,
        label: 'Brand',
        width: 100,
        smallScreenWidth: 50,
    },
    {
        id: 'price_cents',
        numeric: true,
        disablePadding: false,
        label: 'Price',
        width: 70,
        smallScreenWidth: 50,
    },
    {
        id: 'price_cat',
        numeric: false,
        disablePadding: false,
        label: 'Bucket',
        width: 90,
        smallScreenWidth: 50,
    },
    {
        id: 'id',
        numeric: false,
        disablePadding: false,
        label: 'Id',
        width: 240,
        smallScreenWidth: 50,
    },
    {
        id: 'received',
        numeric: false,
        disablePadding: false,
        label: 'Received',
        width: 80,
        smallScreenWidth: 50,
    },

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


export default function SortTableClaims({claimsData}: {claimsData: Data[]}) 
    {
    
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof Data>('name');
  
    const handleSort = (property: keyof Data) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };
  
    const sortedRows = React.useMemo(
        () => [...claimsData].sort(getComparator(order, orderBy)),
        [claimsData, order, orderBy]
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
        // const isSelected = row.item_id === displayedId;
        // const isClaimed = row.claim_state === 'CLAIMED';
        return (
            <TableRow
                key={row.item_id}
                // onClick={() => setDisplayedId(row.item_id)}
                sx={{
                    backgroundColor: 'khaki',
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
                        
                        {column.id === 'img_url' ?
                            <div className='w-10 h-10 m-auto' >
                                <img className="gift image" src= {cdn_fronter + row[column.id]}>
                                </img>
                            </div>
                            : column.id === 'claimant_id' ?
                                row[column.id].split('_').join(' ')
                            : column.id === 'received' ?
                                row[column.id] ? 'Yes' : 'No'
                            : column.id === 'price_cents' ?
                                '$' + (row[column.id] / 100).toFixed(2)
                                : row[column.id]
                        }

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