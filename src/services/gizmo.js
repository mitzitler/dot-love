import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const gizmoApi = createApi({
  reducerPath: 'gizmoApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://api.mitzimatthew.love/gizmo' }),
  endpoints: (builder) => ({
    // Health Check
    ping: builder.query({
      //query: () => '/ping',
      query: () => ({
        url: '/user/guest?code=7z4w',
        method: 'GET',
        headers: {
          "X-First-Last": "mitzi_zitler"
        }
      }),
    }),

    // Login a user
    getUser: builder.query({
    query: (first_last) => ({
          url: '/user',
          method: 'GET',
          headers: {
            "X-First-Last": first_last
          }
      }),
    }),

    // Register a new user
    registerUser: builder.mutation({
      query: (userData, first_last) => ({
        url: '/user',
        method: 'POST',
        body: userData,
        headers: {
          "X-First-Last": first_last
        }
      }),
    }),

    // Update a user's info
    updateUser: builder.mutation({
      query: (updateData, first_last) => ({
        url: '/user',
        method: 'PATCH',
        body: updateData,
        headers: {
          "X-First-Last": first_last
        }
      }),
    }),

    // Get user by guest link
    getUserByGuestLink: builder.query({
      query: (code) => `/user/guest?code=${code}`,
    }),

    // Email a user
    emailUser: builder.mutation({
      query: (emailData, first_last) => ({
        url: '/email',
        method: 'POST',
        body: emailData,
        headers: {
          "X-First-Last": first_last
        }
      }),
    }),

    // Text a user
    textUser: builder.mutation({
      query: (textData, first_last) => ({
        url: '/text',
        method: 'POST',
        body: textData,
        headers: {
          "X-First-Last": first_last
        }
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
