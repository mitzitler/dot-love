import { RegistryClaimCard } from './ClaimPage/RegistryClaimCard'
import '../../App.css';

export function RegistryClaimPage({ claimedItems, registryItems }) {
    
    // claim page is v3

    return (
        <>
            <h1 className="gift title">Your Claims</h1>

            <div className="p-4">
                <div className="claim-section"> 
                    {claimedItems.map((claim) => (
                        <RegistryClaimCard key={claim.id} claim_id={claim.id} 
                        // registryItems={registryItems} 
                        />
                    ))}
                </div>
            </div>

        </>
    )
}