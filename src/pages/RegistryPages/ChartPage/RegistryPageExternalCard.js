import { useEffect, useState } from "react";
import { useDispatch, useSelector } from 'react-redux';
import '../../../App.css';

export function RegistryPageExternalCard({ Data, displayedId, children }) {
    const dispatch = useDispatch();
    const [giftData, setGiftData] = useState({})

    useEffect(() => {
        const gift_name = Data.find(gift => gift.item_id === displayedId)
        setGiftData(gift_name)
    }, [displayedId])

    return ( 
        <div>
            {!giftData
            ?
            <div>
                <p className = "font-suse">
                    {children}
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
                        // onClick={()=>dispatch(
                        //     giftClaimedToggle([
                        //         giftData.id, giftData.claimed
                        //     ]))
                        // }>
                        onClick={()=>giftData.claim_state=!!giftData.claim_state}>
                        I'm claiming this!
                    </button>
                </span>
                <div className="relative m-auto grid grid-cols-4" >
                    <div className={!giftData.claim_state ? "col-span-1" : "col-span-1 grayscale"}> 
                        <img className="gift image w-24 h-24 my-4 mx-24 rounded-2xl flex justify-center items-center" 
                            src={giftData.image_url} alt="Image of gift" /> 
                    </div>
                    <div className="col-span-3">
                        <span>
                            <br/>
                            <p className="gift info">
                                {giftData.descr}
                            </p>

                        </span>
                    </div>
                </div>
            </div>
            }
        </div> 
    )
}

