import { useState } from "react";
import { NewRegistryPageChart } from "./NewRegistryPageChart";
import { RegistryPageExternalTitle } from "./RegistryPageExternalTitle";
import { RegistryPageExternalCard } from "./RegistryPageExternalCard";
import '../App.css';

// NOTE: LINK TO BUY OBJECTS NEEDS TO CREATE A NEW TAB
// price_cat = ['0-50', '50-100', '100-150', '150+', '??']

const Data = [
    { x: 1,   y: 2,   id: 1, name: "Teapot", 
        description: "This teapot is so cute, and we are obsessed with the design. For me, a good teapot makesa good home, because a hot beverage can soothe most anxieties.",
        link: "https://www.williams-sonoma.com/products/mackenzie-childs-checkered-tea-kettle/?catalogId=79&sku=3935686&cm_ven=PLA&cm_cat=Google&cm_pla=Electrics%20%3E%20Tea%20Kettles&cm_ite=3935686_14571727833_aud-868821414659%3Apla-1418851114541&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ699X4nzswtBXyiJ-lf62cQ12ClaoNR-Ag2VClRdE3BnwshAaNVjj-oaArOUEALw_wcB",
        image_link: require("../assets/temp-registry-photos/teapot.png"),
        price: 154,
        price_cat: '150+',
        last_checked: "2024-09-22",
        claimed: true
    },
    { x: 2,   y: 3,   id: 2, name: "Toaster",
        description: "Its crazy we made it this far without a toaster, but this is such a solid registry item I wanted to hold out. This specific toaster mixed form with function, which is so important given such limited counter space.",
        link: "https://www.bespokepost.com/store/alessi-plisse-toaster?b=true&a=m_google_performancemax_manual&utm_campaign=Google_PMax_LowMargin&utm_term=170584&nbt=nb%3Aadwords%3Ax%3A18874446669%3A%3A&nb_adtype=pla&nb_kwd=&nb_ti=&nb_mi=101157940&nb_pc=online&nb_pi=170584&nb_ppi=&nb_placement=&nb_li_ms=&nb_lp_ms=&nb_fii=&nb_ap=&nb_mt=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ69HF0J42fjwdQ32iGb07i-8VXUibTlBsbe-9OkBr7pMa0hyIJnh4k8aApCGEALw_wcB",
        image_link: require("../assets/temp-registry-photos/toaster.png"),
        price: 125,
        price_cat: '100-150',
        last_checked: "2024-09-22",
        claimed: false
     },
    { x: 3,   y: 5,   id: 3, name: "Towels",
        description: "Dusen dusen is an awesome local brand, their workshop located around the corner in East Williamsburg. Pops of color make my seratonin explode (in a good way).",
        link: "https://www.dusendusen.com/products/house-stripe-towels",
        image_link: require("../assets/temp-registry-photos/towels.png"),
        price: 70,
        price_cat: '50-100',
        last_checked: "2024-09-22",
        claimed: false
     },
    { x: 5,   y: 7,   id: 5, name: "Cups",
        description: "Its no secret I love pottery, and will try to make anything and everything with ceramics. One thing I cant make with ceramics? Glass cups.",
        link: "https://mociun.com/products/sophie-lou-jacobsen-ripple-cup?gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ68Vs8TVce2aD5rrPEGtAO8tIllun-lKkrE5LO3n4TPoYQ7U8oGW4CUaAq-7EALw_wcB",
        image_link:require("../assets/temp-registry-photos/cups.png"),
        price: 30,
        price_cat: '0-50',
        last_checked: "2024-09-22",
        claimed: false
     },
    { x: -10, y: 10,  id: 6, name: "Flatware",
        description: "Every house needs flatware. Even ours!",
        link: "https://merryandmoon.com/products/set-of-10-pcs-french-style-flatware-bistrot-cutlery-silverware-set-176476605?variant=48971090592059&currency=USD&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6-4CC4nyYlihpT0ZxURzbJZqJAx1hHDEadGYOZf2sMUl1uSYRdIJA8aApweEALw_wcB",
        image_link: require("../assets/temp-registry-photos/flatware.png"),
        price: 38,
        price_cat: '0-50',
        last_checked: "2024-09-22",
        claimed: false
     },
    { x: 10,  y: 10,  id: 7, name: "Aperitif",
        description: "Everyone needs more non-alcoholic drinks in their life, and we love Ghia's products",
        link: "https://drinkghia.com/products/le-fizz-to-go-set?variant=44752681664746&currency=USD&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&utm_source=google&utm_medium=paid&utm_campaign=20116792284&utm_content=&utm_term=&gadid=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6-GzR1HG1kZytF-jEf0nC_mmzXYcCWUEPpTG7Fg0GpHigVd7295jCIaArWCEALw_wcB",
        image_link: require("../assets/temp-registry-photos/aperitif.png"),
        price: 68,
        price_cat: '50-100',
        last_checked: "2024-09-22",
        claimed: false
     },
    { x: -9.5, y: -7, id: 8, name: "Table Light",
        description: "I believe this gooey wabi-sabi style will never go out of style - or at least that it will always make me happy to look at. This Gantri table lamp really exemplifies that.",
        link: "https://www.gantri.com/products/10181/macaron-table-light-by-romulo-temigue?nbt=nb%3Aadwords%3Ax%3A20217331379%3A%3A&nb_adtype=pla&nb_kwd=&nb_ti=&nb_mi=120308808&nb_pc=online&nb_pi=10181-sm-sunrise&nb_ppi=&nb_placement=&nb_li_ms=&nb_lp_ms=&nb_fii=&nb_ap=&nb_mt=&utm_source=google&utm_medium=paid&utm_campaign=20217331379&utm_content=&utm_term=&gadid=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6832IFGOl4w48EHIaACcg59N1SFFdr0tzA59spG4AFJFNP_wIjJk9saApvMEALw_wcB",
        image_link: require("../assets/temp-registry-photos/table-lamp.png"),
        price: 248,
        price_cat: '150+',
        last_checked: "2024-09-22",
        claimed: false
     },
    { x: 10,  y: -9, id: 9, name: "Honeymoon Drink",
        description: "Buy us a drink on our honeymoon and we will toast to you!",
        link: "venmo",
        image_link: require("../assets/temp-registry-photos/drink.png"),
        price: 15,
        price_cat: '??',
        last_checked: "",
        claimed: false
     },
]

export function NewRegistryPage() {
    const [displayedId, setDisplayedId] = useState<number | null>()
    const [claimedGift, setClaimedGift] = useState<number | boolean>()
    return ( 
        <div>
            <RegistryPageExternalTitle
                Data={Data}
                displayedId = {displayedId} 
                setDisplayedId={setDisplayedId} />
            <div className="card place-self-center p-2 border-4 border-double rounded-lg bg-stone-200/50 border-stone-500">
                <NewRegistryPageChart 
                    data={Data}
                    displayedId = {displayedId} 
                    height={400} width={400}
                    margins={[40, 40, 45, 50]} // clock: top, right, bottom, left
                    setDisplayedId={setDisplayedId}
                    />
            </div>
            <RegistryPageExternalCard class="card col-span-1 static"
                displayedId = {displayedId}
                Data = {Data}  
                setClaimedGift = {setClaimedGift}
                />
        </div>
    )
}



