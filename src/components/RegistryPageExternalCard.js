import { useEffect, useState } from "react";
import '../App.css';

export function RegistryPageExternalCard({Data, displayedId}) {

    const [giftData, setGiftData] = useState({})

    useEffect(() => {
        console.log(Data.find(gift => gift.id === displayedId))
        const gift_name = Data.find(gift => gift.id === displayedId)
        console.log(gift_name)
        setGiftData(gift_name)
    }, [displayedId])

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
            <div class="relative m-auto grid grid-cols-4" >
                <div class="col-span-1"> 
                     <img className="gift image" href={giftData.image_link} alt="Image of gift" /> 
                </div>
                <div class="col-span-3">
                    <span>
                        <p className="gift info">
                            {giftData.description}
                        </p>
                        <a href={giftData.link}>
                            Buy me!
                            {/* the giftData clicks are recorded to the users data */}
                        </a>
                        {/* checkbox for if you buy it. if you click it it opens a modal */}
                    </span>
                </div>
            </div>
            }
        </div> 
    )
}

