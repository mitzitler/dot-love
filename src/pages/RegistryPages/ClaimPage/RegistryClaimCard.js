import { useEffect, useState } from "react"

export function RegistryClaimCard({ claim_id, registryItems }) {

    const [claimData, setClaimData] = useState({})

    // useEffect(() => {
    //     const claim_object = registryItems.find(gift => gift.item_id === claim_id)
    //     console.log(claim_object)
    //     setClaimData(claim_object)
    // }, [claim_id])

// key will be claim.id once this is good to go

    return(
        <div key={claim_id} className="w-[600px] m-auto pt-2 rounded-2xl bg-orange-200/50">
            {/* {claimData.item_id} */}
            {claim_id}
        </div>
    )
} 