import { useState } from "react";
import SpringModal from '../../components/Modal.js';
import { NewRegistryPageChart } from "./ChartPage/NewRegistryPageChart.tsx";
import { RegistryPageExternalTitle } from "./ChartPage/RegistryPageExternalTitle.js";
import { RegistryPageExternalCard } from "./ChartPage/RegistryPageExternalCard.js";
import { useCreateClaimMutation } from "../../services/spectaculo.js"
import '../../App.css';

// NOTE: LINK TO BUY OBJECTS NEEDS TO CREATE A NEW TAB
// price_cat = ['0-50', '50-100', '100-150', '150+', '??']

// const Data = [
//     { brand: "", has_dollar_value: true, size_score: 1,   function_score: 2,   item_id: 1, name: "Teapot", 
//         descr: "This teapot is so cute, and we are obsessed with the design. For me, a good teapot makesa good home, because a hot beverage can soothe most anxieties.",
//         link: "https://www.williams-sonoma.com/products/mackenzie-childs-checkered-tea-kettle/?catalogId=79&sku=3935686&cm_ven=PLA&cm_cat=Google&cm_pla=Electrics%20%3E%20Tea%20Kettles&cm_ite=3935686_14571727833_aud-868821414659%3Apla-1418851114541&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ699X4nzswtBXyiJ-lf62cQ12ClaoNR-Ag2VClRdE3BnwshAaNVjj-oaArOUEALw_wcB",
//         image_url: require("../assets/temp-registry-photos/teapot.png"),
//         price_cents: 154,
//         price_cat: '150+',
//         last_checked: "2024-09-22",
//         claim_state: true
//     },
//     { brand: "", has_dollar_value: true, size_score: 2,   function_score: 3,   item_id: 2, name: "Toaster",
//         descr: "Its crazy we made it this far without a toaster, but this is such a solid registry item I wanted to hold out. This specific toaster mixed form with function, which is so important given such limited counter space.",
//         link: "https://www.bespokepost.com/store/alessi-plisse-toaster?b=true&a=m_google_performancemax_manual&utm_campaign=Google_PMax_LowMargin&utm_term=170584&nbt=nb%3Aadwords%3Ax%3A18874446669%3A%3A&nb_adtype=pla&nb_kwd=&nb_ti=&nb_mi=101157940&nb_pc=online&nb_pi=170584&nb_ppi=&nb_placement=&nb_li_ms=&nb_lp_ms=&nb_fii=&nb_ap=&nb_mt=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ69HF0J42fjwdQ32iGb07i-8VXUibTlBsbe-9OkBr7pMa0hyIJnh4k8aApCGEALw_wcB",
//         image_url: require("../assets/temp-registry-photos/toaster.png"),
//         price_cents: 125,
//         price_cat: '100-150',
//         last_checked: "2024-09-22",
//         claim_state: false
//      },
//     { brand: "", has_dollar_value: true, size_score: 3,   function_score: 5,   item_id: 3, name: "Towels",
//         descr: "Dusen dusen is an awesome local brand, their workshop located around the corner in East Williamsburg. Pops of color make my seratonin explode (in a good way).",
//         link: "https://www.dusendusen.com/products/house-stripe-towels",
//         image_url: require("../assets/temp-registry-photos/towels.png"),
//         price_cents: 70,
//         price_cat: '50-100',
//         last_checked: "2024-09-22",
//         claim_state: false
//      },
//     { brand: "", has_dollar_value: true, size_score: 5,   function_score: 7,   item_id: 5, name: "Cups",
//         descr: "Its no secret I love pottery, and will try to make anything and everything with ceramics. One thing I cant make with ceramics? Glass cups.",
//         link: "https://mociun.com/products/sophie-lou-jacobsen-ripple-cup?gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ68Vs8TVce2aD5rrPEGtAO8tIllun-lKkrE5LO3n4TPoYQ7U8oGW4CUaAq-7EALw_wcB",
//         image_url:require("../assets/temp-registry-photos/cups.png"),
//         price_cents: 30,
//         price_cat: '0-50',
//         last_checked: "2024-09-22",
//         claim_state: false
//      },
//     { brand: "", has_dollar_value: true, size_score: -10, function_score: 10,  item_id: 6, name: "Flatware",
//         descr: "Every house needs flatware. Even ours!",
//         link: "https://merryandmoon.com/products/set-of-10-pcs-french-style-flatware-bistrot-cutlery-silverware-set-176476605?variant=48971090592059&currency=USD&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6-4CC4nyYlihpT0ZxURzbJZqJAx1hHDEadGYOZf2sMUl1uSYRdIJA8aApweEALw_wcB",
//         image_url: require("../assets/temp-registry-photos/flatware.png"),
//         price_cents: 38,
//         price_cat: '0-50',
//         last_checked: "2024-09-22",
//         claim_state: false
//      },
//     { brand: "", has_dollar_value: true, size_score: 10,  function_score: 10,  item_id: 7, name: "Aperitif",
//         descr: "Everyone needs more non-alcoholic drinks in their life, and we love Ghia's products",
//         link: "https://drinkghia.com/products/le-fizz-to-go-set?variant=44752681664746&currency=USD&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&utm_source=google&utm_medium=paid&utm_campaign=20116792284&utm_content=&utm_term=&gadid=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6-GzR1HG1kZytF-jEf0nC_mmzXYcCWUEPpTG7Fg0GpHigVd7295jCIaArWCEALw_wcB",
//         image_url: require("../assets/temp-registry-photos/aperitif.png"),
//         price_cents: 68,
//         price_cat: '50-100',
//         last_checked: "2024-09-22",
//         claim_state: false
//      },
//     { brand: "", has_dollar_value: true, size_score: -9.5, function_score: -7, item_id: 8, name: "Table Light",
//         descr: "I believe this gooey wabi-sabi style will never go out of style - or at least that it will always make me happy to look at. This Gantri table lamp really exemplifies that.",
//         link: "https://www.gantri.com/products/10181/macaron-table-light-by-romulo-temigue?nbt=nb%3Aadwords%3Ax%3A20217331379%3A%3A&nb_adtype=pla&nb_kwd=&nb_ti=&nb_mi=120308808&nb_pc=online&nb_pi=10181-sm-sunrise&nb_ppi=&nb_placement=&nb_li_ms=&nb_lp_ms=&nb_fii=&nb_ap=&nb_mt=&utm_source=google&utm_medium=paid&utm_campaign=20217331379&utm_content=&utm_term=&gadid=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6832IFGOl4w48EHIaACcg59N1SFFdr0tzA59spG4AFJFNP_wIjJk9saApvMEALw_wcB",
//         image_url: require("../assets/temp-registry-photos/table-lamp.png"),
//         price_cents: 248,
//         price_cat: '150+',
//         last_checked: "2024-09-22",
//         claim_state: false
//      },
//     { brand: "", has_dollar_value: true, size_score: 10,  function_score: -9, item_id: 9, name: "Honeymoon Drink",
//         descr: "Buy us a drink on our honeymoon and we will toast to you!",
//         link: "venmo",
//         image_url: require("../assets/temp-registry-photos/drink.png"),
//         price_cents: 15,
//         price_cat: '??',
//         last_checked: "",
//         claim_state: false
//      },
// ]

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

    const modalLabel = "Help!"
    const modalTitle = "What's going on?"
    const modalText = "We are injecting whimsy into everything we do - yes, even if it means it is initially harder to use. The way our brains work, we like to think of a registry like a graph. On the horizontal, is 'size'. On the vertical, is 'artfullness'. All gifts were thoughtfully picked out and currated - we didn't choose anything that wouldn't fit in our apartment! If you hate this chart display, there is also a table below that you can scroll through. Above all, make sure that you hit 'I'm claiming this!', to claim your item!"

    return ( 
        <div>
            <div className="inline-flex ">
            <h1 className="px-4"> Registry Graph Mode </h1> <SpringModal modalLabel={modalLabel} modalTitle={modalTitle} modalText={modalText} />
            </div>
            {/* <RegistryPageExternalTitle
                Data={registryItems}
                displayedId = {displayedId} 
                setDisplayedId={setDisplayedId} /> */}
            <div className="card place-self-center p-2 border-4 border-double rounded-lg bg-stone-200/50 border-stone-500">
                <NewRegistryPageChart 
                    data={registryItems}
                    displayedId = {displayedId} 
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
                This is a graph measuring function versus size. A small practical item will be totally opposite diagonally to a large piece of art.
                    Please remember to click the popup when you buy an item so that we can remove it from the registry!
                </div>
            </RegistryPageExternalCard>
        </div>
    )
}



