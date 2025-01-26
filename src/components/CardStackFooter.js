import '../App.css';

export function CardStackFooter({pageMainColor, children, pageSecondaryColor, pageTertiaryColor}) {

    return(
        <>
            <section className={`section-content swipe-card flex-grow bg-${pageMainColor}-400/75 border-${pageMainColor}-500/50 border-2 backdrop-blur-md`}>
                <span className='button-container'>
                    {children}
                </span>
            </section>
            <section className={`section-content swipe-card flex-grow bg-${pageSecondaryColor}-400/75 border-${pageSecondaryColor}-500/50 border-2 backdrop-blur-md`}/>
            <section className={`section-content swipe-card flex-grow bg-${pageTertiaryColor}-400/75 border-${pageTertiaryColor}-500/50 border-2 backdrop-blur-md`}/>
        </>
    )
}