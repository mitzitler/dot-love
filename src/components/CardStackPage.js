import '../App.css';

export function CardStackPage({pageMainColor, pageSection, children}) {

    return(
        <>
            <section className={`section-content swipe-card flex-grow bg-${pageMainColor}-400/75 border-${pageMainColor}-500/50 border-2 backdrop-blur-md`}>
            <div class={pageSection}>     
                <div id="main">    
                    {children}
                </div>
            </div>
            </section>
            <section className={`section-content swipe-card flex-grow bg-${pageMainColor}-400/75 border-${pageMainColor}-500/50 border-2 backdrop-blur-md`}/>
            <section className={`section-content swipe-card flex-grow bg-${pageMainColor}-400/75 border-${pageMainColor}-500/50 border-2 backdrop-blur-md`}/>
        </>
    )
}