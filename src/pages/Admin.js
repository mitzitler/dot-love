import React, { useState } from "react"
import { useSelector } from 'react-redux';
import { CardStackFooter } from '../components/CardStackFooter';
import { CardStackPage } from '../components/CardStackPage';
import SortTableRSVPs from "./AdminPages/SortTableRSVPs";
import { useGetAllUsersQuery } from "../services/gizmo";
// import useGetAllUsers from "../components/useGetUsers";
import { NavLink } from 'react-router-dom';

export function Admin({ registryItems, key }) {
    const [getAllUsers, { isLoading }] = useGetAllUsersQuery();
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState)
    const [userList, setUserList] = useState(false)

    const pageMainColor = "cyan"
    const pageSecondaryColor = "terracotta"
    const pageTertiaryColor = "plum"
    const pageSection = "admin"

    const handlePassword = async (e) => {
        const formData = new FormData(e.target);
        const password = formData.get("adminPass");

        // api to receive the password
        try {
            console.log('attempting to get all users, for: ', loginHeaderState)
            const result = await getAllUsers(password).unwrap();
            console.log("made getAllUsers call to Gizmo, result:", result);


            if (result.code === 200) {
                console.log("Got all users from the Gizmo, result", result);
                setUserList(result)
                return;
            } else {
                console.log("Something went wrong with Gizmo!", result);
                return;
            }


        } catch (err) {
            console.error("Get users API call failed:", err);
        }

    }

    return (
        <>

            {/* links to all pages */}
            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
              <input onChange={(e)=> handlePassword(e)} ></input>
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
                                    rsvpData={userList}
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
