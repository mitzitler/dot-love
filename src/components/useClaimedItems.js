import { useEffect, useState } from 'react';
import { useGetUserClaimsQuery } from '../services/spectaculo.js';

const useClaimedItems = (loginSuccess, loginHeader) => {
  const [claims, setClaims] = useState([]);

  // Only call the API if loginSuccess is true
  const { data: registry_claims, isSuccess } = useGetUserClaimsQuery(loginHeader, {
    skip: !loginSuccess, // <- this prevents the query from running until loginSuccess is true
  });

  // console.log('claims, isSuccess? ', isSuccess)
  // console.log('registry_claims?.claims ?', registry_claims?.claims)

  useEffect(() => {
    if (isSuccess && registry_claims?.claims) {
      setClaims(registry_claims.claims);
      console.log('claims API message: ', registry_claims.message)
    }
  }, [isSuccess, registry_claims]);

  return claims;
};

export default useClaimedItems;