import '../App.css';

export function CardStackFooter({pageMainColor, pageSection, children, pageSecondaryColor, pageTertiaryColor}) {

    const mainColor = 'bg-' + pageMainColor + '-400/75'
    const mainBorder = 'border-' + pageMainColor + '-500/50'
    
    const secondaryColor = 'bg-' + pageSecondaryColor + '-400/75'
    const secondaryBorder = 'border-' + pageSecondaryColor + '-500/50'

    const tertiaryColor = 'bg-' + pageTertiaryColor + '-400/75'
    const tertiaryBorder = 'border-' + pageTertiaryColor + '-500/50'

    let pageSectionClass = ''
    let pageSectionSwipe = ''

    if (pageSection === 'rsvp') {
        pageSectionClass = 'rsvp-section-content'
        pageSectionSwipe = 'rsvp-swipe-card'
    } else {
        pageSectionClass = 'section-content'
        pageSectionSwipe = 'swipe-card'
    }

    return(
        <>
            <section className={`${pageSectionClass} ${pageSectionSwipe} flex-grow ${mainColor} ${mainBorder} border-2 backdrop-blur-md`}>
                <span className='button-container'>
                    {children}
                </span>
            </section>
            <section className={`${pageSectionClass} ${pageSectionSwipe} flex-grow ${secondaryColor} ${secondaryBorder} border-2 backdrop-blur-md`}/>
            <section className={`${pageSectionClass} ${pageSectionSwipe} flex-grow ${tertiaryColor} ${tertiaryBorder} border-2 backdrop-blur-md`}/>
        </>
    )
}