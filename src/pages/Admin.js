import React, { useState } from "react"
import { useSelector } from 'react-redux';
import { CardStackFooter } from '../components/CardStackFooter';
import { CardStackPage } from '../components/CardStackPage';
import SortTableRSVPs from "./AdminPages/SortTableRSVPs";
import SortTableClaims from "./AdminPages/SortTableClaims";
import { useLazyGetAllUsersQuery } from "../services/gizmo";
import { useLazyGetAllClaimsQuery } from "../services/spectaculo";
import { NavLink } from 'react-router-dom';
import { toast } from 'react-toastify';

function processUsersData(usersArray) {
    if (!Array.isArray(usersArray)) return [];
  
    return usersArray.map(user => {
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
    });
  }

function processClaimsData(claimsArray, registryData) {
    if (!Array.isArray(claimsArray)) return [];

    // Filter out unclaimed items - only show CLAIMED or PURCHASED
    return claimsArray
      .filter(claim => claim.claim_state === "CLAIMED" || claim.claim_state === "PURCHASED")
      .map(claim => {
        const registryItem = registryData.find(function(item) {return item.item_id === claim.item_id});
        return {
          ...claim,
          name: registryItem?.name || 'Unknown',
          img_url: registryItem?.img_url || '',
          price_cents: registryItem?.price_cents || 0,
          received: registryItem?.received || false
        };
      });
  }

export function Admin({ registryItems }) {
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState)
    const [usersData, setUsersData] = useState(null)
    const [claimsData, setClaimsData] = useState(null)
    const [showTableCards, setShowTableCards] = useState(false)
    const [triggerGetAllUsers, {  }] = useLazyGetAllUsersQuery();    
    const [triggerGetAllClaims, {  }] = useLazyGetAllClaimsQuery();


    const pageMainColor = "cyan"
    const pageSecondaryColor = "terracotta"
    const pageTertiaryColor = "plum"
    const pageSection = "admin"

    console.log('registryItems', registryItems)

    const attendingCount = usersData?.filter(user => user.rsvp_status === "ATTENDING").length || 0;

    const handlePassword = async (e) => {
        e.preventDefault();
        const password = e.target.password.value;

        // TODO: this needs to grab the claims list data as well, 
        // and we should join it with registry data being passed in

        // api to receive the password
        try {
            console.log('attempting to get all users, for: ', loginHeaderState)
            console.log('attempting to get claims list as well')

            let resultUsers = null;
            let resultClaims = null;
            let usersError = null;
            let claimsError = null;

            // Try to fetch users
            try {
                resultUsers = await triggerGetAllUsers(password).unwrap();
                console.log("made getAllUsers call to Gizmo, result:", resultUsers);
            } catch (err) {
                usersError = err;
                console.error("Failed to fetch users:", err);
            }

            // Try to fetch claims
            try {
                resultClaims = await triggerGetAllClaims(password).unwrap();
                console.log("made getAllClaims call to Spectaculo, result:", resultClaims);
            } catch (err) {
                claimsError = err;
                console.error("Failed to fetch claims:", err);
            }

            // Handle results
            if (usersError && claimsError) {
                console.log("Both API calls failed");
                toast.error("Failed to load admin data. Please check your password and try again.", {
                    theme: "dark",
                    position: "top-right",
                    autoClose: 5000,
                });
                return;
            } else if (claimsError) {
                console.log("The Gizmo worked, but Spectaculo failed");
                toast.warning("Loaded users data, but failed to load claims data.", {
                    theme: "dark",
                    position: "top-right",
                    autoClose: 5000,
                });
                setUsersData(processUsersData(resultUsers.users))
                setShowTableCards(true)
                return;
            } else if (usersError) {
                console.log("The Spectaculo worked, but Gizmo failed");
                toast.warning("Loaded claims data, but failed to load users data.", {
                    theme: "dark",
                    position: "top-right",
                    autoClose: 5000,
                });
                setClaimsData(processClaimsData(resultClaims.claims, registryItems))
                setShowTableCards(true)
                return;
            } else {
                console.log("Got all users from the Gizmo, and all claims from the Spectaculo");
                toast.success("Admin data loaded successfully!", {
                    theme: "dark",
                    position: "top-right",
                    autoClose: 3000,
                });
                setUsersData(processUsersData(resultUsers.users))
                setClaimsData(processClaimsData(resultClaims.claims, registryItems))
                console.log("claims data format,", claimsData)
                setShowTableCards(true)
                return;
            }
        } catch (err) {
            console.error("Unexpected error in admin data fetch:", err);
            toast.error("An unexpected error occurred. Please try again.", {
                theme: "dark",
                position: "top-right",
                autoClose: 5000,
            });
        }

    }

    // TODO : handle received item id input form

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
                            <div class="m-auto h-[600px] w-[1000px]">
                                <SortTableRSVPs 
                                    rsvpData={usersData}
                                />
                            </div>

                        </div>
                    </CardStackPage>


                    <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                        <div>
                            <h1 class="my-4">Registry claims. Total claimed items: {claimsData?.length || 0}</h1>

                            <div class="flex-col">

                                <div class="m-auto h-[600px] w-[900px]">
                                    {claimsData && claimsData.length > 0 ? (
                                        <SortTableClaims
                                            claimsData={claimsData}
                                        />
                                    ) : (
                                        <p>No claims data available.</p>
                                    )}
                                </div>

                                {/* TODO: Future feature - mark items as received
                                <div class="my-4">
                                    <form class="" onSubmit={handleReceivedClaim}>
                                        <label for="received">submit item id to mark as received: </label>
                                        <input id="received" type="text" name="receivedClaim" value="item id" style={{width: "300px"}} class="w-48 px-2 mx-2"/>
                                        <button type="submit">Submit</button>
                                    </form>
                                </div>
                                */}

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
