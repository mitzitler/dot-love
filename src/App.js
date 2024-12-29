import React, {useRef} from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ScrollSmoother } from 'gsap/ScrollSmoother';
import { GenericHeader } from './components/GenericHeader';
import { Info } from './pages/Info'
import { AboutUs } from './pages/AboutUs'
import { Registry } from './pages/Registry'
import { Data } from './pages/Data'
import { RSVP } from './pages/RSVP'
import { Home } from './pages/Home';
// moved video out because it was 1.3 GB lol
import { LightShow } from './components/LightShowVideo'
import { Routes, Route } from 'react-router-dom';

gsap.registerPlugin(ScrollTrigger, ScrollSmoother )

export default function App() {
  // const main = useRef();

  // ScrollTrigger.normalizeScroll(true)
  
  ScrollSmoother.create({
    smooth: 2,               
    effects: true,          
    smoothTouch: 0.1,        
  });

  gsap.utils.toArray("section").forEach((panel, i) => {
    ScrollTrigger.create({
      trigger: panel,
      start: "top top", 
      pin: true, 
      pinSpacing: false 
    });
  });

  let headerTl = gsap.timeline({
    scrollTrigger: {
      trigger: document.body,
      start: 0,
        end: () => window.innerHeight * 1.2,
        scrub: 0.6
    }
  })
  headerTl.fromTo('.icon', {
    top: '20vw',
    yPercent:-50,
    scale: 5,
  }, {
    top: '2vw',
    yPercent: 0,
    scale: 1,
    duration: 1.2
  }, {
    xPercent: 50,
    duration: 0.8
  })


  return (
    <div id = "root">
      <LightShow/>
      {/* <GenericHeader classname="h-screen transfom-scale-5" /> */}

      {/* <div class="container"> */}
  
        {/* <div class="smooth-wrapper" ref={main}> */}

          {/* <div class="smooth-content"> */}
            <Routes>
              {/* add an all page element here */}
              {/* this will have its own version of generic header, which asks for name instead */}
                <Route path="info" element={<Home/>} /> {/* actually instead, it should be a MainRouter skeleton, which has the generic header and the subroutes for the main pages*/}
                <Route path="rsvp/*" element={<RSVP/>} />
                <Route path="*" element={<Home/>} />
            </Routes>
          {/* </div> */}
        {/* </div> */}

        {/* <div class="footer"></div> */}

      {/* </div> */}

    </div>
  );
}


// to do
// make width width-screen!!
// look into voodoo for swiping
// roll back temp formatting
// redux: design rsvp element
// redux: file structure
// redux: roll back state stuff on every file
// gsap: animate red X on dietary

// later
// flow out rsvp vs normal site
// update graph page
// figure out ACTUAL schedule info
// add copy
// make dietary restrictions more 3d and professional

// zustand
// github pages

// good practice:
// roll stuff yourself