import '../App.css';

export function CardStackFooter({pageMainColor, children, pageSecondaryColor, pageTertiaryColor}) {

    const mainColor = 'bg-' + pageMainColor + '-400/75'
    const mainBorder = 'border-' + pageMainColor + '-500/50'
    
    const secondaryColor = 'bg-' + pageSecondaryColor + '-400/75'
    const secondaryBorder = 'border-' + pageSecondaryColor + '-500/50'

    const tertiaryColor = 'bg-' + pageTertiaryColor + '-400/75'
    const tertiaryBorder = 'border-' + pageTertiaryColor + '-500/50'

    return(
        <>
            <section className={`section-content swipe-card flex-grow ${mainColor} ${mainBorder} border-2 backdrop-blur-md`}>
                <span className='button-container'>
                    {children}
                </span>
            </section>
            <section className={`section-content swipe-card flex-grow ${secondaryColor} ${secondaryBorder} border-2 backdrop-blur-md`}/>
            <section className={`section-content swipe-card flex-grow ${tertiaryColor} ${tertiaryBorder} border-2 backdrop-blur-md`}/>
        </>
    )
}