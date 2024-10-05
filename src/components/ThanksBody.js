import React from 'react';
import { useRef, useEffect } from 'react';
import '../App.css';
import { gsap } from "gsap";
import { Flip } from "gsap/Flip";
import { Draggable } from 'gsap/Draggable';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import logo from '../assets/nav_icon_temp_button.png';

// reads from redux guest tier and location

gsap.registerPlugin(Flip, ScrollTrigger, Draggable)

export function ThanksBody() {
    let tempItem = useRef(null)
    useEffect(() => {
        console.log(tempItem)
        Draggable.create(tempItem.current, {
            type: "rotation",
            inertia: false         
        });

        return () => {
            if (tempItem.current) {
                gsap.killTweensOf(tempItem.current);
                Draggable.get(tempItem.current).kill()
            }
        }
        // gsap.to(".box", {
        //     duration: 3,
        //     rotation: 360,
        //     scale: 2,
        //     scrollTrigger: {
        //         trigger: ".box",
        //         markers: true,
        //         scrub: true
        //     }
        // })
    }, [])
    console.log(tempItem)

    return (
        <div 
        // ref={div => (this.content = div)} 
        class="generic-body">
            Hey man thanks for everything We wouldnt be here without the support of our family and friends
            <ul>i am information</ul>
            <ul>more information</ul>
            <img 
            ref={tempItem}
            src={logo} />
        </div>
    )
}

