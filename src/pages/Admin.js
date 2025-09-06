import React, { useState } from "react"
import { useSelector } from 'react-redux';
import { CardStackFooter } from '../components/CardStackFooter';
import { CardStackPage } from '../components/CardStackPage';
import SortTableRSVPs from "./AdminPages/SortTableRSVPs";
import { useLazyGetAllUsersQuery } from "../services/gizmo";
import { useLazyGetAllClaimsQuery } from "../services/spectaculo";
import { NavLink } from 'react-router-dom';

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
  
    return claimsArray.map(claim => {
      return {
        ...claim,
        name: registryData.find(function(item) {return item.item_id === claim.item_id}).name,
        img_url: registryData.find(function(item) {return item.item_id === claim.item_id}).img_url,
        price_cents: registryData.find(function(item) {return item.item_id === claim.item_id}).price_cents,
        received: registryData.find(function(item) {return item.item_id === claim.item_id}).received
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
            const resultUsers = await triggerGetAllUsers(password).unwrap();
            const resultClaimsWrapped = await triggerGetAllClaims(password);
            const resultClaims = await triggerGetAllClaims(password).unwrap();
            console.log("made getAllUsers call to Gizmo, result:", resultUsers);
            console.log("made getAllClaims call to Spectaculo, result:", resultClaims)
            
            if (resultUsers.isError && resultClaims.isError) {
                
                console.log("Something went wrong with Gizmo!", resultUsers);
                console.log("Something went wrong with Spectaculo!", resultClaims);
                return;

            } else if (resultClaims.isError) {
                console.log("The Gizmo worked:", resultUsers);
                console.log("Something went wrong with Spectaculo!", resultClaims);
                console.log("Something went wrong with Spectaculo, this is the result before its unwrapped,", resultClaimsWrapped)
                setUsersData(processUsersData(resultUsers.body.users))
                setShowTableCards(true)
                return;
            } else if (resultUsers.isError) {
                console.log("The Spectaculo worked:", resultClaims);
                console.log("Something went wrong with Gizmo!", resultUsers);
                setClaimsData(processClaimsData(resultClaims.claims, registryItems))
                setShowTableCards(true)
                return;
            } else {
                console.log("Got all users from the Gizmo, and all claims from the Spectaculo");
                setUsersData(processUsersData(resultUsers.body.users))
                setClaimsData(processClaimsData(resultClaims.claims, registryItems))
                console.log("claims data format,", claimsData)
                setShowTableCards(true)
                return;
            }
        } catch (err) {
            console.error("Get users API call failed:", err);
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
                            <h1>Claims info</h1>

                            <div class="flex-col">

                                <div class="m-auto h-[600px] w-[900px]">
                                    {/* <SortTableClaims
                                        // claimsData={claimedItemsClaimed} 
                                        claimsData={registryItemsClaimed}
                                    /> */}
                                </div>

                                <div class="my-4">
                                    {/* <form class="" onSubmit={handleReceivedClaim}>
                                        <label for="received">submit item id to mark as received: </label>
                                        <input id="received" type="text" name="receivedClaim" value="item id" style={{width: "300px"}} class="w-48 px-2 mx-2"/>
                                        <button type="submit">Submit</button>
                                    </form> */}
                                </div>

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
