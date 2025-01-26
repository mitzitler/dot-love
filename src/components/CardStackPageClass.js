import '../App.css';

export function CardStackPageClass({pageMainClass, pageSection, children, pageSecondaryClass, pageTertiaryClass, opacity}) {



    // look into: https://stackoverflow.com/questions/72889068/template-literal-not-working-correctly-with-tailwind-css

    return(
        <>
            <section className={pageMainClass}>
            <div class={pageSection}>     
                <div id="main">    
                    {children}
                </div>
            </div>
            </section>
            <section className={pageSecondaryClass}/>
            <section className={pageTertiaryClass}/>
        </>
    )
}