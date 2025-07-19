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

// interface Address {
//     street: string;
//     second_line: string;
//     city: string;
//     zipcode: string;
//     country: string;
//     state_loc: string;
// }
  
// interface Diet {
//     alcohol: boolean;
//     meat: boolean;
//     dairy: boolean;
//     fish: boolean;
//     shellfish: boolean;
//     eggs: boolean;
//     gluten: boolean;
//     peanuts: boolean;
//     restrictions: string;
// }

// interface GuestDetails {
//     date_link_requested: boolean;
//     link: string;
//     pair_first_last: string;
// }

// export interface Data {
//     first: string;
//     last: string;
//     email: string;
//     phone: string;
//     pronouns: string;
//     rsvp_code: string;
//     rsvp_status: string;

//     address: Address;
//     diet: Diet;
//     guest_details: GuestDetails;
// }

export interface Data {
    // Basic info
    first: string;
    last: string;
    first_last: string;
    email: string;
    phone: string;
    pronouns: string;
    rsvp_code: string;
    rsvp_status: string;
  
    // Address (flattened)
    street: string;
    second_line: string;
    city: string;
    zipcode: string;
    country: string;
    state_loc: string;
  
    // Dietary info (flattened)
    alcohol: boolean;
    meat: boolean;
    dairy: boolean;
    fish: boolean;
    shellfish: boolean;
    eggs: boolean;
    gluten: boolean;
    peanuts: boolean;
    restrictions: string;
  
    // Guest details (flattened)
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

const headCells: readonly HeadCell[] = [
    {
        id: 'first',
        numeric: false,
        disablePadding: true,
        label: 'First',
        width: 50,
        smallScreenWidth: 40,
    },
    {
        id: 'last',
        numeric: false,
        disablePadding: true,
        label: 'Last',
        width: 50,
        smallScreenWidth: 40,
    },
    {
        id: 'pair_first_last',
        numeric: false,
        disablePadding: false,
        label: 'Date Pair',
        width: 50,
        smallScreenWidth: 40,
    },
    {
        id: 'date_link_requested',
        numeric: false,
        disablePadding: false,
        label: 'Date Link Req',
        width: 50,
        smallScreenWidth: 40,
    },
    {
        id: 'phone',
        numeric: false,
        disablePadding: false,
        label: 'Phone',
        width: 50,
        smallScreenWidth: 40,
    },
    {
        id: 'rsvp_status',
        numeric: false,
        disablePadding: false,
        label: 'RSVP',
        width: 50,
        smallScreenWidth: 40,
    },
    {
        id: 'country',
        numeric: false,
        disablePadding: false,
        label: 'Country',
        width: 50,
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


export default function SortTableRSVPs({ rsvpData }: {rsvpData: Data[]})  {
    
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof Data>('last');
  
    const handleSort = (property: keyof Data) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };
  
    const sortedRows = React.useMemo(
        () => [...rsvpData].sort(getComparator(order, orderBy)),
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
                key={row.first_last}
                sx={{
                    backgroundColor: 'khaki',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    opacity: notComing ? 0.7 : 1
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
                        {/* {column.id === 'price' ? `$${row[column.id].toFixed(2)}` : row[column.id]}
                        
                        {column.id === 'name' && isClaimed && (
                            <span style={{ marginLeft: '5px', fontSize: '8px', color: 'green' }}>
                                (Claimed)
                            </span>
                        )} */}

                        row[column.id]

                    </TableCell>
                ))}
            </TableRow>
        );
    };


    console.log("i am a console log from within SortTableRSVPs.tsx")
  
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