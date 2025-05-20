import { RegistryClaimCard } from './ClaimPage/RegistryClaimCard'
import '../../App.css';

export function RegistryClaimPage({ claimedItems, registryItems }) {
    
    function leftJoin(leftArray, rightArray, key) {
        const result = [];
      
        leftArray.forEach(leftItem => {
          const rightItem = rightArray.find(right => right[key] === leftItem[key]);
          result.push({ ...leftItem, ...(rightItem || {}) });
        });
      
        return result;
    }

    let claimedItemsLong = leftJoin(claimedItems, registryItems, 'item_id')

    // make an 'unclaim' button component, which goes on these cards

    return (
        <>
            {claimedItemsLong.length == 1 
                ? <h1 className="gift title">Your Claim</h1>
                : <h1 className="gift title">Your Claims</h1>
            }
            <div className="p-4">
                <div className="claim-section"> 
                    {claimedItemsLong.map((claim) => (
                        <RegistryClaimCard 
                            key={claim.item_id} 
                            name={claim.name}
                            brand={claim.brand}
                            descr={claim.descr}
                            img_url={claim.img_url}
                            link={claim.link}
                            updated_at={claim.updated_at}
                            claim_state={claim.claim_state}
                        />
                    ))}
                </div>
            </div>

        </>
    )
}