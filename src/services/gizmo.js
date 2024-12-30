import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const gizmoApi = createApi({
  reducerPath: 'gizmoApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/gizmo' }),
  endpoints: (builder) => ({
    // Health Check
    ping: builder.query({
      query: () => '/ping',
    }),

    // Login a user
    getUser: builder.query({
      query: () => '/user',
    }),

    // Register a new user
    registerUser: builder.mutation({
      query: (userData) => ({
        url: '/user',
        method: 'POST',
        body: userData,
      }),
    }),

    // Update a user's info
    updateUser: builder.mutation({
      query: (updateData) => ({
        url: '/user',
        method: 'PATCH',
        body: updateData,
      }),
    }),

    // Get user by guest link
    getUserByGuestLink: builder.query({
      query: (code) => `/user/guest?code=${code}`,
    }),

    // Email a user
    emailUser: builder.mutation({
      query: (emailData) => ({
        url: '/email',
        method: 'POST',
        body: emailData,
      }),
    }),

    // Text a user
    textUser: builder.mutation({
      query: (textData) => ({
        url: '/text',
        method: 'POST',
        body: textData,
      }),
    }),
  }),
});

export const {
  usePingQuery,
  useGetUserQuery,
  useRegisterUserMutation,
  useUpdateUserMutation,
  useGetUserByGuestLinkQuery,
  useEmailUserMutation,
  useTextUserMutation,
} = gizmoApi;
