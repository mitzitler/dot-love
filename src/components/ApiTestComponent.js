import React from 'react';
import { usePingQuery, useRegisterUserMutation } from '../services/gizmo';

const ApiTestComponent = () => {
  // Query example: Ping the API
  const { data: pingData, error: pingError, isLoading: isPingLoading } = usePingQuery();

  // Mutation example: Register a user
  const [registerUser, { isLoading: isRegistering, error: registerError }] = useRegisterUserMutation();

  const handleRegister = async () => {
  };


  return (
    <div>
      <h1>Gizmo API Example</h1>
      <div>
        <h2>Ping API</h2>
        {isPingLoading && <p>Loading...</p>}
        {pingError && <p>Error: {pingError.message}</p>}
        {pingData && <p>Code: {pingData["statusCode"]}</p>}
        {pingData && <p>Message: {pingData["message"]}</p>}
      </div>
      {/* <div> */}
      {/*   <h2>Register User</h2> */}
      {/*   <button onClick={handleRegister} disabled={isRegistering}> */}
      {/*     {isRegistering ? 'Registering...' : 'Register User'} */}
      {/*   </button> */}
      {/*   {registerError && <p>Error: {registerError.message}</p>} */}
      {/* </div> */}
    </div>
  );
};

export default ApiTestComponent;
