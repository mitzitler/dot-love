import React, { useState } from "react"
import { useSelector } from 'react-redux';
import { CardStackFooter } from '../components/CardStackFooter';
import { CardStackPage } from '../components/CardStackPage';
import SortTableRSVPs from "./AdminPages/SortTableRSVPs";
import { useGetAllUsersQuery } from "../services/gizmo";
// import { useGetAllClaimsQuery } from "../services/spectaculo";
import useGetUsers from "../components/useGetUsers";
// import useGetClaims from "../components/useGetClaims";
// import SortTableClaims from "./AdminPages/SortTableClaims";
import { NavLink } from 'react-router-dom';

export function Admin({ registryItems, key }) {
    const [adminPass, setAdminPass] = useState('');
    // const [receivedClaim, setReceivedClaim] = useState('');
    // const [getAllUsers, { isLoading }] = useGetAllUsersQuery(key);
    // const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 

    const adminPassAccept = '435o'

    const allUsers = useGetAllUsersQuery(key);
    // const allClaims = useGetAllClaimsQuery(loginHeaderState);

    const pageMainColor = "cyan" 
    const pageSecondaryColor = "terracotta"
    const pageTertiaryColor = "plum"
    
    const pageSection = "admin"

    console.log('allUsers: ', allUsers)
    const listUsers = allUsers?.data?.body?.users
    console.log('allUsers?.data?.body?.users: ', allUsers?.data?.body?.users)
    // console.log('allClaims: ', allClaims)
    console.log('registryItems: ', registryItems)

    // const handleReceivedClaim = (e) => {
    //     e.preventDefault(); // prevent page reload
    //     const formData = new FormData(e.target);
    //     const claim_item_id = formData.get("receivedClaim"); // assuming input name="adminPass"
    //     setReceivedClaim(claim_item_id);
    // }

    let registryItemsFilter = Object.fromEntries(
        Object.entries(registryItems)
        .filter(([_, value]) => value.claim_state == "CLAIMED"))

    let registryItemsClaimed = Object.entries(registryItemsFilter).map(([key, item]) => ({
        ...item,
        id: key,
        }));

    Object.entries(listUsers)['first_last'] =  Object.entries(listUsers)['first'] + Object.entries(listUsers)['last']

    console.log('registryItemsClaimed: ', registryItemsClaimed)

    // let claimedItemsFilter = Object.fromEntries(
    //     Object.entries(allClaims)
    //         .filter(([_, value]) => value.claim_state == "CLAIMED")
    // )

    // let claimedItemsClaimed = Object.entries(claimedItemsFilter).map(([key, item]) => ({
    //     ...item,
    //     id: key,
    //   }));


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

                <>
                    <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                        <div>
                            <h1>RSVP'd guest info</h1>

                            <div className="h-[454px]">
                                <SortTableRSVPs 
                                    rsvpData={listUsers} 
                                />
                            </div>

                        </div>
                    </CardStackPage>


                    {/* <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                        <div>
                            <h1>Claims info</h1>

                            <div className="flex-col">

                                <div className="m-auto h-[600px] w-[900px]">
                                    <SortTableClaims
                                        // claimsData={claimedItemsClaimed} 
                                        claimsData={registryItemsClaimed}
                                    />
                                </div>

                                <div className="my-4">
                                    <form className="" onSubmit={handleReceivedClaim}>
                                        <label for="received">submit item id to mark as received: </label>
                                        <input id="received" type="text" name="receivedClaim" value="item id" style={{width: "300px"}} className="w-48 px-2 mx-2"/>
                                        <button type="submit">Submit</button>
                                    </form>
                                </div>

                            </div>

                        </div>
                    </CardStackPage> */}
                </>
                {/* :
                <></>
            } */}
        </>
    )
}