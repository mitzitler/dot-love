import '../../styles/Registry.css'

export type InteractionData = {
    xPos: number;
    yPos: number;
    name: string;
    // brand: string;
    price: number
}

type TooltipProps = {
    interactionData: InteractionData | null
}

export const Tooltip = ({ interactionData }: TooltipProps) => {
    if (!interactionData) {
        return null;
    }

    return (
        <div
            className='tooltip'
            style={{
                left: interactionData.xPos+120,
                top: interactionData.yPos+40
            }}
        >
            {interactionData.name}
        </div>
    )
}