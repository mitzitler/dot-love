import { useEffect, useState } from "react";
import '../App.css';

export function RegistryPageExternalTitle({Data, displayedId}) {

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
                <h1>
                    Try clicking on the graph!
                </h1>
            </div>
            :
            <div>
                <h1 className="gift title">
                    {giftData.name}
                </h1>
            </div>
            }
        </div> 
    )
}