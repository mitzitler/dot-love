import { useEffect, useState } from "react";
import { useDispatch, useSelector } from 'react-redux';
import useMediaQuery from '@mui/material/useMediaQuery';
import SpringModal from '../../../components/Modal.js';
import { useCreateClaimMutation, useUpdateClaimMutation } from '../../../services/spectaculo.js'
import useRegistryItems from '../../../components/useRegistryItems';
import '../../../App.css';

export function RegistryPageExternalCard({ Data, displayedId, children }) {
    const dispatch = useDispatch();
    const [giftData, setGiftData] = useState({})
    const [createClaim, { isLoadingCreate }] = useCreateClaimMutation();
    const [updateClaim, { isLoadingUpdate }] = useUpdateClaimMutation();

    const cdn_fronter = "https://cdn.mitzimatthew.love/"

    useEffect(() => {
        const gift_name = Data.find(gift => gift.item_id === displayedId)
        console.log(gift_name)
        setGiftData(gift_name)
    }, [displayedId])


    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 

    const handleClaimClick = async (makeApiCall) => {

        // you can unclaim if you are the claimant
        if (giftData.claim_state === 'CLAIMED' && giftData.claimant_id === loginHeaderState.toLowerCase()) {
            console.log('You have claimed this item, so you can release it')

            // dont proceed if loadin
            if (isLoadingCreate || isLoadingUpdate) return;

             // make the API call
            try {
                console.log('attempting to unclaim item, user: ', loginHeaderState)
                const updateData = {'item_id': giftData.item_id, 'claim_state': "UNCLAIMED"};
                const result = await updateClaim({
                    firstLast: loginHeaderState,
                    updateData,
                }).unwrap();

                // the cache invalidation will trigger a refresh of the items

                // to do: response code formatting of spectaculo endpoints differs 
                // from gizmo format - need to console log request to see how to check 
                // errors on code here

                console.log("Patched Claim to the Spectaculo, result:", result);

                // temp update local state to show immediate feedback
                setGiftData({
                    ...giftData,
                    claim_state: 'UNCLAIMED'
                })

            } catch (err) {
                console.error("Patch Claim API call failed:", err);
            }
        }

        // dont let them claim stuff already claimed
        if (giftData.claim_state === 'CLAIMED' && giftData.claimant_id !== loginHeaderState.toLowerCase()) {
            console.log('This item is already claimed by someone else')
            return;
        }

        if (giftData.claim_state === 'UNCLAIMED') {

            // dont proceed if loadin
            if (isLoadingCreate || isLoadingUpdate) return;

            // make the API call
            try {
                console.log('attempting to claim item, user: ', loginHeaderState)
                const claimData = {'item_id': giftData.item_id, 'claimant_id': loginHeaderState};
                const result = await createClaim({
                    firstLast: loginHeaderState,
                    claimData,
                }).unwrap();

                // the cache invalidation will trigger a refresh of the items

                // to do: response code formatting of spectaculo endpoints differs 
                // from gizmo format - need to console log request to see how to check 
                // errors on code here

                console.log("Posted Claim to the Spectaculo, result:", result);

                // temp update local state to show immediate feedback
                setGiftData({
                    ...giftData,
                    claim_state: 'CLAIMED',
                    claimant_id: loginHeaderState.toLowerCase()
                })

            } catch (err) {
                console.error("Post Claim API call failed:", err);
            }
        }
    }


    const isMobile = useMediaQuery('(max-width:480px)');

    return ( 
        <div className="w-[600px] m-auto mt-2 rounded-2xl bg-orange-200/50">
            {!giftData
            ?
            <div>
                <p className = "registry-item-description">
                    {giftData ? giftData.descr : children}
                </p>
            </div>
            :
            <div>

                <span className={giftData.claim_state == 'UNCLAIMED' ? '' : 'grayscale' }>
                    <button className="rounded-lg text-lg pt-1 my-2">
                        <a target="_blank" href={giftData.link} >
                            🪩  🌸  🪐   Buy me for $ {Math.ceil(giftData.price_cents/100)} !   🪐  🌸  🪩
                            {/* the giftData clicks are recorded to the users data */}
                        </a>
                    </button>
                    <span className="rounded-lg text-sm pt-1 my-2"> → </span>
                    <button className="rounded-lg text-lg pt-1 px-2 my-2"
                        onClick={()=>handleClaimClick()}
                        >
                        {giftData.claim_state == 'UNCLAIMED' ? "I'm claiming this!" 
                            :  giftData.claimant_id === loginHeaderState.toLowerCase() ? "You claimed me!" : "This is claimed!"}
                    </button>
                </span>
                <div className="relative m-auto grid grid-cols-4" >
                    <div className={giftData.claim_state == 'UNCLAIMED' ? "col-span-1" : "col-span-1 grayscale"}> 
                        <img className="gift image w-24 h-24 my-4 mx-12 rounded-2xl flex justify-center items-center" 
                            src= {cdn_fronter + giftData.img_url} alt="Image of gift" /> 
                    </div>
                    {/* conditionally render either the description in a block or in a modal */}
                    <div className="col-span-3">
                        {isMobile ? (
                            <SpringModal
                            modalLabel={giftData.name}
                            modalTitle={`${giftData.name} by ${giftData.brand}`}
                            modalText={giftData.descr}
                            />
                        ) : (
                            <span>
                            <h3 className="text-sm">{giftData.name} ⋆ ｡ ° ✩ from <em>{giftData.brand}</em> </h3>
                            <p className="registry-item-description">{giftData.descr}</p>
                            </span>
                        )}
                    </div>

                </div>
            </div>
            }
        </div> 
    )
}

