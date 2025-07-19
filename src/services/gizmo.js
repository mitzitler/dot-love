import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const gizmoApi = createApi({
  reducerPath: 'gizmoApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://api.mitzimatthew.love/gizmo' }),
  endpoints: (builder) => ({
    // Register a new user
    registerRSVP: builder.mutation({
      query: ({headers, rsvpData}) => ({
        url: '/user',
        method: 'POST',
        body: rsvpData,
        headers: headers,
      }),
    }),

    // Health Check
    ping: builder.query({
      query: () => '/ping',
    }),

    // Login a user
    // headers: headers,
    getUser: builder.query({
      query: (headers) => ({
        url: '/user',
        headers: headers,
      }),
    }),

    // Update a user's info
    // headers: headers,
    updateUser: builder.mutation({
      query: (headers, updateData) => ({
        url: '/user',
        method: 'PATCH',
        body: updateData,
        headers: headers,
      }),
    }),

    // Get user by guest link
    getUserByGuestLink: builder.query({
      query: (code) => ({
        url: `/user/guest?code=${code}`,
        method: 'GET',
        headers: { 'X-First-Last': 'plus_one' }
      }),
    }),

    // Get all users
    getAllUsers: builder.query({
      query: (apiKey) => ({
        url: `/user/list`,
        method: 'GET',
        headers: { 'Internal-Api-Key': apiKey },
      }),
    }),

    // Email a user
    emailUser: builder.mutation({
      query: (headers, emailData) => ({
        url: '/email',
        method: 'POST',
        body: emailData,
        headers: headers,
      }),
    }),

    // Text a user
    textUser: builder.mutation({
      query: (headers, textData) => ({
        url: '/text',
        method: 'POST',
        body: textData,
        headers: headers,
      }),
    }),
  }),
});

export const {
  usePingQuery,
  useGetUserQuery,
  useRegisterRSVPMutation,
  useUpdateUserMutation,
  useGetUserByGuestLinkQuery,
  useGetAllUsersQuery,
  useEmailUserMutation,
  useTextUserMutation,
} = gizmoApi;
