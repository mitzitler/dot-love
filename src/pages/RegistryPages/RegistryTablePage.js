import { useState } from "react";
import { useCreateClaimMutation } from "../../services/spectaculo.js"
// import { RegistryTableComponent } from "./TablePage/RegistryTableComponent.js";
import ReactVirtualizedTable from "./TablePage/VirtuosoTableComponent";
import SortableVirtualizedTable from "./TablePage/SortVirtualizedTableComponent"
import '../../App.css';
import { RegistryPageExternalCard } from "./ChartPage/RegistryPageExternalCard.js";

export function RegistryTablePage({ registryItems }) {
    // this is the same displayed configuration as the chart, but they are not linked
    const [displayedId, setDisplayedId] = useState()

    const registryItemsMod = registryItems.map(item => {
        const price = item.price_cents / 100;
        return {
          ...item,
          price,
          price_string: `$${price.toFixed(2)}`
        };
      });

    return (
        <>
            <h1 className="gift title">Registry Classic Mode</h1>

            <div className="p-4">

                
                <div className="h-[454px]">
                    <SortableVirtualizedTable 
                        registryItemsMod={registryItemsMod} 
                        displayedId = {displayedId} 
                        setDisplayedId={setDisplayedId}
                        />
                </div>

                <div> 
                    {/* className="h-[175px] my-auto border-2 border-coolGray-500 rounded-md
                font-extralight text-md text-center text-balance align-middle "> */}
                    <RegistryPageExternalCard 
                        displayedId = {displayedId}
                        Data = {registryItemsMod}>
                        <div className = "registry-item-description">
                            Try clicking on the lines in this table to see more detail about the registry items
                            <br/>
                            <br/>
                            And don't forget to claim an item on this site when you are registering for it!
                        </div>
                    </RegistryPageExternalCard>
                </div>

            </div>

        </>
    )
    
}