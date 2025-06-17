import React, { useState } from "react"
import { useSelector } from 'react-redux';
import { CardStackFooter } from '../components/CardStackFooter';
import { CardStackPage } from '../components/CardStackPage';
import SortTableRSVPs from "./AdminPages/SortTableRSVPs";
import { useGetAllUsersQuery } from "../services/gizmo";
import useGetUsers from "../components/useGetUsers";
// import SortTableClaims from "./AdminPages/SortTableClaims";
import { NavLink } from 'react-router-dom';

export function Admin() {
    const [adminPass, setAdminPass] = useState('');
    // const [getAllUsers, { isLoading }] = useGetAllUsersQuery();
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 

    const adminPassAccept = '435o'

    const allUsers = useGetAllUsersQuery(loginHeaderState);

    const pageMainColor = "cyan" 
    const pageSecondaryColor = "terracotta"
    const pageTertiaryColor = "plum"
    
    const pageSection = "admin"


    // const rsvpData = []
    // const claimsData = []
    

    // const usersItems = useGetUsers(true, adminPass)

    // const handlePassword = async (e, makeApiCall) => {
    //     e.preventDefault()
    //     const formData = new FormData(e.target);
    //     const password = formData.get("adminPass");
    //     setAdminPass(password);
    //     let passwordSuccess = false;

    //     if (adminPass == adminPassAccept)
    //         passwordSuccess = true;

    //     if (!makeApiCall || isLoading) return;
    //     try {
    //         const adminPassAccept = '435o'
    //         // api to recieve the password 
    //         // const result = await getAllUsers({
    //         //     headers: password,
    //         // }).unwrap();
    //         const { data: users_data, isSuccess } = useGetAllUsersQuery(password, {
    //             skip: !passwordSuccess, // <- this prevents the query from running until passwordSuccess is true
    //         })

    //         if (result.code !== 200) {
    //             console.log("Something went wrong with Gizmo!", result);
    //             return;
    //         }

    //         if (adminPass == adminPassAccept) {
    //             console.log("Got all users from the Gizmo, result", result);
    //             return;
    //         }

    //         else {
    //             console.error("Something went wrong with Gizmo!", result);
    //             return;
    //         }
    //     } catch (err) {
    //         console.error("Get users API call failed:", err);
    //         return;
    //     }

    // }

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
                                {/* <SortTableRSVPs  */}
                                    {/* rsvpData={rsvpData}  */}
                                {/* /> */}
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

                            {/* input  */}

                        </div>
                    </CardStackPage>
                </>
                :
                <></>
            }
        </>
    )
}