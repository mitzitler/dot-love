import React from 'react';
import { useRef, useEffect } from 'react';
import { SwitchTransition, Transition } from 'react-transition-group';
import { useLocation } from 'react-router-dom';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// code from: https://stackblitz.com/edit/react-snrn5k?file=src%2FApp.js,src%2Froutes%2FRouter.js,src%2Fcomponents%2FTransition.js
export function Transitionizer({ children }) {
    const location = useLocation()

    return (
        <SwitchTransition>
            <Transition
                key={location.pathname}
                timeout={500}
                onEnter={(node) => {
                    gsap.set(node, {autoAlpha: 0, scale: 1, yPercent: 100});
                    gsap
                        .timeline({paused: true})
                        .to(node, {autoAlpha: 1, yPercent: 0, duration: 0.6})
                        .to(node, {scale: 1, duration: 0.25})
                        .play()
                }}
                onExit={(node) => {
                    gsap
                        .timeline({paused: true})
                        .to(node, {scale: 1, duration: 0.2})
                        .to(node, {yPercent: 0, autoAlpha: 0, duration: 0.2})
                        .play();
                }}
            >
                {children}
            </Transition>
        </SwitchTransition>
    )
}
