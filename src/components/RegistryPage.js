import { useState } from "react";
import { RegistryChartD3 } from "./RegistryPageChart";
import { RegistryPageExternalCard } from "./RegistryPageExternalCard";
import { GenericHeader } from "./GenericHeader";
import '../App.css';

// this is the ultimate source of all data, so the data will be read in on this page
const Data = [
    { x: 1,   y: 2,   id: 1, name: "Teapot", 
        description: "This teapot is so cute, and we are obsessed with the design. For me, a good teapot makesa good home, because a hot beverage can soothe most anxieties.",
        link: "https://www.williams-sonoma.com/products/mackenzie-childs-checkered-tea-kettle/?catalogId=79&sku=3935686&cm_ven=PLA&cm_cat=Google&cm_pla=Electrics%20%3E%20Tea%20Kettles&cm_ite=3935686_14571727833_aud-868821414659%3Apla-1418851114541&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ699X4nzswtBXyiJ-lf62cQ12ClaoNR-Ag2VClRdE3BnwshAaNVjj-oaArOUEALw_wcB",
        image_link: "https://assets.wsimgs.com/wsimgs/ab/images/dp/wcm/202419/0038/img34o.jpg",
        price: 149,
        last_checked: "2024-09-22"
    },
    { x: 2,   y: 3,   id: 2, name: "Toaster",
        description: "Its crazy we made it this far without a toaster, but this is such a solid registry item I wanted to hold out. This specific toaster mixed form with function, which is so important given such limited counter space.",
        link: "https://www.bespokepost.com/store/alessi-plisse-toaster?b=true&a=m_google_performancemax_manual&utm_campaign=Google_PMax_LowMargin&utm_term=170584&nbt=nb%3Aadwords%3Ax%3A18874446669%3A%3A&nb_adtype=pla&nb_kwd=&nb_ti=&nb_mi=101157940&nb_pc=online&nb_pi=170584&nb_ppi=&nb_placement=&nb_li_ms=&nb_lp_ms=&nb_fii=&nb_ap=&nb_mt=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ69HF0J42fjwdQ32iGb07i-8VXUibTlBsbe-9OkBr7pMa0hyIJnh4k8aApCGEALw_wcB",
        image_link: "",
        price: 125,
        last_checked: "2024-09-22"
     },
    { x: 3,   y: 5,   id: 3, name: "Towels",
        description: "Dusen dusen is an awesome local brand, their workshop located around the corner in East Williamsburg. Pops of color make my seratonin explode (in a good way).",
        link: "https://www.dusendusen.com/products/house-stripe-towels",
        image_link: "https://www.dusendusen.com/cdn/shop/files/DD.gif?v=1719871120&width=800",
        price: 168,
        last_checked: "2024-09-22"
     },
    { x: 5,   y: 7,   id: 5, name: "Cups",
        description: "Its no secret I love pottery, and will try to make anything and everything with ceramics. One thing I cant make with ceramics? Glass cups.",
        link: "https://mociun.com/products/sophie-lou-jacobsen-ripple-cup?gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ68Vs8TVce2aD5rrPEGtAO8tIllun-lKkrE5LO3n4TPoYQ7U8oGW4CUaAq-7EALw_wcB",
        image_link: "https://mociun.com/cdn/shop/products/8Xx4MqQAdn7KMcTlI09AICTye8_wGqJEtPBdRPfBDsw.jpg?v=1699715977&width=2000",
        price: 30,
        last_checked: "2024-09-22"
     },
    { x: -10, y: 10,  id: 6, name: "Flatware",
        description: "Every house needs flatware. Even ours!",
        link: "https://merryandmoon.com/products/set-of-10-pcs-french-style-flatware-bistrot-cutlery-silverware-set-176476605?variant=48971090592059&currency=USD&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6-4CC4nyYlihpT0ZxURzbJZqJAx1hHDEadGYOZf2sMUl1uSYRdIJA8aApweEALw_wcB",
        image_link: "https://merryandmoon.com/cdn/shop/files/set-of-10-pcs-french-dopamine-flatware-bistrot-cutlery-silverware-set-399-each-188274.jpg?v=1718240641",
        price: 38,
        last_checked: "2024-09-22"
     },
    { x: 10,  y: 10,  id: 7, name: "Apertif",
        description: "Everyone needs more non-alcoholic drinks in their life, and we love Ghia's products",
        link: "https://drinkghia.com/products/le-fizz-to-go-set?variant=44752681664746&currency=USD&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&utm_source=google&utm_medium=paid&utm_campaign=20116792284&utm_content=&utm_term=&gadid=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6-GzR1HG1kZytF-jEf0nC_mmzXYcCWUEPpTG7Fg0GpHigVd7295jCIaArWCEALw_wcB",
        image_link: "https://drinkghia.com/cdn/shop/files/tumblerset_1200x.jpg?v=1725454718",
        price: 68,
        last_checked: "2024-09-22"
     },
    { x: -9.5, y: -7, id: 8, name: "Table Light",
        description: "I believe this gooey wabi-sabi style will never go out of style - or at least that it will always make me happy to look at. This Gantri table lamp really exemplifies that.",
        link: "https://www.gantri.com/products/10181/macaron-table-light-by-romulo-temigue?nbt=nb%3Aadwords%3Ax%3A20217331379%3A%3A&nb_adtype=pla&nb_kwd=&nb_ti=&nb_mi=120308808&nb_pc=online&nb_pi=10181-sm-sunrise&nb_ppi=&nb_placement=&nb_li_ms=&nb_lp_ms=&nb_fii=&nb_ap=&nb_mt=&utm_source=google&utm_medium=paid&utm_campaign=20217331379&utm_content=&utm_term=&gadid=&gad_source=1&gclid=Cj0KCQjwgL-3BhDnARIsAL6KZ6832IFGOl4w48EHIaACcg59N1SFFdr0tzA59spG4AFJFNP_wIjJk9saApvMEALw_wcB",
        image_link: "https://res.cloudinary.com/gantri/image/upload/ar_1:1,c_lfill,w_640/dpr_2.0/f_auto/v1/dynamic-assets/gantri/products/10181/10181-sm-sunrise/product-photos/product-photos_1724951086119.jpg",
        price: 248,
        last_checked: "2024-09-22"
     },
    { x: 10,  y: -9, id: 9, name: "Honeymoon Drink",
        description: "Buy us a drink on our honeymoon and we will toast to you!",
        link: "venmo",
        image_link: "",
        price: 15,
        last_checked: ""
     },
]

// function RegistryPageChartContainer({displayedId, setDisplayedId}) {

//     return (
//         <div >
//             <div class="card col-span-2 width-500 border-2 static" style = {{position: "static"}}>
//                 <RegistryChartD3 Data={Data}
//                 displayedId = {displayedId} setDisplayedId={setDisplayedId}
//                 />
//             </div>
//             <div class="card col-span-1 width-200 border-2 static">
//                 <h1 class="card-title border-2">This is where we see the description for the gift</h1>
//                 <p class="card-body border-2">
//                     More information, gift id is {displayedId}
//                 </p>
//             </div>
//         </div>
//     )
// }

export function RegistryPage() {
    const [displayedId, setDisplayedId] = useState(null)
    return ( 
        <div>
            <GenericHeader />
            <p>title</p>
            <div class=" relative m-auto grid grid-cols-3 gap-2 border-4">
                <div class="card col-span-2 width-500 border-2 static" style = {{position: "static"}}>
                    <RegistryChartD3 Data={Data}
                        displayedId = {displayedId} 
                        setDisplayedId={setDisplayedId}/>
                </div>
                <RegistryPageExternalCard class="card col-span-1 width-200 border-2 static"
                displayedId = {displayedId}
                Data={Data}  
                />
            </div> 
        </div>
    )
}



