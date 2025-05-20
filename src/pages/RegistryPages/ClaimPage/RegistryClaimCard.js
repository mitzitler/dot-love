import { useEffect, useState } from "react"
import { useDispatch, useSelector } from 'react-redux';
import useMediaQuery from '@mui/material/useMediaQuery';
import SpringModal from '../../../components/Modal.js';
import { useUpdateClaimMutation } from '../../../services/spectaculo.js'

export function RegistryClaimCard(props) {
    const dispatch = useDispatch();
    const [tempUnclaim, setTempUnclaim] = useState(false)
    const [updateClaim, { isLoading }] = useUpdateClaimMutation();
    const loginHeaderState = useSelector((state) => state.extras.loginHeaderState) 

    console.log(props)

    const handleUnclaimClick = async () => {

        
        if (isLoading || props.claim_state == "UNCLAIMED") return;

            // make the API call
        try {
            console.log('attempting to unclaim item, user: ', loginHeaderState)
            const updateData = {'item_id': props.item_id, 'claim_state': "UNCLAIMED"};
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
            setTempUnclaim(true)

        } catch (err) {
            console.error("Patch Claim API call failed:", err);
            console.error("item_id used:", props.item_id, "claim_state setting:", "UNCLAIMED")
        }
        
    }

    console.log(tempUnclaim)
    
    const cdn_fronter = "https://cdn.mitzimatthew.love/"

    const claim_updated_at = new Date(props.updated_at)
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    const claim_month = monthNames[claim_updated_at.getMonth()]
    let claim_day = claim_updated_at.getDate()
    let day_suffix = ""

    if (claim_day == 1 || claim_day == 21 || claim_day == 31) 
        day_suffix = "st"
    else if (claim_day == 2 || claim_day == 22)
        day_suffix = "nd"
    else if (claim_day == 3 || claim_day == 23)
        day_suffix = "rd"
    else
        day_suffix = "th"
        
    let claim_date = `${claim_month} ${claim_day}${day_suffix}`

    const isMobile = useMediaQuery('(max-width:520px)');
    const isMedium = useMediaQuery('(max-width:570px)');

    return(
        <div key={props.key} className={tempUnclaim ? "grayscale" : ""}>
            <div className="w-[600px] m-auto py-2 my-2 rounded-2xl bg-orange-200/50">
                
                <div className="font-serif text-md mb-2">
                    <span className="text-orange-900">You claimed </span>
                    <span className="text-lg text-orange-700">{props.name}</span>
                    {isMobile ? <></> :
                    <>
                        <span className="text-orange-900"> on </span>
                        <span className="text-lg text-orange-700">{claim_date}!</span>
                    </>
                    }
                </div>

                <div className="relative m-auto grid grid-cols-4 font-suse" >
                    <div className="col-span-3">
                        {isMobile ? <></> :
                        <p className="text-xs">
                            {props.descr.substring(0,120)}... 
                        </p>    
                        }
                        <p className="text-xs text-blue-700 pb-2">
                            (Click the image for the whole description)
                        </p>
                        <span>Changed your mind? </span>
                        {isMedium ? <></> : <span>you can always.... </span>}
                        {!tempUnclaim ?
                            <button
                                className="!text-sm !font-mono font-bold !text-green-800 !border-coolGray-100 border-y-1 p-1 !rounded-md !bg-lilac-300 hover:not-focus:bg-indigo-700"
                                onClick={()=>handleUnclaimClick()}
                                >
                                unclaim it!
                            </button> :
                            <button
                                className="!line-through !text-sm !font-mono font-bold !text-green-800 !border-coolGray-100 border-y-1 p-1 !rounded-md !bg-lilac-300 hover:not-focus:bg-indigo-700"
                                >
                            unclaim it!
                        </button>
                        }
                    </div>
                    <div className="col-span-1">
                    <SpringModal 
                        modalLabel={
                            <img className=
                                {isMobile ? "gift image w-16 h-16 my-2 mr-10 rounded-2xl flex justify-center items-center" :
                                "gift image w-24 h-24 my-4 mr-10 rounded-2xl flex justify-center items-center"}
                            src= {cdn_fronter + props.img_url} alt="Image of gift" />
                            }
                        modalTitle={`${props.name} by ${props.brand}`}
                        modalText={props.descr}
                        modalHelp={false}
                    />
                    </div>
                </div>
            </div>
        </div>
    )
} 