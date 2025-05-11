import { useEffect, useState } from "react";
import { useDispatch, useSelector } from 'react-redux';
import { useCreateClaimMutation } from '../../../services/spectaculo.js'
import '../../../App.css';

export function RegistryPageExternalCard({ Data, displayedId, children }) {
    const dispatch = useDispatch();
    const [giftData, setGiftData] = useState({})
    const [createClaim, { isLoading }] = useCreateClaimMutation();

    useEffect(() => {
        const gift_name = Data.find(gift => gift.item_id === displayedId)
        console.log(gift_name)
        setGiftData(gift_name)
    }, [displayedId])

    console.log('giftData: ', giftData)
    // console.log('loginHeader: ', loginHeader)

    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 
    console.log('loginHeaderState: ', loginHeaderState)

    // const handleClaimClick = async (makeApiCall) => {

    //     // if this is not already claimed, we make a call
    //     if (giftData.claim_state == 'UNCLAIMED'  || isLoading) return;

    //     // Make the API call
    //     try {
    //         const firstLast = loginHeader;
    //         const claimData = giftData.item_id;
    //         const result = await createClaim({
    //             headers: { 'X-First-Last': firstLast },
    //             // NOTE: so we don't run into a
    //             body: claimData,
    //         }).unwrap();

    //         if (result.code !== 200) {
    //             console.error("Something went wrong with Spectaculo!", result);
    //         }

    //         console.log("Posted Claim to the Spectaculo, result:", result);
    //     } catch (err) {
    //         console.error("Post Claim API call failed:", err);
    //     }
    // }


    return ( 
        <div className="w-[600px] m-auto mt-2 rounded-2xl bg-orange-200/50">
            {!giftData
            ?
            <div>
                <p className = "registry-item-description">
                    {!giftData ? children : giftData.descr}
                </p>
            </div>
            :
            <div>

                <span className={!giftData.claim_state ? '' : 'grayscale' }>
                    <button className="rounded-lg text-lg pt-1 my-2">
                        <a href={giftData.link} >
                            🪩  🌸  🪐   Buy me for $ {giftData.price_cents/100.0} !   🪐  🌸  🪩
                            {/* the giftData clicks are recorded to the users data */}
                        </a>
                    </button>
                    <span className="rounded-lg text-sm pt-1 my-2"> → </span>
                    <button className="rounded-lg text-lg pt-1 px-2 my-2"
                        onClick={()=>handleClaimClick()}
                        >
                            {/* if the user is the one who claimed it.. You claimed me! */}
                        {/* {giftData.claim_state == 'UNCLAIMED' ? "I'm claiming this!" :  giftData.claimant_id === loginHeader ? "You claimed me!" : "This is claimed!"} */}
                    </button>
                </span>
                <div className="relative m-auto grid grid-cols-4" >
                    <div className={!giftData.claim_state ? "col-span-1" : "col-span-1 grayscale"}> 
                        <img className="gift image w-24 h-24 my-4 mx-12 rounded-2xl flex justify-center items-center" 
                            src={giftData.image_url} alt="Image of gift" /> 
                    </div>
                    <div className="col-span-3">
                        <span>
                            <h3 className="text-sm">{giftData.name} ⋆  ｡  °  ✩ from <em>{giftData.brand}</em> </h3>
                            {/* <h3 className="text-sm">{giftData.name.toUpperCase()} ⋆  ｡  °  ✩ from <em>{giftData.brand}</em> </h3> */}
                            {/* <br/> */}
                            <p className="registry-item-description">
                                {/* {giftData.descr} */}
                                Sample description for an item. This description is probably several sentences long - it is our pitch for someone to buy the item. 
                            </p>

                        </span>
                    </div>
                </div>
            </div>
            }
        </div> 
    )
}

