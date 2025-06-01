import React, { useState } from "react"
import { CardStackFooter } from '../components/CardStackFooter';
import { CardStackPage } from '../components/CardStackPage';
import SortTableRSVPs from "./AdminPages/SortTableRSVPs";
// import SortTableClaims from "./AdminPages/SortTableClaims";
import { NavLink } from 'react-router-dom';

export function Admin() {
    const [adminPass, setAdminPass] = useState('')

    const pageMainColor = "cyan" 
    const pageSecondaryColor = "terracotta"
    const pageTertiaryColor = "plum"
    
    const pageSection = "admin"

    const adminPassAccept = '435o'

    const rsvpData = []
    const claimsData = []

    return (
        <>

            {/* links to all pages */}
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
                <input onChange={(e)=>setAdminPass(e.target.value)} ></input>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/info' end>INFO</NavLink>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/about' end>ABOUT</NavLink>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/registry' end>REGISTRY</NavLink>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/rsvp' end>RSVP</NavLink>
            </CardStackFooter>

            { adminPass == adminPassAccept ?
                <>
                    <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                        <div>
                            <h1>RSVP'd guest info</h1>

                            <div className="h-[454px]">
                                <SortTableRSVPs 
                                    rsvpData={rsvpData} 
                                />
                            </div>

                        </div>
                    </CardStackPage>


                    <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                        <div>
                            <h1>Claims info</h1>

                            <div className="h-[454px]">
                                {/* <SortTableClaims 
                                    claimsData={claimsData} 
                                /> */}
                            </div>

                        </div>
                    </CardStackPage>
                </>
                :
                <></>
            }
        </>
    )
}