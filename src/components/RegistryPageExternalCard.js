import { useEffect, useState } from "react";
import { useDispatch, useSelector } from 'react-redux';
import { giftClaimedToggle } from '../features/guest/extrasSlice';
import '../App.css';

export function RegistryPageExternalCard({Data, displayedId}) {
    const dispatch = useDispatch();
    // const giftClaimed = useSelector((state) => state.extras.giftClaimed) 
    const [giftData, setGiftData] = useState({})
    // const [giftClaimed, setGiftClaimed] = useState({})
    // const [giftClaimed, setGiftClaimed] = useState(false)

    useEffect(() => {
        const gift_name = Data.find(gift => gift.item_id === displayedId)
        setGiftData(gift_name)
    }, [displayedId])

    // const handleClaim = () => {
    //     const gift_claimed = giftData.claimed
    //     setGiftClaimed(!gift_claimed)
    // }, [displayedId, giftClaimed])

    return ( 
        <div>
            {!giftData
            ?
            <div>
                <p>
                    This is a graph measuring function versus size. A small practical item will be totally opposite diagonally to a large piece of art.
                    Please remember to click the popup when you buy an item so that we can remove it from the registry!
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

