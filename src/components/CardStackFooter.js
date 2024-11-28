import '../App.css';

export function CardStackFooter({children}) {

    return(
        <>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute">
                <span className='button-container'>
                    {children}
                </span>
            </section>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
            <section className="section-content swipe-card flex-grow bg-amber-400/75 border-amber-500/50 border-2 backdrop-blur-md position-absolute"/>
        </>
    )
}