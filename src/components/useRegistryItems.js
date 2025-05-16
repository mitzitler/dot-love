import { useEffect, useState } from 'react';
import { useGetRegistryItemsQuery } from '../services/spectaculo.js';

const useRegistryItems = (loginSuccess, loginHeader) => {
  const [items, setItems] = useState([]);
  
  // Only call the API if loginSuccess is true
  const { data: registry_data, isSuccess } = useGetRegistryItemsQuery(loginHeader, {
    skip: !loginSuccess, // <- this prevents the query from running until loginSuccess is true
  });

  useEffect(() => {
    if (isSuccess && registry_data?.items) {
      setItems(registry_data.items);
      console.log('items API message: ', registry_data.message)
    }
  }, [isSuccess, registry_data]);

  return items;
};

export default useRegistryItems;