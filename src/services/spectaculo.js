import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const spectaculoApi = createApi({
  reducerPath: 'spectaculoApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://api.mitzimatthew.love/spectaculo' }),
  tagTypes: ['RegistryItems', 'UserClaims'],
  endpoints: (builder) => ({
    // Get all registry items
    getRegistryItems: builder.query({
      query: (firstLast) => ({
        url: '/item',
        method: 'GET',
        headers: { 'X-First-Last': firstLast },
      }),
      providesTags: ['RegistryItems'],
    }),

    // Get claims for a specific user
    getUserClaims: builder.query({
      query: (firstLast) => ({
        url: `/claim`,
        method: 'GET',
        headers: { 'X-First-Last': firstLast },
      }),
      providesTags: ['UserClaims'],
    }),

    // Create a claim on a registry item
    createClaim: builder.mutation({
      query: ({ firstLast, claimData }) => ({
        url: '/claim',
        method: 'POST',
        body: claimData,
        headers: { 'X-First-Last': firstLast },
      }),
      // Invalidate the registry items and user claims cache after a claim is created
      invalidatesTags: ['RegistryItems', 'UserClaims']
    }),

    // Update a claim status (claimed/purchased/unclaimed)
    updateClaim: builder.mutation({
      query: ({ firstLast, updateData }) => ({
        url: '/claim',
        method: 'PATCH',
        body: updateData,
        headers: { 'X-First-Last': firstLast },
      }),
    }),

    // Create a payment intent for a gift/donation
    createPayment: builder.mutation({
      query: ({ firstLast, paymentData }) => ({
        url: '/payment/create',
        method: 'POST',
        body: paymentData,
        headers: { 'X-First-Last': firstLast },
      }),
    }),
  }),
});

export const {
  useGetRegistryItemsQuery,
  useGetRegistryItemQuery,
  useGetUserClaimsQuery,
  useCreateClaimMutation,
  useUpdateClaimMutation,
  useCreatePaymentMutation,
} = spectaculoApi;
