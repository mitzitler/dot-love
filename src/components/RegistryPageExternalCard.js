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
                <p>Humor me - this wedding registry is a <em>chart</em>. On the x axis, you have size, from small to large.
                    On the y axis, we have function - from most practical to most artsy. 
                    A massive mural would be in the top right, a single fork in the bottom left. 
                    </p>
                </div>
            :
            <div>
                <p className="gift title">
                    {giftData.name}
                    </p>
                    <br></br>
                <p className="gift info">
                    {giftData.description}
                    </p>
                {/* <div> 
                     <img className="gift image" href={giftData.image_link} alt="Image of gift" /> 
                    </div> */}
                    <br></br>
                <a href={giftData.link}>Buy me!</a>
                </div>
            }
        </div> 
    )
}



