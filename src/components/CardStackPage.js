import '../App.css';

export function CardStackPage({pageMainColor, pageSection, children, pageSecondaryColor, pageTertiaryColor, opacity}) {

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
    // look into: https://stackoverflow.com/questions/72889068/template-literal-not-working-correctly-with-tailwind-css

    return(
        <>
            <section className={`${pageSectionClass} ${pageSectionSwipe} flex-grow ${mainColor} ${mainBorder} border-1 backdrop-blur-md`}>
            <div className={pageSection}>     
                <div id="main">    
                    {children}
                </div>
            </div>
            </section>
            <section className={`${pageSectionClass} ${pageSectionSwipe}  flex-grow ${secondaryColor} ${secondaryBorder} border-1 backdrop-blur-md`}/>
            <section className={`${pageSectionClass} ${pageSectionSwipe}  flex-grow ${tertiaryColor} ${tertiaryBorder} border-1 backdrop-blur-md`}/>
        </>
    )
}