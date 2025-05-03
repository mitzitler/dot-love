import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import '../../../App.css';
import { red } from '@mui/material/colors';

export function RegistryTableComponent({ registryItems, displatedId, setDisplayedId}) {


    return (

        // based on basic container example from this sandbox:
        // https://codesandbox.io/embed/s62jdz?module=/src/Demo.tsx&fontsize=12
            <div className="mx-2">
                <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650, backgroundColor: 'beige' }} aria-label="simple table">

                <TableHead>
                    <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell align="right">Brand</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">Last Checked</TableCell>
                    </TableRow>
                </TableHead>

                <TableBody>
                    {registryItems.map((item) => (
                        // IF claim_state == false
                    <TableRow
                        key={item.item_id}
                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                    >
                        {/* Name */}
                        <TableCell component="th" scope="row">
                        {item.name}
                        </TableCell>
                        {/* Brand */}
                        <TableCell align="right">{item.brand}</TableCell>
                        {/* Price */}
                        <TableCell align="right">${item.price_cents / 100.0}</TableCell>
                        {/* Last Checked */}
                        <TableCell align="right">{item.last_checked}</TableCell>
                    </TableRow>
                    ))}
                </TableBody>
                </Table>
            </TableContainer>
        </div>
    )
}