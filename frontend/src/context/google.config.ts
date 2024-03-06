
export const googleConfig = {
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    uxMode: 'redirect',
    redirectUri: import.meta.env.VITE_REDIRECT_URI,
    scopes: 'profile email openid',
    prompt: 'select_account',
    responseType: 'token acess_token',
    cookiePolicy: 'single_host_origin'
} as gapi.auth2.ClientConfig;