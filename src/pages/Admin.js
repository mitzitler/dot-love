import React, { useState } from "react"
import { useSelector } from 'react-redux';
import { CardStackFooter } from '../components/CardStackFooter';
import { CardStackPage } from '../components/CardStackPage';
import SortTableRSVPs from "./AdminPages/SortTableRSVPs";
import SortTableClaims from "./AdminPages/SortTableClaims";
import { LettersAdmin } from "./AdminPages/LettersAdmin";
import { useLazyGetAllUsersQuery } from "../services/gizmo";
import { useLazyGetAllClaimsQuery } from "../services/spectaculo";
import { useLazyGetAllLettersQuery } from "../services/letters";
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
    const [lettersData, setLettersData] = useState(null)
    const [apiKey, setApiKey] = useState(null)
    const [showTableCards, setShowTableCards] = useState(false)
    const [triggerGetAllUsers, {  }] = useLazyGetAllUsersQuery();
    const [triggerGetAllClaims, {  }] = useLazyGetAllClaimsQuery();
    const [triggerGetAllLetters, {  }] = useLazyGetAllLettersQuery();


    const pageMainColor = "cyan"
    const pageSecondaryColor = "terracotta"
    const pageTertiaryColor = "plum"
    const pageSection = "admin"

    const attendingCount = usersData?.filter(user => user.rsvp_status === "ATTENDING").length || 0;

    const handlePassword = async (e) => {
        e.preventDefault();
        const password = e.target.password.value;
        setApiKey(password);

        const errors = {};

        const [usersOutcome, claimsOutcome, lettersOutcome] = await Promise.allSettled([
            triggerGetAllUsers(password).unwrap(),
            triggerGetAllClaims(password).unwrap(),
            triggerGetAllLetters(password).unwrap(),
        ]);

        let resultUsers = null;
        if (usersOutcome.status === "fulfilled") {
            resultUsers = usersOutcome.value;
        } else {
            errors.users = usersOutcome.reason;
            console.error("Failed to fetch users:", usersOutcome.reason);
        }

        let resultClaims = null;
        if (claimsOutcome.status === "fulfilled") {
            resultClaims = claimsOutcome.value;
        } else {
            errors.claims = claimsOutcome.reason;
            console.error("Failed to fetch claims:", claimsOutcome.reason);
        }

        let resultLetters = null;
        if (lettersOutcome.status === "fulfilled") {
            resultLetters = lettersOutcome.value;
        } else {
            errors.letters = lettersOutcome.reason;
            console.error("Failed to fetch letters:", lettersOutcome.reason);
        }

        if (Object.keys(errors).length === 3) {
            toast.error("Failed to load admin data. Please check your password and try again.", {
                theme: "dark",
                position: "top-right",
                autoClose: 5000,
            });
            return;
        }

        if (resultUsers) setUsersData(processUsersData(resultUsers.users));
        if (resultClaims) setClaimsData(processClaimsData(resultClaims.claims, registryItems));
        if (resultLetters) setLettersData(resultLetters.letters);

        if (Object.keys(errors).length > 0) {
            toast.warning(`Loaded admin data, but failed to load: ${Object.keys(errors).join(', ')}.`, {
                theme: "dark",
                position: "top-right",
                autoClose: 5000,
            });
        } else {
            toast.success("Admin data loaded successfully!", {
                theme: "dark",
                position: "top-right",
                autoClose: 3000,
            });
        }
        setShowTableCards(true)
    }

    // TODO : handle received item id input form

    return (
        <>

            <CardStackFooter pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor}
                pageTertiaryColor={pageTertiaryColor} >
                    <form onSubmit={handlePassword}>
                        <label htmlFor="password">password</label>
                        <input type="password" id="password" name="password" />
                        <button type="submit">Submit</button>
                    </form>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/info' end>INFO</NavLink>
                <NavLink className='bg-warmGray-100 border-red-300 w-24 mx-6' to='/games/militsa' end>GAMES</NavLink>
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

                    <CardStackPage class="card-stack" pageMainColor={pageMainColor} pageSecondaryColor={pageSecondaryColor} pageTertiaryColor={pageTertiaryColor} pageSection={pageSection}>
                        <div>
                            <h1 class="my-4">Thank-you letters. Total letters: {lettersData?.length || 0}</h1>
                            <LettersAdmin
                                letters={lettersData}
                                setLetters={setLettersData}
                                apiKey={apiKey}
                                triggerGetAllLetters={triggerGetAllLetters}
                            />
                        </div>
                    </CardStackPage>
                </>
                :
                <></>
            }
        </>
    )
}
