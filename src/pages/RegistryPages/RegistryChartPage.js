import { useState } from "react";
import * as d3 from "d3"
import SpringModal from '../../components/Modal.js';
import { NewRegistryPageChart } from "./ChartPage/NewRegistryPageChart.tsx";
import { RegistryPageExternalTitle } from "./ChartPage/RegistryPageExternalTitle.js";
import { RegistryPageExternalCard } from "./ChartPage/RegistryPageExternalCard.js";
import { useCreateClaimMutation } from "../../services/spectaculo.js"
import '../../App.css';

export function RegistryChartPage({ registryItems }) {
    const [displayedId, setDisplayedId] = useState()
    const [claimedGift, setClaimedGift] = useState(false)

    //INSTEAD API needs to use 
    // useCreateClaimMutation

    // let loginHeader = 'mitzi_zitler'
    // const registryItems = useRegistryItems(loginSuccess, loginHeader)
    // console.log(registryItems)

    // let Data = []
    // let data_array = []

    // API Call - triggers only when loginHeader changes
    // const { data } = useGetRegistryItemsQuery( loginHeader );

    // data_array = data.items

    // console.log(data_array)

    const PRICE_CAT_DICT = {
        '??' : "#fcba03",
        '$0-75' : "#32a852",
        '$75-150' : "#e052eb",
        '$150-225' : "#5eb4ff",
        '$225-300' : "#8037b8",
        '$300+' : "#e35954",
    };
    
    const PRICE_CAT_ARRAY = Object.keys(PRICE_CAT_DICT);
    
    const colorScale = d3
      .scaleOrdinal()
      .domain(PRICE_CAT_ARRAY)
      .range(PRICE_CAT_ARRAY.map(cat => PRICE_CAT_DICT[cat]));

    const modalLabel = "Help!"
    const modalTitle = "What's going on?"
    const modalText = "We are injecting whimsy into everything we do - yes, even if it means it is initially harder to use. The way our brains work, we like to think of a registry like a graph. On the horizontal, is 'size'. On the vertical, is 'artfullness'. All gifts were thoughtfully picked out and currated - we didn't choose anything that wouldn't fit in our apartment! If you hate this chart display, there is also a table below that you can scroll through. Above all, make sure that you hit 'I'm claiming this!', to claim your item!"

    return ( 
        <div>
            <div className="inline-flex ">
            <h1 className="px-4"> Registry Graph Mode </h1> <SpringModal modalLabel={modalLabel} modalTitle={modalTitle} modalText={modalText} modalHelp={true} />
            </div>
            {/* <RegistryPageExternalTitle
                Data={registryItems}
                displayedId = {displayedId} 
                setDisplayedId={setDisplayedId} /> */}
            <div className="card place-self-center p-2 border-4 border-double rounded-lg bg-stone-200/50 border-stone-500">
                <NewRegistryPageChart 
                    data={registryItems}
                    displayedId = {displayedId} 
                    PRICE_CAT_DICT = {PRICE_CAT_DICT}
                    height={400} width={400}
                    margins={[40, 40, 45, 50]} // clock: top, right, bottom, left
                    setDisplayedId={setDisplayedId}
                    />
            </div>
            <RegistryPageExternalCard className="card col-span-1 static"
                // loginHeader = {loginHeader}
                displayedId = {displayedId}
                Data = {registryItems}  
                // setClaimedGift = {setClaimedGift}
                >
                <div className="registry-item-description">
                This is a graph measuring artfullness versus size. A small practical item will be totally opposite diagonally to a large piece of art.
                    Please remember to click the popup when you buy an item so that we can remove it from the registry!
                </div>
            </RegistryPageExternalCard>
        </div>
    )
}



