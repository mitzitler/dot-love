import React, { useState } from "react"
import { useSelector } from 'react-redux';
import { CardStackFooter } from '../components/CardStackFooter';
import { CardStackPage } from '../components/CardStackPage';
import SortTableRSVPs from "./AdminPages/SortTableRSVPs";
import { useLazyGetAllUsersQuery } from "../services/gizmo";
import { NavLink } from 'react-router-dom';

export function Admin({ registryItems }) {
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState)
    const [usersData, setUsersData] = useState(null)
    const [showTableCards, setShowTableCards] = useState(false)
    const [triggerGetAllUsers, { data: userData, isLoading, isError }] = useLazyGetAllUsersQuery();

    const pageMainColor = "cyan"
    const pageSecondaryColor = "terracotta"
    const pageTertiaryColor = "plum"
    const pageSection = "admin"

    const attendingCount = usersData?.filter(user => user.rsvp_status === "ATTENDING").length || 0;

    const handlePassword = async (e) => {
        e.preventDefault();
        console.log(e);
        const password = ""; 

        // TODO: this needs to grab the claims list data as well, 
        // and we should join it with registry data being passed in

        // api to receive the password
        try {
            console.log('attempting to get all users, for: ', loginHeaderState)
            const result = await triggerGetAllUsers(password).unwrap();
            console.log("made getAllUsers call to Gizmo, result:", result);
            if (result.code === 200) {
                console.log("Got all users from the Gizmo");
                
                let resultData = result.body.users
                const processedData = Array.isArray(resultData)
                    ? resultData.map(user => {
                        const diet = user.diet || {};
                        const restrictedItems = [];

                        const dietKeys = [
                            'alcohol', 'dairy', 'eggs', 'fish', 'gluten', 'meat', 'peanuts', 'shellfish'
                        ];

                        dietKeys.forEach(key => {
                            if (diet[key] === false) {
                            restrictedItems.push(key);
                            }
                        });

                        if (diet.restrictions && diet.restrictions.trim() !== '') {
                            restrictedItems.push(diet.restrictions.trim());
                        }

                        return {
                            ...user,
                            first_last: `${user.first} ${user.last}`,
                            pair_first_last: user.guest_details?.pair_first_last ?? '',
                            address_info: `${user.address?.city || ''} ${user.address?.state_loc || ''} ${user.address?.country || ''}`.trim(),
                            phone: user.address?.phone ?? '',
                            dietary: restrictedItems.join(' '),
                        };
                        })
                    : [];

                setUsersData(processedData)
                setShowTableCards(true)
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

            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
                    <form onSubmit={handlePassword}>
                        <label htmlFor="password">password</label>
                        <input type="text" id="password" name="password" />
                        <button type="submit">Submit</button>
                    </form>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/info' end>INFO</NavLink>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/about' end>ABOUT</NavLink>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/registry' end>REGISTRY</NavLink>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/rsvp' end>RSVP</NavLink>
            </CardStackFooter>

            { showTableCards ?
                <>
                    <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                        <div>
                            <h1 class="my-4">RSVP'd guest info. There are {attendingCount} confirmed attending guests.</h1>
                            {console.log("Parent data", usersData)}
                            <div className="m-auto h-[600px] w-[1000px]">
                                <SortTableRSVPs 
                                    rsvpData={usersData}
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
                :
                <></>
            }
        </>
    )
}
