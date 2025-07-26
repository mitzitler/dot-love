import { useEffect, useState } from 'react';
import { useGetAllUsersQuery } from '../services/gizmo.js';

const useGetUsers = (passwordSuccess, loginHeader) => {
  const [users, setUsers] = useState([]);
  
  const { data: users_data, isSuccess } = useGetAllUsersQuery(loginHeader, {
    skip: !passwordSuccess,
  });

  useEffect(() => {
    if (isSuccess && users_data?.users) {
      setUsers(users_data.users);
      console.log('Users API message: ', users_data.message)
    }
  }, [isSuccess, users_data]);

  return users;
};

export default useGetUsers;